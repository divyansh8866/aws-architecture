"""
Divyansh Patel
"""
try:
    import json
    import os
    import boto3
    from modules.create_filename import create_filename
    from datetime import datetime
    print("Import : OK")

except Exception as e:
    raise Exception("Import Error : {} ".format(e))


# Global Variable
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')
print(">> DEBUG MODE = {}".format(DEBUG))



class Datetime(object):
    @staticmethod
    def get_year_month_day():
        """
        Return Year month and day
        :return: str str str
        """
        dt = datetime.now()
        year = dt.year
        month = dt.month
        day = dt.day
        return year, month, day


class S3Handler():
    """
    This class is used to interact with S3 bucket.
    """

    def __init__(self) -> None:
        self.BucketName = os.getenv("DATA_BUCKET_NAME")
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION_NAME"),
        )

    def flatten_dict(self, data, parent_key='', sep='_') -> dict:
        """Flatten data into a single dict

        Args:
            data (dict): dict to be flattened
            parent_key (str, optional): _description_. Defaults to ''.
            sep (str, optional): seperator. Defaults to '_'.

        Raises:
            Exception: Error while flattening dict

        Returns:
            dict: flattened dict
        """
        try:
            items = []
            for key, value in data.items():
                new_key = parent_key + sep + key if parent_key else key
                if type(value) == dict:
                    items.extend(self.flatten_dict(
                        value, new_key, sep=sep).items())
                else:
                    items.append((new_key, value))
            print("Dict Flattening : OK")
            return dict(items)
        except Exception as e:
            print({
                "statusCode": "-1",
                "Error": "Dict Flattening Failed: {}".format(e)})
            raise Exception()

    def dict_clean(self, record):
        """Cleaned the values and convert it into string
        Args:
            record (dict) : dict in which we want to clean the values
        Return:
            cleaned dict with string format values.
        """
        result = {}
        for key, value in record.items():
            if value is None:
                value = 'n/a'
            if value == "None":
                value = 'n/a'
            if value == "null":
                value = 'n/a'
            if len(str(value)) < 1:
                value = 'n/a'
            result[key] = str(value)
        return result

    def upload(self, data, payload_region):
        """This class will upload a dict file to s3.

        Args:
            data (dict): data to be uploaded
            path (str): path for files to be uploaded
        """

        records = ""
        file_name = create_filename(service="jobseeker", filename="DATE_TIME_GUID_PROJECTNAME_SERVICE.json")        
        for item in data:
            item['file_name'] = file_name
            flatten_data = self.flatten_dict(data=item)
            clean_data = self.dict_clean(record=flatten_data)
            records += json.dumps(clean_data) + "\n"

        if records != "":
            try:
                year, month, day = Datetime.get_year_month_day()
                path = "messaging-events/year={year}/month={month}/day={day}/".format(
                    year=year,
                    month=month,
                    day=day
                )
                
                response = self.client.put_object(
                    Body=records,
                    Bucket=self.BucketName,
                    Key=path + file_name,
                    StorageClass='ONEZONE_IA'
                )
                if DEBUG:
                    print("[DEBUG] s3 response : {}".format(response))
                print("File Created on S3 : [OK] {}".format(file_name))
            except Exception as e:
                print({
                    "statusCode": "-1",
                    "Error": "Uploading Error : {}".format(e)})

def lambda_handler(event, context):
    try:
        if DEBUG:
            print("[DEBUG] Payload event : {}".format(event))
        aws_s3 = S3Handler()
        # print(event)
        records = [
            json.loads(record.get("body")).get("detail")
            for record in event.get("Records")
        ]
        print("Event Serialized: OK")
        payload_region = json.loads(
            event.get("Records")[0].get("body")).get("region")

        aws_s3.upload(data=records, payload_region=payload_region)
        print("All : OK")

    except Exception as e:
        print({
            "statusCode": "-1",
            "Error": "S3_handler Failed : {} ".format(e)})
