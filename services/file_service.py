"""File storage service."""

import os
import uuid
import shutil
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status
from app.config.settings import settings

class FileService:
    """Service for handling file uploads and secure downloads."""

    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
    ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        self.storage_backend = settings.STORAGE_BACKEND
        self.upload_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", settings.UPLOAD_DIR)
        )
        if self.storage_backend == "local":
            os.makedirs(self.upload_dir, exist_ok=True)

        self._s3_client = None

    @property
    def s3_client(self):
        """Lazy loader for S3 client."""
        if self._s3_client is None and self.storage_backend == "s3":
            try:
                import boto3
                self._s3_client = boto3.client(
                    "s3",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="boto3 library is required for S3 storage, but not installed."
                )
        return self._s3_client

    async def validate_file(self, file: UploadFile) -> Tuple[str, int]:
        """Validate file type, extension, and size."""
        # 1. Validate Extension
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extension {ext} not allowed. Supported formats: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # 2. Validate Content Type
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content type {file.content_type} not allowed."
            )

        # 3. Validate Size
        try:
            await file.seek(0, 2)
            size = await file.tell()
            await file.seek(0)
        except Exception:
            # Fallback size calculation if seek is not supported
            size = 0
            file_content = await file.read()
            size = len(file_content)
            await file.seek(0)

        if size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size of 10MB (file size: {size / (1024*1024):.2f}MB)"
            )

        return ext, size

    async def upload_file(
        self,
        file: UploadFile,
        company_id: str,
        resource_type: str,
        resource_id: str
    ) -> dict:
        """Upload file either to local disk or AWS S3."""
        ext, size = await self.validate_file(file)
        unique_id = uuid.uuid4().hex
        filename = f"{unique_id}{ext}"

        if self.storage_backend == "s3" and settings.S3_BUCKET_NAME:
            # Upload to S3
            key = f"{company_id}/{resource_type}/{resource_id}/{filename}"
            try:
                self.s3_client.upload_fileobj(
                    file.file,
                    settings.S3_BUCKET_NAME,
                    key,
                    ExtraArgs={"ContentType": file.content_type}
                )
                # S3 URL (could be presigned or public depends on settings)
                url = f"s3://{settings.S3_BUCKET_NAME}/{key}"
                return {
                    "filename": file.filename,
                    "stored_filename": filename,
                    "file_type": ext.replace(".", ""),
                    "size_bytes": size,
                    "storage_key": key,
                    "url": url
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload to S3: {str(e)}"
                )
        else:
            # Upload to local disk
            # Directory structure: upload_dir/company_id/resource_type/resource_id/
            relative_dir = os.path.join(company_id, resource_type, resource_id)
            target_dir = os.path.join(self.upload_dir, relative_dir)
            os.makedirs(target_dir, exist_ok=True)

            target_path = os.path.join(target_dir, filename)
            try:
                with open(target_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # The URL will point to our secure download API router
                # E.g., /v1/documents/download/filename
                storage_key = os.path.join(relative_dir, filename)
                url = f"/v1/documents/download/{filename}"

                return {
                    "filename": file.filename,
                    "stored_filename": filename,
                    "file_type": ext.replace(".", ""),
                    "size_bytes": size,
                    "storage_key": storage_key,
                    "url": url
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to write file locally: {str(e)}"
                )

    def get_local_file_path(self, storage_key: str) -> str:
        """Get the full absolute path of a locally stored file."""
        return os.path.join(self.upload_dir, storage_key)

    def delete_file(self, storage_key: str) -> bool:
        """Delete file from storage."""
        if self.storage_backend == "s3" and settings.S3_BUCKET_NAME:
            try:
                self.s3_client.delete_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=storage_key
                )
                return True
            except Exception:
                return False
        else:
            full_path = self.get_local_file_path(storage_key)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    return True
                except Exception:
                    return False
            return False
