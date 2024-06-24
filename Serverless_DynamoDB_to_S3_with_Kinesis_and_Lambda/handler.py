import json

def process_data(event, context):
    for record in event['records']:
        payload = json.loads(record['data'])
        # Process the data as required
        print(f"Processed record: {payload}")
        
    return {
        'records': [{
            'recordId': record['recordId'],
            'result': 'Ok'
        } for record in event['records']]
    }
