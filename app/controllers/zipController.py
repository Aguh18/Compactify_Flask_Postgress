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


# Initialize base controller
base_controller = BaseController('zipController')

def create_zip(directory, zip_filename):
                # Membuka file ZIP dalam mode write
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    # Melakukan iterasi pada semua file dan direktori dalam direktori yang diberikan
                    for root, _, files in os.walk(directory):
                        for file in files:
                            # Mendapatkan path absolut file
                            file_path = os.path.join(root, file)
                            # Menambahkan file ke dalam ZIP
                            zipf.write(file_path, os.path.relpath(file_path, directory))

                print(f"File ZIP '{zip_filename}' telah berhasil dibuat.")
                return "sukses"    


def zip():
  
    if request.method == "GET":
        return render_template("zip/zipForm.html" )
    elif request.method == "POST":
        try:
            uid = str(uuid.uuid4())
            directories = base_controller.setup_directories()

            pathfile = request.files["file[0]"]

            # Create unique input directory
            input_dir = f"{directories['uploads_path']}/{uid}"
            os.makedirs(input_dir, exist_ok=True)

            # Get output path for zip file
            paths = base_controller.get_download_paths(uid, pathfile.filename + ".zip")
            output_path = paths['output_path']

            # Save all uploaded files
            for i in range(0, int(request.form["length"])):
                file = request.files["file["+ str(i) +"]"]
                file.save(os.path.join(input_dir, secure_filename(file.filename)))

            # Create zip file
            create_zip(input_dir, output_path)

            # Save to database
            zip_filename = uid + secure_filename(pathfile.filename) + ".zip"
            file_db = base_controller.save_to_database(zip_filename, uid)
            
            # Redirect to download page directly
            return render_template("zip/zipDownload.html", file=file_db)
        except Exception as e:
            return str(e)


def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("zip/zipDownload.html", filename=filename, file=file)


def download_file(file):
    """
    Download file using base controller
    """
    return base_controller.download_file(file)
    
   