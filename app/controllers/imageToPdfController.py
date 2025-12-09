from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
import img2pdf
from PIL import Image
import os
from dotenv import dotenv_values
import uuid
base_controller = BaseController('imageToPdfController')
def imageTopdf():
    from flask import jsonify
    if request.method == "GET":
        return render_template("imagetopdf/imageToPdfForm.html" )
    elif request.method == "POST":
        try:
            env_values = dotenv_values(".env")
            directories = base_controller.setup_directories()
            uid = str(uuid.uuid4())
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({"error": "No files selected"}), 400
            image_paths = []
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    input_path = project_Path+"uploads/" + uid + "_" + filename
                    file.save(input_path)
                    image_paths.append(input_path)
            output_filename = f"converted_images_{uid}.pdf"
            paths = base_controller.get_download_paths(uid, filename)
            output_Path = paths['output_path']
            pdf_bytes = img2pdf.convert(image_paths)
            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)
            print("Successfully created PDF file")
            for img_path in image_paths:
                try:
                    os.remove(img_path)
                except:
                    pass
            file_db = "imagetopdf/downloads/" + output_filename
            base_controller.save_to_database(filename, uid)
            print("file success created")
            download_url = url_for('imagetopdf_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("imagetopdf/download.html", filename=filename, file=file)
def download_file(file):
    return base_controller.download_file(file)