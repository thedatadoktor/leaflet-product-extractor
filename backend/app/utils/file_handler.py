"""
File handling utilities for uploads and temporary storage.
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import app_logger as logger


class FileHandler:
    """Handle file uploads and temporary storage"""
    
    def __init__(
        self,
        input_dir: Optional[str] = None,
        output_dir: Optional[str] = None
    ):
        """
        Initialize file handler.
        
        Args:
            input_dir: Directory for uploaded files
            output_dir: Directory for output files
        """
        self.input_dir = Path(input_dir or settings.INPUT_DIRECTORY)
        self.output_dir = Path(output_dir or settings.OUTPUT_DIRECTORY)
        
        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileHandler initialized - Input: {self.input_dir}, Output: {self.output_dir}")
    
    async def save_upload(
        self,
        file_content: bytes,
        original_filename: str
    ) -> str:
        """
        Save uploaded file asynchronously.
        
        Args:
            file_content: File content as bytes
            original_filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_extension = Path(original_filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        filepath = self.input_dir / unique_filename
        
        # Save file asynchronously
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"Saved upload: {original_filename} -> {filepath}")
        return str(filepath)
    
    def save_upload_sync(
        self,
        file_content: bytes,
        original_filename: str
    ) -> str:
        """
        Save uploaded file synchronously.
        
        Args:
            file_content: File content as bytes
            original_filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_extension = Path(original_filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        filepath = self.input_dir / unique_filename
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved upload: {original_filename} -> {filepath}")
        return str(filepath)
    
    def cleanup_file(self, filepath: str) -> bool:
        """
        Delete a file.
        
        Args:
            filepath: Path to file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            Path(filepath).unlink(missing_ok=True)
            logger.info(f"Deleted file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {filepath}: {e}")
            return False
    
    def get_file_size(self, filepath: str) -> int:
        """
        Get file size in bytes.
        
        Args:
            filepath: Path to file
            
        Returns:
            File size in bytes
        """
        return Path(filepath).stat().st_size
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove dangerous characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name
        
        # Remove or replace dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        return filename
