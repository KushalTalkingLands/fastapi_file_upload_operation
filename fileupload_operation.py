import boto3
from fastapi import UploadFile, HTTPException
import logging
from aws_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME, S3_BUCKET_NAME
from loggersconstants import UPLOAD_SUCCESS, UPLOAD_ERROR, DELETE_SUCCESS, DELETE_ERROR, HTTP_EXCEPTION_UPLOAD, HTTP_EXCEPTION_DELETE


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION_NAME)

def create_bucket(bucket_name):
    try:
        location_constraint = {'LocationConstraint': AWS_REGION_NAME}
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
    if not bucket_exists(S3_BUCKET_NAME):
        create_bucket(S3_BUCKET_NAME)
    if not bucket_exists(f"{S3_BUCKET_NAME}-deletedfile"):
        create_bucket(f"{S3_BUCKET_NAME}-deletedfile")

def upload_file_to_s3(file: UploadFile, filename: str):
    ensure_buckets_exist()
    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, filename)
        logger.info(f"File '{filename}' uploaded to bucket '{S3_BUCKET_NAME}'.")
        return {
            "path": f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/{filename}",
            "filename": filename
            }
    except Exception as e:
        logger.error(f"Error uploading file '{filename}' to bucket '{S3_BUCKET_NAME}': {e}")
        raise HTTPException(status_code=400, detail=str(e))

def delete_file_from_s3(filename: str):
    ensure_buckets_exist()
    try:
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=filename)
        s3_client.copy_object(Bucket=f"{S3_BUCKET_NAME}-deletedfile", Key=filename, CopySource={'Bucket': S3_BUCKET_NAME, 'Key': filename})
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
        logger.info(f"File '{filename}' deleted from bucket '{S3_BUCKET_NAME}'.")
        return {
            "path": f"https://{S3_BUCKET_NAME}-deletedfile.s3.{AWS_REGION_NAME}.amazonaws.com/{filename}",
            "filename": filename
            }
    except Exception as e:
        logger.error(f"Error deleting file '{filename}' from bucket '{S3_BUCKET_NAME}': {e}")
        raise HTTPException(status_code=400, detail=str(e))