# DevOps Tools and services


## LAMBDA FUNCTIONS

### Log Compression function

The `compression-*.py` is a lambda functions that should be executed as Batch job in order to make a merging/compression of the logs stored in a given S3 bucket. 

With this kind of functionallity we can reduce the cost of the logs tremendously. For example if we have 5GB of regular logs, we can merge everything into one file and change the compression algoritham to be gz, parquet and we will have one file of logs with size around 1GB instead of 5GB. With this we can still search/query through the logs using this 1GB of file. 

After everything is done with the merging part, and the file is created, the old logs will be deleted. 


### The process of execution
The script take some arguments like:

1. Bucket Name
2. Directory - is a full path starting from the bucket name to the "date" directory of the logs
3. Source is used for moving the merged files 
4. Steps - time unit e.g hours, days
5. time_window - a lenght of time period (0 current day, 1 day, 2 days)


### Way of execution
The script can be executed as Batch Job and trigger using Cron/aws scheduler and send the parameters via JSON. 


## Security Analysis

The `key-rotation-scan.py` can scan all the user in the give account and check if the key need to be rotate/renew. It also have option to send message to slack. 
