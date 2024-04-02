from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.fileUploadServices import upload_file_to_s3, delete_file_from_s3
from app.core.constants.loggersConstants import UPLOAD_SUCCESS, UPLOAD_ERROR, DELETE_SUCCESS, DELETE_ERROR, HTTP_EXCEPTION_UPLOAD, HTTP_EXCEPTION_DELETE
from app.utils.fileUploadUtils import validate_file
from app.core.constants.httpStatusConstants import BAD_REQUEST
fileUploadRouter = APIRouter()
import logging

logger = logging.getLogger(__name__)

@fileUploadRouter.post("/upload/")
async def upload_file_handler(file: UploadFile = File(...)):
    try:
        validate_file(file)
        uploadSuccessResponse = upload_file_to_s3(file, file.filename)
        logger.info(UPLOAD_SUCCESS.format(filename=file.filename))
        return uploadSuccessResponse
    except HTTPException as e:
        logger.error(HTTP_EXCEPTION_UPLOAD.format(filename=file.filename, detail=e.detail))
        raise e
    except Exception as e:
        logger.error(UPLOAD_ERROR.format(filename=file.filename, error=e))
        raise HTTPException(status_code=BAD_REQUEST, detail=str(e))

@fileUploadRouter.delete("/delete/{filename}")
async def delete_file_handler(filename: str):
    try:
        deleteSuccessResponse = delete_file_from_s3(filename)
        logger.info(DELETE_SUCCESS.format(filename=filename))
        return deleteSuccessResponse
    except HTTPException as error:
        logger.error(HTTP_EXCEPTION_DELETE.format(filename=filename, detail=error.detail))
        raise e
    except Exception as error:
        logger.error(DELETE_ERROR.format(filename=filename, error=error))
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error))