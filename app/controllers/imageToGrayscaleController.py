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



# Initialize base controller
base_controller = BaseController('imageToGrayscaleController')

def imgtogray():
    from flask import jsonify
    if request.method == "GET":
        return render_template("imgtogray/imgtograyform.html" )
    elif request.method == "POST":
            try:
                print("POST request received")
                
                # Check if file exists in request
                if 'file' not in request.files:
                    print("No file in request")
                    return jsonify({"error": "No file uploaded"}), 400
                
                file = request.files["file"]
                if file.filename == '':
                    print("Empty filename")
                    return jsonify({"error": "No file selected"}), 400
                
                print(f"File received: {file.filename}")
                
                env_values = dotenv_values(".env")
                directories = base_controller.setup_directories()
                
                input_path = base_controller.get_uploads_path(base_controller.module_name) + "/" + uid + secure_filename(file.filename)
                file.save(input_path )
                print(f"File saved to: {input_path}")
                
                paths = base_controller.get_download_paths(uid, filename)
                output_Path = paths['output_path']
                
                img = Image.open(input_path).convert('L')
                img.save(output_path)
                print(f"Grayscale image saved to: {output_path}")
                
                processed_filename = uid + secure_filename(file.filename)
                file_db = base_controller.save_to_database(processed_filename, uid)
                print("file success created")
                print(f"Redirecting to download page with file: {file_db}")
                
                # Kembalikan URL halaman download (bukan file langsung)
                download_url = url_for('imgtogray_download', file=file_db)
                return jsonify({"download_url": download_url})
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                print(f"Error traceback: {traceback.format_exc()}")
                return jsonify({"error": f"Error processing image: {str(e)}"}), 500


def render_download_page(file):
    return render_template("imgtogray/imgtograydownload.html", file=file)


def download_file(file):
    """
    Download file using base controller
    """
    return base_controller.download_file(file)


def preview_file(file):
    """
    Preview file using base controller
    """
    return base_controller.preview_file(file)

