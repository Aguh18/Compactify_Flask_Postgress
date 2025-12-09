"""
Base Controller Class
Provides common functionality for all file processing controllers
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_file, jsonify
from app.config.paths import path_config, get_module_name
from app.config.database import db
from app.models.fileModel import filesModel

class BaseController:
    def __init__(self, controller_name):
        """
        Initialize base controller with module name

        Args:
            controller_name (str): Name of the controller
        """
        self.module_name = get_module_name(controller_name)
        self.controller_name = controller_name

    def setup_directories(self):
        """
        Setup necessary directories for file operations

        Returns:
            dict: Dictionary with path information
        """
        return path_config.ensure_directories(self.module_name)

    def save_uploaded_file(self, file, uid=None):
        """
        Save uploaded file to uploads directory

        Args:
            file: File object from request
            uid (str): Unique identifier for this operation

        Returns:
            str: Path to saved file
        """
        if uid is None:
            uid = str(uuid.uuid4())

        directories = self.setup_directories()
        filename = secure_filename(file.filename)
        input_path = f"{directories['uploads_path']}/{uid}{filename}"

        file.save(input_path)
        return input_path, filename, uid

    def save_to_database(self, filename, uid):
        """
        Save file information to database

        Args:
            filename (str): Processed filename
            uid (str): Unique identifier

        Returns:
            str: Database file path
        """
        db_path = path_config.get_database_path(self.module_name, f"{uid}{filename}")
        db.session.add(filesModel(db_path))
        db.session.commit()
        return db_path

    def download_file(self, relative_path):
        """
        Download file by relative path

        Args:
            relative_path (str): Relative path from database

        Returns:
            Response: File download response or error
        """
        try:
            file_path = path_config.get_full_file_path(relative_path)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            filename = os.path.basename(file_path)
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"processed_{filename}"
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def preview_file(self, relative_path):
        """
        Preview file by relative path

        Args:
            relative_path (str): Relative path from database

        Returns:
            Response: File preview response or error
        """
        try:
            file_path = path_config.get_full_file_path(relative_path)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            return send_file(file_path)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def get_download_paths(self, uid, filename):
        """
        Get paths for file processing

        Args:
            uid (str): Unique identifier
            filename (str): Filename

        Returns:
            dict: Dictionary with path information
        """
        directories = self.setup_directories()
        secure_name = secure_filename(filename)

        return {
            'downloads_path': directories['downloads_path'],
            'output_filename': f"{uid}{secure_name}",
            'output_path': f"{directories['downloads_path']}/{uid}{secure_name}"
        }