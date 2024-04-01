from fastapi import FastAPI, UploadFile, File, HTTPException
from fileupload_operation import upload_file_to_s3, delete_file_from_s3
import logging
from loggersconstants import UPLOAD_SUCCESS, UPLOAD_ERROR, DELETE_SUCCESS, DELETE_ERROR, HTTP_EXCEPTION_UPLOAD, HTTP_EXCEPTION_DELETE
from helper import validate_file

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload/")
async def upload_file_handler(file: UploadFile = File(...)):
    try:
        validate_file(file)
        response = upload_file_to_s3(file, file.filename)
        logger.info(UPLOAD_SUCCESS.format(filename=file.filename))
        return response
    except HTTPException as e:
        logger.error(HTTP_EXCEPTION_UPLOAD.format(filename=file.filename, detail=e.detail))
        raise e
    except Exception as e:
        logger.error(UPLOAD_ERROR.format(filename=file.filename, error=e))
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/delete/{filename}")
async def delete_file_handler(filename: str):
    try:
        response = delete_file_from_s3(filename)
        logger.info(DELETE_SUCCESS.format(filename=filename))
        return response
    except HTTPException as e:
        logger.error(HTTP_EXCEPTION_DELETE.format(filename=filename, detail=e.detail))
        raise e
    except Exception as e:
        logger.error(DELETE_ERROR.format(filename=filename, error=e))
        raise HTTPException(status_code=400, detail=str(e))