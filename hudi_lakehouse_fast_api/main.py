from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import daft
import boto3
import asyncio

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

class DivisionIDInput(BaseModel):
    division_id: int

# Initialize session and credentials once to reuse them
region = os.getenv("DEV_AWS_REGION")
s3_path = os.getenv("DEV_S3_PATH")

session = boto3.session.Session(
    aws_access_key_id=os.getenv("DEV_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("DEV_AWS_SECRET_ACCESS_KEY"),
    region_name=region
)
creds = session.get_credentials()

io_config = daft.io.IOConfig(
    s3=daft.io.S3Config(
        access_key=creds.secret_key,
        key_id=creds.access_key,
        session_token=creds.token,
        region_name=region,
    )
)

@app.post("/fetch_hudi_data")
async def fetch_hudi_data(input_data: DivisionIDInput):
    try:
        # Use async to improve performance with I/O operations
        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(None, lambda: daft.read_hudi(s3_path, io_config=io_config))
        df = df.where(df["pk_column"] == input_data.division_id).limit(2)
        data_dict = df.to_pydict()
        json_data = json.dumps(data_dict, default=str)  # Convert datetimes to strings

        return json.loads(json_data)  # Return as proper JSON
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
