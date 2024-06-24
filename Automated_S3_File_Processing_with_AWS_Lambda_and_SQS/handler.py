import boto3
import json
import urllib.parse

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def process_file(event, context):
    for record in event['Records']:
        # Get the message from SQS
        message = json.loads(record['body'])
        src_bucket = message['Records'][0]['s3']['bucket']['name']
        src_key = urllib.parse.unquote_plus(message['Records'][0]['s3']['object']['key'])
        dest_bucket = 'your-processed-files-bucket-name'
        dest_key = src_key.replace('raw_files/', 'processed_files/')
        
        try:
            copy_source = {'Bucket': src_bucket, 'Key': src_key}
            s3.copy_object(CopySource=copy_source, Bucket=dest_bucket, Key=dest_key)
            print(f'File copied from {src_key} to {dest_key}')
        except Exception as e:
            print(f'Error processing file {src_key}: {e}')
            raise e
