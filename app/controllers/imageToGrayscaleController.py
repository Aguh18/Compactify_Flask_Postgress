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
            from app.service.r2_helper import r2_helper
            input_result = r2_helper.download_file(input_key)

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

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(output_key, uid)
            print("file success created")
            # Return download page URL instead of direct file URL
            download_url = url_for('imgtogray_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500
def render_download_page(file):
    return render_template("imgtogray/imgtograydownload.html", file=file)
def download_file(file):
    return base_controller.download_file(file)
def preview_file(file):
    return base_controller.preview_file(file)