import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")

class FileStorageService:
    @staticmethod
    def save_file(file: UploadFile) -> str:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path
