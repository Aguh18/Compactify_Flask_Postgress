import os
import uuid
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename
from dotenv import dotenv_values
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class R2Helper:
    """
    Cloudflare R2 Storage Helper
    Provides interface for uploading, downloading, and managing files in Cloudflare R2
    """

    def __init__(self):
        """Initialize R2 client with credentials from environment variables"""
        self.config = dotenv_values()

        # R2 Configuration
        self.account_id = self.config.get('R2_ACCOUNT_ID')
        self.access_key = self.config.get('R2_ACCESS_KEY_ID')
        self.secret_key = self.config.get('R2_SECRET_ACCESS_KEY')
        self.bucket_name = self.config.get('R2_BUCKET_NAME')
        self.public_url = self.config.get('R2_PUBLIC_URL')

        # Validate R2 configuration
        if not all([self.account_id, self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError(
                "Cloudflare R2 storage is required. Please configure the following in your .env file:\n"
                "- R2_ACCOUNT_ID: Your Cloudflare account ID\n"
                "- R2_ACCESS_KEY_ID: Your R2 access key ID\n"
                "- R2_SECRET_ACCESS_KEY: Your R2 secret access key\n"
                "- R2_BUCKET_NAME: Your R2 bucket name\n"
                "\nGet these from: https://dash.cloudflare.com/r2/api-tokens"
            )

        # Initialize R2 client
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'
            )

            # Initialize resource for easier operations
            self.resource = boto3.resource(
                's3',
                endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'
            )
            logger.info("R2 Helper initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize R2 client: {e}")

    def upload_file(self, file_obj, filename=None, folder="", content_type=None):
        """
        Upload file to R2 storage

        Args:
            file_obj: File object (from request.files or file path)
            filename: Original filename (optional)
            folder: Folder path in bucket (optional)
            content_type: MIME type (optional)

        Returns:
            dict: {
                'success': bool,
                'file_key': str,
                'file_url': str,
                'message': str
            }
        """
        try:
            # Generate secure filename if not provided
            if filename is None:
                if hasattr(file_obj, 'filename'):
                    filename = file_obj.filename
                else:
                    filename = str(file_obj)

            secure_name = secure_filename(filename)

            # Generate unique file key
            file_ext = os.path.splitext(secure_name)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"

            if folder:
                file_key = f"{folder}/{unique_filename}"
            else:
                file_key = unique_filename

            # Determine content type
            if content_type is None:
                if hasattr(file_obj, 'content_type'):
                    content_type = file_obj.content_type
                else:
                    # Basic content type detection
                    ext = file_ext.lower()
                    content_type_map = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp',
                        '.pdf': 'application/pdf',
                        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        '.zip': 'application/zip',
                        '.mp3': 'audio/mpeg',
                        '.wav': 'audio/wav',
                    }
                    content_type = content_type_map.get(ext, 'application/octet-stream')

            # Prepare extra args
            extra_args = {
                'ContentType': content_type,
                'Metadata': {
                    'original_filename': secure_name,
                    'upload_date': datetime.now().isoformat()
                }
            }

            # Upload file
            if hasattr(file_obj, 'save'):  # File object from request
                file_obj.seek(0)  # Reset file pointer
                self.client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    file_key,
                    ExtraArgs=extra_args
                )
            else:  # File path
                self.client.upload_file(
                    file_obj,
                    self.bucket_name,
                    file_key,
                    ExtraArgs=extra_args
                )

            # Generate URL
            if self.public_url:
                file_url = f"{self.public_url}/{file_key}"
            else:
                # Generate presigned URL for private buckets
                file_url = self.generate_presigned_url(file_key)

            logger.info(f"Successfully uploaded file: {file_key}")

            return {
                'success': True,
                'file_key': file_key,
                'file_url': file_url,
                'original_filename': secure_name,
                'message': 'File uploaded successfully'
            }

        except ClientError as e:
            logger.error(f"Error uploading file to R2: {e}")
            return {
                'success': False,
                'message': f"Failed to upload file: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            return {
                'success': False,
                'message': f"Unexpected error: {str(e)}"
            }

    def download_file(self, file_key, local_path=None):
        """
        Download file from R2 storage

        Args:
            file_key: Key of the file in R2
            local_path: Local path to save file (optional)

        Returns:
            dict: {
                'success': bool,
                'file_obj': File object or None,
                'local_path': str or None,
                'message': str
            }
        """
        try:
            if local_path:
                # Download to local file
                self.client.download_file(self.bucket_name, file_key, local_path)
                return {
                    'success': True,
                    'local_path': local_path,
                    'message': 'File downloaded successfully'
                }
            else:
                # Download as file object
                obj = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
                return {
                    'success': True,
                    'file_obj': obj['Body'],
                    'content_type': obj.get('ContentType', 'application/octet-stream'),
                    'size': obj.get('ContentLength', 0),
                    'message': 'File retrieved successfully'
                }

        except ClientError as e:
            logger.error(f"Error downloading file from R2: {e}")
            return {
                'success': False,
                'message': f"Failed to download file: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {e}")
            return {
                'success': False,
                'message': f"Unexpected error: {str(e)}"
            }

    def delete_file(self, file_key):
        """
        Delete file from R2 storage

        Args:
            file_key: Key of the file to delete

        Returns:
            dict: {
                'success': bool,
                'message': str
            }
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file: {file_key}")

            return {
                'success': True,
                'message': 'File deleted successfully'
            }

        except ClientError as e:
            logger.error(f"Error deleting file from R2: {e}")
            return {
                'success': False,
                'message': f"Failed to delete file: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {e}")
            return {
                'success': False,
                'message': f"Unexpected error: {str(e)}"
            }

    def generate_presigned_url(self, file_key, expiration=3600):
        """
        Generate presigned URL for file access

        Args:
            file_key: Key of the file
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL
        """
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

    def list_files(self, folder="", limit=100):
        """
        List files in bucket or folder

        Args:
            folder: Folder path to list (optional)
            limit: Maximum number of files to return

        Returns:
            dict: {
                'success': bool,
                'files': list,
                'message': str
            }
        """
        try:
            prefix = folder if folder.endswith('/') else f"{folder}/" if folder else ""

            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'url': f"{self.public_url}/{obj['Key']}" if self.public_url else self.generate_presigned_url(obj['Key'])
                    })

            return {
                'success': True,
                'files': files,
                'count': len(files),
                'message': f"Found {len(files)} files"
            }

        except ClientError as e:
            logger.error(f"Error listing files from R2: {e}")
            return {
                'success': False,
                'files': [],
                'message': f"Failed to list files: {str(e)}"
            }

    def get_file_info(self, file_key):
        """
        Get file metadata from R2

        Args:
            file_key: Key of the file

        Returns:
            dict: File metadata
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=file_key)

            return {
                'success': True,
                'metadata': {
                    'key': file_key,
                    'size': response.get('ContentLength', 0),
                    'content_type': response.get('ContentType', ''),
                    'last_modified': response.get('LastModified'),
                    'metadata': response.get('Metadata', {}),
                    'etag': response.get('ETag', '')
                }
            }

        except ClientError as e:
            logger.error(f"Error getting file info from R2: {e}")
            return {
                'success': False,
                'message': f"Failed to get file info: {str(e)}"
            }

    def copy_file(self, source_key, destination_key):
        """
        Copy file within R2 storage

        Args:
            source_key: Source file key
            destination_key: Destination file key

        Returns:
            dict: Operation result
        """
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key
            )

            logger.info(f"Successfully copied file from {source_key} to {destination_key}")

            return {
                'success': True,
                'message': 'File copied successfully'
            }

        except ClientError as e:
            logger.error(f"Error copying file in R2: {e}")
            return {
                'success': False,
                'message': f"Failed to copy file: {str(e)}"
            }

    def move_file(self, source_key, destination_key):
        """
        Move file within R2 storage (copy + delete)

        Args:
            source_key: Source file key
            destination_key: Destination file key

        Returns:
            dict: Operation result
        """
        # Copy file first
        copy_result = self.copy_file(source_key, destination_key)

        if copy_result['success']:
            # Delete original file
            delete_result = self.delete_file(source_key)

            if delete_result['success']:
                return {
                    'success': True,
                    'message': 'File moved successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f"File copied but failed to delete original: {delete_result['message']}"
                }
        else:
            return copy_result

# Global instance
r2_helper = R2Helper()