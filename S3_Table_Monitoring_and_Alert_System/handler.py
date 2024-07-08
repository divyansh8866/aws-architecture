import json
import os
import boto3
from datetime import datetime, timedelta, timezone

s3 = boto3.client('s3')
sns = boto3.client('sns')

TOPIC_ARN = os.environ['TOPIC_ARN']

def load_metadata(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)

metadata = load_metadata('monitor.json')

def check_updates(bucket_name, prefix, timedelta_days):
    current_date = datetime.now(timezone.utc)
    specific_date = current_date - timedelta(days=timedelta_days)
    print(f"START DATE : {specific_date} for bucket {bucket_name} and prefix {prefix}")
    count = 0
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in response:
        for obj in response['Contents']:
            if obj['LastModified'] > specific_date:
                count += 1
    print({
        'statusCode': 200,
        'body': json.dumps({
            'bucket_name': bucket_name,
            'count': count,
            'period': f"{specific_date} to {current_date}"
        })
    })
    return {
        'statusCode': 200,
        'body': {
            'bucket_name': bucket_name,
            'count': count,
            'period': f"{specific_date} to {current_date}"
        }
    }
    
def format_message(payload):
    message = "S3 Monitoring\n-------------------------------------------\n"
    for entry in payload:
        message += (
            f"{entry['table']} : {entry['status']}\n"
            f"Bucket: {entry['bucket']}\n"
            f"Message: {entry['message']}\n"
            "-------------------------------------------\n"
        )
    return message

def send_notification(message):
    payload = {
        "default":json.dumps(message),
        "email":format_message(message)
    }
    sns.publish(
        TopicArn=TOPIC_ARN,
        MessageStructure = 'json',
        Message=json.dumps(payload),
        Subject='S3 Monitoring Alert'
    )
    print("Report Published to SNS")

def monitor(event, context):
    print(">> STARTING ")
    response_list = []
    for bucket_name, prefix_list in metadata.items():
        for item in prefix_list:
            prefix = item['prefix']
            timedelta_days = item['timedelta_days']
            response = check_updates(bucket_name, prefix, timedelta_days)
            if response.get('body', {}).get('count', 0) == 0:
                response = {
                    "status_code": -1,
                    "status": "WARNING",
                    "bucket":response.get('body', {}).get('bucket_name', ""),
                    "table": prefix.split('/')[1],
                    "message": f"No new data for time period {response.get('body', {}).get('period', 0)}."
                }
            else:
                response = {
                    "status_code": 200,
                    "status": "OK",
                    "bucket":response.get('body', {}).get('bucket_name', ""),
                    "table": prefix.split('/')[1],
                    "message": f"{response.get('body', {}).get('count', 0)} new files found for time period {response.get('body', {}).get('period', 0)}."
                }
            response_list.append(response)
    print(response_list)
    send_notification(response_list)
    print(">> SUCCESSFUL")