from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify, send_file
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
import os
import zipfile
from datetime import datetime, timedelta
from dotenv import dotenv_values
import uuid
base_controller = BaseController('zipController')
def create_zip(directory, zip_filename):
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for root, _, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, directory))
                print(f"File ZIP '{zip_filename}' telah berhasil dibuat.")
                return "sukses"    
def zip():
    import tempfile
    import shutil

    if request.method == "GET":
        return render_template("zip/zipForm.html")
    elif request.method == "POST":
        try:
            uid = str(uuid.uuid4())
            length = int(request.form.get("length", 0))

            if length == 0:
                return jsonify({"error": "No files selected"}), 400

            # Create temporary directory for files
            temp_dir = tempfile.mkdtemp()

            # Get files and save to R2 first
            from app.service.r2_helper import r2_helper
            file_keys = []

            for i in range(length):
                file_key = f"file[{i}]"
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename:
                        # Save to R2 storage
                        input_key, filename, file_uid = base_controller.save_uploaded_file(file, uid)
                        file_keys.append((input_key, filename))

            if not file_keys:
                return jsonify({"error": "No valid files provided"}), 400

            # Download all files from R2 for zipping
            for input_key, filename in file_keys:
                input_result = r2_helper.download_file(input_key)
                if input_result['success']:
                    file_path = os.path.join(temp_dir, secure_filename(filename))
                    with open(file_path, 'wb') as f:
                        f.write(input_result['file_obj'].read())

            # Create zip file
            temp_zip_path = tempfile.mktemp(suffix='.zip')
            create_zip(temp_dir, temp_zip_path)

            # Create proper filename for zip file
            original_filename = secure_filename(file_keys[0][1]) if file_keys else "files"
            name, ext = os.path.splitext(original_filename)
            zip_filename = f"{name}_compressed.zip" if ext else f"{original_filename}_compressed.zip"

            # Upload zip to R2
            output_key = base_controller.save_processed_file(temp_zip_path, zip_filename, uid)

            # Clean up temporary directory and zip file
            shutil.rmtree(temp_dir)
            os.unlink(temp_zip_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(output_key, uid)
            # Return download page URL instead of direct file URL
            download_url = url_for('zip_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error in zip: {e}")
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("zip/zipDownload.html", filename=filename, file=file)
def download_file(file):
    return base_controller.download_file(file)