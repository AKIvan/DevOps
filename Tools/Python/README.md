# EC2 Spot Instance Cost-Effectiveness Calculator

## Overview

The **EC2 Spot Instance Cost-Effectiveness Calculator** is a Python tool that helps you find the most cost-effective AWS EC2 Spot Instances based on their CPU and memory specifications. By comparing the number of CPUs and memory size against the current spot prices, this tool ranks instances to help you save money on your cloud resources.

## Features

- **Retrieve Spot Prices:** Gets the latest spot prices for selected EC2 instance types.
- **Collect Specifications:** Gathers information on the number of vCPUs and memory size for each instance.
- **Cost-Effectiveness Metric:** Calculates a score to determine which instances offer the best value.
- **Flexible Input:** Choose to input instance types directly or via a JSON file.
- **Formatted Output:** Displays a neat table ranking instances based on cost-effectiveness.

## Prerequisites

- **Python 3.8 or higher**
- **AWS Account:** Ensure you have AWS credentials with permissions to access EC2 services.

## Setup

### 1. Set Up AWS Credentials

```
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=your_preferred_region
```

### 2.  Install Dependencies

It's recommended to use a virtual environment to manage dependencies.

```
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Usage

You can run the script in two ways: by specifying instance types directly via command-line arguments or by providing a JSON file with the instance types.

### 1. Using Command-Line Arguments
Provide the AWS region and a list of EC2 instance types directly in the command.

```
python PyDevOps.py --region <AWS_REGION> --instance-types <INSTANCE_TYPE_1> <INSTANCE_TYPE_2> ...
```

Example:
```
python PyDevOps.py --region us-west-2 --instance-types t2.micro t3.small m5.large
```

### 2. Using a JSON File
Provide a JSON file that contains a list of EC2 instance types.

Create a file named instances.json with the following content:

```
[
  "t2.micro",
  "t3.small",
  "m5.large"
]
```

Execyte the script:
```
python PyDevOps.py --region <AWS_REGION> --instance-file <PATH_TO_JSON_FILE>
```

Example:
```
python PyDevOps.py --region us-west-2 --instance-file instances.json
```

## Expected Output

```
InstanceType    vCPUs Memory (GiB) SpotPrice  CostEffectiveness 
-----------------------------------------------------------------
t2.micro            1         1.00     0.0022             909.09
t3.small            2         2.00     0.0080              500.0
m5.large            2         8.00     0.0316             316.46
```


