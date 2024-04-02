from fastapi import FastAPI, UploadFile, File, HTTPException
import logging
from app.api.v1.fileuploadEndpoint import fileUploadRouter
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.include_router(fileUploadRouter)
