import os
import uuid
import tempfile
from werkzeug.utils import secure_filename
from flask import send_file, jsonify
from app.config.database import db
from app.models.fileModel import filesModel
from app.service.r2_helper import r2_helper

class BaseController:
    def __init__(self, controller_name):
        self.module_name = controller_name.lower()
        self.controller_name = controller_name

    def save_uploaded_file(self, file, uid=None):
        """
        Save uploaded file to R2 storage

        Args:
            file: File object
            uid: Unique identifier (optional)

        Returns:
            tuple: (file_key, filename, uid)
        """
        if uid is None:
            uid = str(uuid.uuid4())

        filename = secure_filename(file.filename)

        # Upload to R2
        result = r2_helper.upload_file(
            file,
            filename=filename,
            folder=self.module_name
        )

        if not result['success']:
            raise RuntimeError(f"Failed to upload file to R2: {result['message']}")

        return result['file_key'], filename, uid

    def save_to_database(self, file_key, uid, original_size=None, compressed_size=None, compression_ratio=None, quality=None):
        """
        Save file record to database

        Args:
            file_key: R2 file key
            uid: Unique identifier
            original_size: Original file size in bytes
            compressed_size: Compressed file size in bytes
            compression_ratio: Compression percentage
            quality: Quality level used

        Returns:
            str: Full download URL
        """
        from app.service.r2_helper import r2_helper

        # Generate full download URL
        if r2_helper.public_url:
            download_url = f"{r2_helper.public_url}/{file_key}"
        else:
            download_url = r2_helper.generate_presigned_url(file_key)

        db.session.add(filesModel(
            download_url,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            quality=quality
        ))
        db.session.commit()
        return download_url

    def download_file(self, file_or_url):
        """
        Download file from R2 storage

        Args:
            file_or_url: R2 file key or full download URL

        Returns:
            File response or error
        """
        try:
            # If it's a URL, extract the file key
            if file_or_url.startswith('http'):
                # Extract file key from URL: https://domain/module/filename
                parts = file_or_url.split('/')
                if len(parts) >= 4:  # https:, , domain, module, filename
                    file_key = '/'.join(parts[3:])  # Join module/filename
                else:
                    file_key = file_or_url  # Fallback
            else:
                file_key = file_or_url

            # Download from R2
            result = r2_helper.download_file(file_key)

            if not result['success']:
                return jsonify({"error": "File not found in storage"}), 404

            # Create temporary file for download
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(result['file_obj'].read())
                tmp_file_path = tmp_file.name

            filename = os.path.basename(file_key)

            response = send_file(
                tmp_file_path,
                as_attachment=True,
                download_name=f"processed_{filename}"
            )

            # Clean up temp file after response
            response.call_on_close(lambda: os.unlink(tmp_file_path))

            return response

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def preview_file(self, file_or_url):
        """
        Preview file from R2 storage

        Args:
            file_or_url: R2 file key or full download URL

        Returns:
            File response or error
        """
        try:
            # If it's a URL, extract the file key
            if file_or_url.startswith('http'):
                # Extract file key from URL: https://domain/module/filename
                parts = file_or_url.split('/')
                if len(parts) >= 4:  # https:, , domain, module, filename
                    file_key = '/'.join(parts[3:])  # Join module/filename
                else:
                    file_key = file_or_url  # Fallback
            else:
                file_key = file_or_url

            # Get from R2
            result = r2_helper.download_file(file_key)

            if not result['success']:
                return jsonify({"error": "File not found in storage"}), 404

            # Create temporary file for preview
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(result['file_obj'].read())
                tmp_file_path = tmp_file.name

            response = send_file(tmp_file_path)

            # Clean up temp file after response
            response.call_on_close(lambda: os.unlink(tmp_file_path))

            return response

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def save_processed_file(self, file_path_or_content, original_filename, uid=None):
        """
        Save processed file to R2 storage

        Args:
            file_path_or_content: File path or file content
            original_filename: Original filename
            uid: Unique identifier (optional)

        Returns:
            str: File key
        """
        if uid is None:
            uid = str(uuid.uuid4())

        secure_name = secure_filename(original_filename)

        # Upload to R2
        if isinstance(file_path_or_content, str):
            # It's a file path
            result = r2_helper.upload_file(
                file_path_or_content,
                filename=secure_name,
                folder=self.module_name
            )
        else:
            # It's file content - create temp file first
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(file_path_or_content)
                tmp_file_path = tmp_file.name

            result = r2_helper.upload_file(
                tmp_file_path,
                filename=secure_name,
                folder=self.module_name
            )

            # Clean up temp file
            os.unlink(tmp_file_path)

        if not result['success']:
            raise RuntimeError(f"Failed to upload processed file to R2: {result['message']}")

        return result['file_key']

    def get_download_info(self, uid, filename):
        """
        Get download information for processed file

        Args:
            uid: Unique identifier
            filename: Original filename

        Returns:
            dict: Download information
        """
        secure_name = secure_filename(filename)
        file_key = f"{self.module_name}/{uid}{secure_name}"

        return {
            'file_key': file_key,
            'filename': secure_name,
            'download_name': f"processed_{secure_name}"
        }

    def cleanup_files(self, file_key):
        """
        Clean up file from R2 storage

        Args:
            file_key: R2 file key
        """
        try:
            result = r2_helper.delete_file(file_key)
            if not result['success']:
                print(f"Error cleaning up file {file_key}: {result['message']}")
        except Exception as e:
            print(f"Error cleaning up file {file_key}: {e}")

    def get_file_info(self, file_key):
        """
        Get file metadata from R2

        Args:
            file_key: R2 file key

        Returns:
            dict: File metadata
        """
        return r2_helper.get_file_info(file_key)

    def move_file(self, source_key, destination_folder=None):
        """
        Move file within R2 storage

        Args:
            source_key: Source file key
            destination_folder: Destination folder (optional)

        Returns:
            dict: Operation result
        """
        if destination_folder is None:
            destination_folder = f"{self.module_name}/processed"

        filename = os.path.basename(source_key)
        destination_key = f"{destination_folder}/{filename}"

        return r2_helper.move_file(source_key, destination_key)