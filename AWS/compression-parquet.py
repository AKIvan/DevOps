from datetime import datetime, date, timedelta
import io
import json
import logging
import os
import time
from unittest.mock import patch
from urllib.parse import urlparse

import boto3
import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO)


def time_range(time_back, step="days", include_current=False):
    """ Provides a datetime generator from some time in the past untill current date

    :param time_back: a lenght of time period
    :param step: time unit e.g hours, days
    :param include_current: Include current time or not
    :return: time series generator
    """

    stop_date = datetime.now()
    current_date = stop_date - timedelta(**{step: time_back})
    delta = timedelta(**{step: 1})

    if include_current:
        stop_date += delta

    while current_date < stop_date:
        yield current_date
        current_date += delta


def get_objects(bucket, prefix):
    """ Retrieves objects from s3 bucket with given prefix

    :param bucket: s3 bucket object
    :param prefix: file prefix
    :returns: List of objects
    """
    files = bucket.objects.filter(Prefix=prefix)

    logging.info(
        f"Files found in %s at %s: %s",
        bucket.name,
        prefix,
        ", ".join([f.key for f in files]),
    )
    return files


def merge_files(bucket, files):
    """ Merge multiple parquet files from s3 into one

    :param bucket: s3 bucket object
    :param files: list of dict containaining file keys
    :returns: merged parquet file content
    """
    merged_content = None
    rows_count = 0
    for obj in files:
        logging.info(f"Load file {obj['Key']}")
        content = io.BytesIO()
        bucket.download_fileobj(obj["Key"], content)
        content.seek(0)
        parquet_table = pq.read_table(content)
        rows_count += parquet_table.num_rows
        merged_content = (
            parquet_table
            if merged_content is None
            else pa.concat_tables([merged_content, parquet_table])
        )

    assert (
        merged_content.num_rows == rows_count
    ), f"Resulting data row count doesn't match {merged_content.num_rows} != {rows_count}"

    merged_object_file = io.BytesIO()
    pq.write_table(merged_content, merged_object_file)
    merged_object_file.seek(0)
    return merged_object_file


def upload_parquet_file(bucket, key, content):
    """ uploads parquet file into s3 bucket

    :param bucket: s3 bucket object
    :param key: new file key
    :param content: file-like object containing file content
    """

    logging.info(f"Upload file {key} into {bucket.name}")
    bucket.upload_fileobj(content, key)


def delete_files(bucket, keys_list):
    """ delete multiple files from s3 bucket

    :param bucket: s3 bucket object
    :param keys_list: list of files keys
    """

    logging.info("Delete files: %s", keys_list)
    while keys_list:
        # delete_objects allows to delete at most 1000 files. We're using half this amount.
        chunk, keys_list = (
            keys_list[:500],
            keys_list[500:],
        )
        bucket.delete_objects(Delete={"Objects": chunk, "Quiet": True})


def move_file(bucket, source, destination):
    """ copy file to final destination and remove original

    :param bucket: s3 bucket object
    :param source: source file key
    :param destination: destination file key
    """

    bucket.copy({"Bucket": bucket.name, "Key": source}, destination)
    bucket.delete_objects(Delete={"Objects": [{"Key": source}], "Quiet": True})


def get_prefix(date, directory, step="days"):
    """ Returns file prefix

    :param date: date
    :param directory: main directory
    :param step: time unit e.g hours, days
    :returns: prepared prefix
    """
    mapping = {
        "hours": "{date.year:d}/{date.month:02d}/{date.day:02d}/{date.hour:02d}/",
        "days": "{date.year:d}/{date.month:02d}/{date.day:02d}/",
    }

    return os.path.join(directory, mapping[step].format(date=date))


def get_result_prefix(date, directory, step="days"):
    """ Returns file prefix

    :param date: date
    :param directory: main directory
    :param step: time unit e.g hours, days
    :returns: prepared prefix
    """

    mapping = {
        "hours": "{date.year:d}/{date.month:02d}/{date.day:02d}/{date.hour:02d}/",
        "days": "{date.year:d}/{date.month:02d}/{date.day:02d}/00/",
    }

    return os.path.join(directory, mapping[step].format(date=date))


def lambda_handler(event, context):
    """ Main lambda handler function

    :param event: event data
    :param context: additional context
    """
    bucket_name = event["BUCKET"]
    directory = event["DIRECTORY"]
    source = event["SOURCE"]
    time_window = int(event["TIME_WINDOW"])
    step = event.get("STEP", "days")

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    for date in time_range(time_window, step):
        prefix = get_prefix(date, directory, step)
        files = get_objects(bucket, prefix)
        obj_list = [{"Key": f.key} for f in files if f.key.endswith(".parquet")]
        files_count = len(obj_list)
        if files_count > 1:

            result_prefix = get_result_prefix(date, directory, step)
            filename = f"{source}-{date.year:d}-{date.month:02d}-{date.day:02d}-{date.hour:02d}-concat.parquet"
            tmp_filename = f"tmp/{int(time.time())}-concat.parquet"

            try:
                merged_content = merge_files(bucket, obj_list)
                upload_parquet_file(
                    bucket, os.path.join(result_prefix, tmp_filename), merged_content
                )
            except Exception as e:
                logging.error("Error occured: %s", e)
                raise
            else:
                delete_files(bucket, obj_list)
                move_file(
                    bucket,
                    os.path.join(result_prefix, tmp_filename),
                    os.path.join(result_prefix, filename),
                )
        else:
            logging.info("No files to merge for date %s", date)
