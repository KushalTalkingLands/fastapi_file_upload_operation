import os
from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv
from appConstants import ENV_ACCEPTED_EXTENSIONS_NOT_FOUND, FILE_EMPTY
# config = dotenv_values(".env")
load_dotenv() 


def validate_file(file: UploadFile):
    accepted_extensions = os.getenv("ACCEPTED_EXTENSIONS")
    display_accepted_extensions = accepted_extensions
    accepted_file_prefix = os.getenv("ACCEPTED_FILENAME_PREFIX")
    if not accepted_extensions:
        raise ValueError(ENV_ACCEPTED_EXTENSIONS_NOT_FOUND)
    
    accepted_extensions = set(accepted_extensions.split(','))
    # print(accepted_extensions)
    if not file.filename.startswith(accepted_file_prefix):
        raise HTTPException(status_code=400, detail=f"Filename must start with '{accepted_file_prefix}'")
    
    # Check if file extension is in the accepted extensions
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in accepted_extensions:
        raise HTTPException(status_code=400, detail=f"File extension must be  '{display_accepted_extensions}'")
    if file.file.seek(0, os.SEEK_END) == 0:
        raise HTTPException(status_code=400, detail=FILE_EMPTY)
