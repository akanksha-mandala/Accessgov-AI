import os
import uuid
import logging
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status
from config import settings

logger = logging.getLogger("accessgov.utils.file_storage")

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/pjpeg"}


class FileStorageUtil:
    """
    Secure File Storage Utility (Refinements #1 & #2).
    Enforces UUID file naming, max 10MB size limits, path traversal prevention, and extension/MIME validation.
    Stores files in isolated local directory without exposing static public URLs.
    """

    def __init__(self, storage_path: str = None, max_size_mb: int = None):
        self.storage_path = storage_path or settings.DOCUMENT_STORAGE_PATH
        self.max_bytes = (max_size_mb or settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024
        os.makedirs(self.storage_path, exist_ok=True)

    def validate_and_save_upload(self, upload_file: UploadFile) -> Tuple[str, str, int, str]:
        """
        Validates file extension, MIME type, size limit, and saves file securely with UUID name.
        Returns Tuple[saved_file_path, secure_filename, file_size_bytes, mime_type].
        """
        original_name = os.path.basename(upload_file.filename or "upload.bin")
        _, ext = os.path.splitext(original_name)
        ext = ext.lower()

        # 1. Validate File Extension
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: PDF, PNG, JPG, JPEG."
            )

        # 2. Validate Client MIME Type
        mime_type = upload_file.content_type.lower() if upload_file.content_type else "application/octet-stream"
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type '{mime_type}'. Allowed formats: PDF, PNG, JPG, JPEG."
            )

        # 3. Read Content and Enforce 10MB Size Limit
        contents = upload_file.file.read()
        file_size = len(contents)

        if file_size > self.max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB (Uploaded size: {file_size / (1024*1024):.2f}MB)."
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded. Please upload a valid document."
            )

        # 4. Generate UUID Filename to prevent Path Traversal and Script Execution
        unique_filename = f"doc_{uuid.uuid4().hex}{ext}"
        saved_path = os.path.abspath(os.path.join(self.storage_path, unique_filename))

        # Ensure path stays within storage directory
        if not saved_path.startswith(os.path.abspath(self.storage_path)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security violation: Invalid file path traversal detected."
            )

        # 5. Write Content to Disk
        with open(saved_path, "wb") as f:
            f.write(contents)

        logger.info(f"Saved upload file securely to: {saved_path} ({file_size} bytes)")
        return saved_path, unique_filename, file_size, mime_type

    def delete_file(self, file_path: str) -> bool:
        """
        Safely deletes a physical file from storage.
        """
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted storage file: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {str(e)}")
        return False


file_storage_util = FileStorageUtil()
