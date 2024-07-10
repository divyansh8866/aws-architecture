# S3-Table-Monitoring-and-Alert-System
Developer : `divyansh patel`
## Overview


The S3-Table-Monitoring-and-Alert-System is designed to monitor specific S3 buckets for any new files. If no new files are detected within a defined time period, the system will send a notification through SNS (Simple Notification Service). This ensures that data ingestion or file updates in your S3 buckets are monitored, and any disruptions are promptly alerted.

## Architecture

The system is composed of the following AWS components:

1. **Amazon S3 Buckets**: These buckets hold the data tables that need to be monitored.
2. **AWS Lambda Function**: This function is triggered daily to check for new files in the specified S3 buckets. If no new files are found within the specified time frame (24 hours), it raises a warning or error.
3. **Amazon SNS**: SNS is used to send email notifications if no new files are detected.
4. **Daily CRON**: A scheduled event that triggers the Lambda function daily.

### Diagram

![Alt text](doc/diagram.png)

## Components

### Amazon S3
Three S3 buckets (S3-table #1, S3-table #2, S3-table #3) are monitored for new file uploads.

### AWS Lambda
- **Function Name**: `monitor`
- **Trigger**: Scheduled daily CRON job
- **Environment Variables**:
  - `TOPIC_ARN`: The ARN of the SNS topic to send notifications.

### Amazon SNS
- **Topic Name**: `S3TableMonitoringNotifications`
- **Usage**: Sends email notifications to alert when no new files are detected within the 24-hour time frame.

### Daily CRON
- **Schedule**: `cron(0 0 * * ? *)` - Runs daily at midnight UTC.


## How It Works

1. **File Monitoring**: The Lambda function runs daily, checking the specified S3 buckets for new files.
2. **Alert Trigger**: If no new files are detected within the last 24 hours, the Lambda function sends a warning or error message to the SNS topic.
3. **Notification**: SNS sends an email notification to the subscribed users, alerting them of the issue.

## Understanding the `monitor.json` File

The `monitor.json` file is a crucial component of the S3-Table-Monitoring-and-Alert-System. It serves as a metadata configuration file for the AWS Lambda function, defining which S3 buckets and specific folders (prefixes) need to be monitored and the time intervals for checking new data. Here's a detailed explanation of its structure and how to make changes to it.

### Structure of `monitor.json`

The `monitor.json` file is a JSON object that contains keys representing the S3 buckets to be monitored. Each bucket key maps to an array of objects, where each object specifies a prefix (folder path) within the bucket and the `timedelta_days` indicating the period within which new files are expected.

Here is a sample structure:

```json
{
    "bucket_1": [
        {
            "prefix": "db1/folder/",
            "timedelta_days": 1
        },
        {
            "prefix": "db1/folder_2/",
            "timedelta_days": 1
        }
    ],
    "bucket_2":[
        {
            "prefix": "db2/folder1/",
            "timedelta_days": 1
        }
    ]
}
```

### Explanation of Fields

- **Bucket Name (`bucket_1`, `bucket_2`)**: These are the names of the S3 buckets that the Lambda function will monitor.
- **Prefix**: The `prefix` field specifies the folder path within the S3 bucket that needs to be monitored. For example, `db1/folder/` refers to a specific directory within `bucket_1`.
- **Timedelta Days (`timedelta_days`)**: This field indicates the number of days within which new files are expected. If no new files are detected within this time frame, the system will raise an alert.

### Making Changes to `monitor.json`

To update the `monitor.json` file, you can follow these steps:

1. **Adding a New Bucket**:
   - To monitor a new S3 bucket, add a new key-value pair to the JSON object, where the key is the name of the new bucket, and the value is an array of objects specifying the prefixes and `timedelta_days`.

   ```json
   "bucket_3": [
       {
           "prefix": "db3/new_folder/",
           "timedelta_days": 1
       }
   ]
   ```

2. **Adding a New Prefix to an Existing Bucket**:
   - To add a new prefix to an existing bucket, simply add a new object to the array corresponding to that bucket.

   ```json
   "bucket_1": [
       {
           "prefix": "db1/folder/",
           "timedelta_days": 1
       },
       {
           "prefix": "db1/folder_2/",
           "timedelta_days": 1
       },
       {
           "prefix": "db1/new_folder/",
           "timedelta_days": 1
       }
   ]
   ```

3. **Changing the Time Interval**:
   - To change the time interval for checking new files, modify the value of the `timedelta_days` field for the respective prefix.

   ```json
   {
       "prefix": "db1/folder/",
       "timedelta_days": 2
   }
   ```

4. **Removing a Prefix or Bucket**:
   - To remove a prefix, delete the corresponding object from the array.
   - To remove an entire bucket, delete the key-value pair from the JSON object.

### Example of a Modified `monitor.json`

Suppose you want to add a new S3 bucket `bucket_3` with a prefix `db3/new_folder/` to be monitored, and change the time interval for `db1/folder/` in `bucket_1` to 2 days. The updated `monitor.json` would look like this:

```json
{
    "bucket_1": [
        {
            "prefix": "db1/folder/",
            "timedelta_days": 2
        },
        {
            "prefix": "db1/folder_2/",
            "timedelta_days": 1
        }
    ],
    "bucket_2":[
        {
            "prefix": "db2/folder1/",
            "timedelta_days": 1
        }
    ],
    "bucket_3": [
        {
            "prefix": "db3/new_folder/",
            "timedelta_days": 1
        }
    ]
}
```

By updating the `monitor.json` file, you can easily configure the monitoring parameters for different S3 buckets and prefixes, ensuring that your data ingestion processes are continuously and effectively monitored.

## Setting Up

1. Deploy the serverless configuration using the Serverless Framework.
2. Ensure the S3 buckets are properly configured and contain the data tables to be monitored.
3. Subscribe to the SNS topic to receive email notifications.

## Notes

- Modify the `CRON_SCHEDULE` environment variable to change the frequency of the monitoring.
- Ensure the IAM role associated with the Lambda function has the necessary permissions to access the S3 buckets and publish to the SNS topic.

This setup helps in maintaining a robust data pipeline by ensuring timely alerts for any disruptions in the data flow.
