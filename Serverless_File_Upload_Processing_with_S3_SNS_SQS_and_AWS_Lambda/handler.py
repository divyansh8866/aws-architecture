import json
import boto3

def process_file_1(event, context):
    for record in event['Records']:
        payload = json.loads(record['body'])
        print(f"Processing file 1: {payload}")

def process_file_2(event, context):
    for record in event['Records']:
        payload = json.loads(record['body'])
        print(f"Processing file 2: {payload}")
