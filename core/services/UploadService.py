"""
File upload handling. Extend for S3 in production.
"""
from django.core.files.uploadedfile import UploadedFile


class UploadService:
    """Service for handling file uploads."""

    @staticmethod
    def save_upload(uploaded_file: UploadedFile, path_prefix: str):
        """Save uploaded file under path_prefix. Return relative path."""
        return f"{path_prefix}/{uploaded_file.name}"
