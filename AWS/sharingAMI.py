from sys import argv

import boto3

TARGET_ACCOUNT_ID = '<ACCOUNT ID>'
ROLE_ON_TARGET_ACCOUNT = 'arn:aws:iam::<ACCOUNT ID>:role/<ROLENAME>'
SOURCE_REGION = 'us-east-1'
TARGET_REGION = 'us-east-1'


def role_arn_to_session(**args):
    """
    Lets you assume a role and returns a session ready to use
    Usage :
        session = role_arn_to_session(
            RoleArn='arn:aws:iam::012345678901:role/example-role',
            RoleSessionName='ExampleSessionName')
        client = session.client('sqs')
    """
    client = boto3.client('sts')
    response = client.assume_role(**args)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])


if len(argv) != 2:
    print('usage: share-ami.py [ami]')
    exit(1)

source_ec2 = boto3.resource('ec2')
source_ami = source_ec2.Image(argv[1])

source_snapshot = source_ec2.Snapshot(source_ami.block_device_mappings[0]['Ebs']['SnapshotId'])

# Ensure the snapshot is shared with target account
source_sharing = source_snapshot.describe_attribute(Attribute='createVolumePermission')
if source_sharing['CreateVolumePermissions'] \
        and source_sharing['CreateVolumePermissions'][0]['UserId'] != TARGET_ACCOUNT_ID:
    print("Snapshot already shared with account, creating a copy")
else:
    print("Sharing with target account")
    source_snapshot.modify_attribute(
        Attribute='createVolumePermission',
        OperationType='add',
        UserIds=[TARGET_ACCOUNT_ID]
    )

# Get session with target account
target_session = role_arn_to_session(
    RoleArn=ROLE_ON_TARGET_ACCOUNT,
    RoleSessionName='share-admin-temp-session'
)
target_ec2 = target_session.resource('ec2', region_name=TARGET_REGION)

# A shared snapshot, owned by source account
shared_snapshot = target_ec2.Snapshot(source_ami.block_device_mappings[0]['Ebs']['SnapshotId'])

# Ensure source snapshot is completed, cannot be copied otherwise
if shared_snapshot.state != "completed":
    print("Shared snapshot not in completed state, got: " + shared_snapshot.state)
    exit(1)

# Create a copy of the shared snapshot on the target account
copy = shared_snapshot.copy(
    SourceRegion=SOURCE_REGION,
    Encrypted=True,
)

# Wait for the copy to complete
copied_snapshot = target_ec2.Snapshot(copy['SnapshotId'])
copied_snapshot.wait_until_completed()

print("Created target-owned copy of shared snapshot with id: " + copy['SnapshotId'])

# Optional: tag the created snapshot
# copied_snapshot.create_tags(
#     Tags=[
#         {
#             'Key': 'cost_centre',
#             'Value': 'project abc',
#         },
#     ]
# )

# Create an AMI from the snapshot.
# Modify the below if your configuration differs
new_image = target_ec2.register_image(
    Name='copy-' + copied_snapshot.snapshot_id,
    Architecture='x86_64',
    RootDeviceName='/dev/sda1',
    BlockDeviceMappings=[
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "SnapshotId": copied_snapshot.snapshot_id,
                "VolumeSize": copied_snapshot.volume_size,
                "DeleteOnTermination": True,
                "VolumeType": "gp2"
            },
        }
    ],
    VirtualizationType='hvm'
)

print("New AMI created ")

# Optional: tag the created AMI
# new_image.create_tags(
#     Tags=[
#         {
#             'Key': 'cost_centre',
#             'Value': 'project abc',
#         },
#     ]
# )

# Optional: Remove old snapshot and image
# source_ami.deregister()
# source_snapshot.delete()