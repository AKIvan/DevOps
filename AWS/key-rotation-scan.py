import datetime, boto3, os
import urllib3
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

http = urllib3.PoolManager()
IAM = boto3.client('iam')

slack_url = os.environ["SLACKHOOK"]
aws_account_id = os.environ["AWS_Account_ID"]

client = boto3.client("sts")
account_id = client.get_caller_identity()["Account"]


def send_to_slack(encoded_msg: bytes) -> Request:
    request = Request(url, encoded_msg)

    try:
        response = urlopen(request)
        return_status = response.read()
        if return_status == b'ok':
            logger.info("Message posted to Slack")
        else:
            logger.warning(f"Message could not be posted to slack")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
        raise e
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
        raise e
    else:
        return return_status

def time_diff(keycreatedtime):
    # Getting the current time in utc format
    now = datetime.datetime.now(datetime.timezone.utc)
    # Calculating diff between two datetime objects.
    diff = now - keycreatedtime
    # Returning the difference in days
    return diff.days


def access_key(user):
    """List the access key(s) of every user. Then iterate over the keys and pass the created date to time_diff()
    CreateDate of Access Key is a datetime object. Passing it as an input to time_diff func to get the age in days.
       Parameters: user (string) : Username of IAM user
    """
    keydetails = IAM.list_access_keys(UserName=user)
    # Some user may have 2 access keys. So iterating over them and listing the details of active access key.
    for keys in keydetails['AccessKeyMetadata']:
        if keys['Status'] == 'Active' and (time_diff(keys['CreateDate'])) >= 90:
            # print(keys['UserName'], keys['AccessKeyId'], time_diff(keys['CreateDate']), sep=',')
            payload = {"text": f"User *{keys['UserName']}* in has not rotated access key in over 90 days! -- Create Date: {time_diff(keys['CreateDate'])}"}
            encoded_msg = json.dumps(payload).encode('utf-8')
            send_to_slack(encoded_msg)

def lambda_handler(event, context):
    # This returns a dictionary response
    details = IAM.list_users(MaxItems=300)
    for user in details['Users']:
        access_key(user['UserName'])
