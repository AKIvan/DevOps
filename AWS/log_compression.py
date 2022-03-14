import json
from pathlib import Path
import os
import time
import io
import logging
import boto3
from datetime import datetime, date, timedelta
import io
from io import BytesIO
import gzip


logging.basicConfig(level=logging.INFO)


from io import BytesIO
import gzip
import shutil

s3_bucket = boto3.resource("s3")

def upload_gzipped(bucket, key, fp, compressed_fp=None, content_type='text/plain'):
    """Compress and upload the contents from fp to S3.

    If compressed_fp is None, the compression is performed in memory.
    """
    if not compressed_fp:
        compressed_fp = BytesIO()
    with gzip.GzipFile(fileobj=compressed_fp, mode='wb') as gz:
        shutil.copyfileobj(fp, gz)
    compressed_fp.seek(0)
    bucket.upload_fileobj(
        compressed_fp,
        key,
        {'ContentType': content_type, 'ContentEncoding': 'gzip'})


def merge_files_s3(bucket, obj_list, filename):
    bucket_name = bucket.name
    session = boto3.Session()
    s3_client = session.client("s3")

    for file in obj_list:
        f = BytesIO()
        s3_client.download_fileobj(bucket_name, file["Key"], f)
        f.seek(0)
        upload_gzipped(bucket, filename, f)


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


def lambda_handler(event, context):
    """
    Use the following test variables to test it.

    # bucket_name = ""
    # time_window = 4
    # source = "SOURCE"
    # step="days"
    # directory = ""
    """

    bucket_name = event["BUCKET"]
    directory = event["DIRECTORY"]
    source = event["SOURCE"]
    time_window = int(event["TIME_WINDOW"])
    step = event.get("STEP", "days")
    bucket = s3_bucket.Bucket(bucket_name)

    for date in time_range(time_window, step):
        prefix = get_prefix(date, directory, step)
        files = get_objects(bucket, prefix)
        obj_list = [{"Key": f.key} for f in files if f.key]
        new_obj_list = obj_list[1:]
        files_count = len(obj_list)
        
        if files_count > 1:
            result_prefix = get_result_prefix(date, directory, step)
            filename = f"{source}-{date.year:d}-{date.month:02d}-{date.day:02d}-{date.hour:02d}-concat.gz"
            tmp_filename = f"tmp/{int(time.time())}-concat.parquet"
            try:
                merged_content = merge_files_s3(bucket, obj_list, filename)
                
            except Exception as e:
                logging.error("Error occured: %s", e)
                raise
            else:
                pass
                logging.info("Uncoment me for make it to production")
                # delete_files(bucket, obj_list)
                # move_file(
                #     bucket,
                #     os.path.join(result_prefix, tmp_filename),
                #     os.path.join(result_prefix, filename),
                # )
        else:
            logging.info("No files to merge for date %s", date)


