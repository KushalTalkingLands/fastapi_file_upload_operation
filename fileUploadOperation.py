import boto3
import os
from fastapi import UploadFile, HTTPException
import logging
from loggersConstants import UPLOAD_SUCCESS, UPLOAD_ERROR, DELETE_SUCCESS, DELETE_ERROR, HTTP_EXCEPTION_UPLOAD, HTTP_EXCEPTION_DELETE
from dotenv import load_dotenv
load_dotenv()

region_name = os.getenv("AWS_REGION_NAME")
bucket_name = os.getenv("S3_BUCKET_NAME")
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

s3_client = boto3.client('s3')

def create_bucket(bucket_name):
    try:
        location_constraint = {'LocationConstraint': region_name}
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location_constraint)
        logger.info(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating bucket '{bucket_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))

def bucket_exists(bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        logger.error(f"Error checking bucket '{bucket_name}' existence: {e}")
        return False

def ensure_buckets_exist():
    if not bucket_exists(bucket_name):
        create_bucket(bucket_name)
    if not bucket_exists(f"{bucket_name}-deletedfile"):
        create_bucket(f"{bucket_name}-deletedfile")

def upload_file_to_s3(file: UploadFile, filename: str):
    ensure_buckets_exist()
    try:
        s3_client.upload_fileobj(file.file, bucket_name, filename)
        logger.info(f"File '{filename}' uploaded to bucket '{bucket_name}'.")
        return {
            "path": f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{filename}",
            "filename": filename
            }
    except Exception as e:
        logger.error(f"Error uploading file '{filename}' to bucket '{bucket_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))

def delete_file_from_s3(filename: str):
    ensure_buckets_exist()
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=filename)
        s3_client.copy_object(Bucket=f"{bucket_name}-deletedfile", Key=filename, CopySource={'Bucket': bucket_name, 'Key': filename})
        s3_client.delete_object(Bucket=bucket_name, Key=filename)
        logger.info(f"File '{filename}' deleted from bucket '{bucket_name}'.")
        return {
            "path": f"https://{bucket_name}-deletedfile.s3.{region_name}.amazonaws.com/{filename}",
            "filename": filename
            }
    except Exception as e:
        logger.error(f"Error deleting file '{filename}' from bucket '{bucket_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))