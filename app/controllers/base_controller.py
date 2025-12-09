import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_file, jsonify
from app.config.paths import path_config, get_module_name
from app.config.database import db
from app.models.fileModel import filesModel

class BaseController:
    def __init__(self, controller_name):
        self.module_name = get_module_name(controller_name)
        self.controller_name = controller_name

    def setup_directories(self):
        return path_config.ensure_directories(self.module_name)

    def save_uploaded_file(self, file, uid=None):
        if uid is None:
            uid = str(uuid.uuid4())

        directories = self.setup_directories()
        filename = secure_filename(file.filename)
        input_path = f"{directories['uploads_path']}/{uid}{filename}"

        file.save(input_path)
        return input_path, filename, uid

    def save_to_database(self, filename, uid):
        db_path = path_config.get_database_path(self.module_name, filename)
        db.session.add(filesModel(db_path))
        db.session.commit()
        return db_path

    def download_file(self, relative_path):
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
        try:
            file_path = path_config.get_full_file_path(relative_path)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            return send_file(file_path)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def get_download_paths(self, uid, filename):
        directories = self.setup_directories()
        secure_name = secure_filename(filename)

        return {
            'downloads_path': directories['downloads_path'],
            'output_filename': f"{uid}{secure_name}",
            'output_path': f"{directories['downloads_path']}/{uid}{secure_name}"
        }