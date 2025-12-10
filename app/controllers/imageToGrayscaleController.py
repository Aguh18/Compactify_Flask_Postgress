from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
try:
    from PIL import Image
except ImportError:
    import Image
from dotenv import dotenv_values
import uuid
import os
import traceback
base_controller = BaseController('imageToGrayscaleController')
def imgtogray():
    from flask import jsonify
    import tempfile

    if request.method == "GET":
        return render_template("imgtogray/imgtograyform.html")
    elif request.method == "POST":
        try:
            print("POST request received")
            if 'file' not in request.files:
                print("No file in request")
                return jsonify({"error": "No file uploaded"}), 400
            file = request.files["file"]
            if file.filename == '':
                print("Empty filename")
                return jsonify({"error": "No file selected"}), 400
            print(f"File received: {file.filename}")

            uid = str(uuid.uuid4())

            # Save to R2 storage
            input_key, filename, uid = base_controller.save_uploaded_file(file, uid)
            print(f"File saved to R2 with key: {input_key}")

            # Download file from R2 for processing
            from app.service.r2_helper import get_r2_helper
            input_result = get_r2_helper().download_file(input_key)

            if not input_result['success']:
                return jsonify({"error": "Failed to retrieve file from storage"}), 500

            # Create temporary files for processing
            with tempfile.NamedTemporaryFile(delete=False) as tmp_input:
                tmp_input.write(input_result['file_obj'].read())
                temp_input_path = tmp_input.name

            temp_output_path = tempfile.mktemp(suffix='_grayscale.jpg')

            # Process image to grayscale
            img = Image.open(temp_input_path).convert('L')
            img.save(temp_output_path)
            print(f"Grayscale image saved to: {temp_output_path}")

            # Create proper filename for processed file
            name, ext = os.path.splitext(filename)
            processed_filename = f"{name}_grayscale.jpg"

            # Upload grayscale image to R2
            output_key = base_controller.save_processed_file(temp_output_path, processed_filename, uid)

            # Calculate file sizes
            original_size = os.path.getsize(temp_input_path)
            compressed_size = os.path.getsize(temp_output_path)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(
                output_key, 
                uid,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio
            )
            print("file success created")
            # Return download page URL instead of direct file URL
            download_url = url_for('imgtogray_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500
def render_download_page(file):
    from app.models.fileModel import filesModel
    from app.config.database import db

    # Get file record from database
    file_record = db.session.query(filesModel).filter_by(file=file).first()
    
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

    return render_template("imgtogray/imgtograydownload.html", 
                         file=file,
                         file_record=file_record,
                         format_size=format_size)
def download_file(file):
    return base_controller.download_file(file)
def preview_file(file):
    return base_controller.preview_file(file)