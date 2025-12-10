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
            from app.service.r2_helper import get_r2_helper
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
                input_result = get_r2_helper().download_file(input_key)
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

            # Calculate sizes
            # 1. Calculate original size (sum of all input files)
            original_size = 0
            for root, _, files in os.walk(temp_dir):
                for file in files:
                     original_size += os.path.getsize(os.path.join(root, file))
            
            # 2. Calculate compressed size
            compressed_size = os.path.getsize(temp_zip_path)
            
            # 3. Calculate ratio
            if original_size > 0:
                compression_ratio = round((1 - compressed_size / original_size) * 100, 2)
            else:
                compression_ratio = 0.0

            # Clean up temporary directory and zip file
            shutil.rmtree(temp_dir)
            os.unlink(temp_zip_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(
                output_key, 
                uid,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio
            )
            # Return download page URL instead of direct file URL
            download_url = url_for('zip_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error in zip: {e}")
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    from app.models.fileModel import filesModel
    from app.config.database import db

    # Get file record from database
    file_record = db.session.query(filesModel).filter_by(file=file).first()
    
    filename = os.path.basename(file)
    
    # Format file sizes for display
    def format_size(bytes):
        if not bytes:
            return "0 Bytes"
        sizes = ["Bytes", "KB", "MB", "GB"]
        i = 0
        while bytes >= 1024 and i < len(sizes) - 1:
            bytes /= 1024.0
            i += 1
        return f"{bytes:.2f} {sizes[i]}"

    return render_template("zip/zipDownload.html", 
                         filename=filename, 
                         file=file,
                         file_record=file_record,
                         format_size=format_size)
def download_file(file):
    return base_controller.download_file(file)