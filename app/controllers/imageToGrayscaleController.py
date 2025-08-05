from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
try:
    from PIL import Image
except ImportError:
    import Image
from dotenv import dotenv_values
import uuid
import os
import traceback


def imgtogray():
    if request.method == "GET":
        return render_template("imgtogray/imgtograyform.html" )
    elif request.method == "POST":
            try:
                print("POST request received")
                
                # Check if file exists in request
                if 'file' not in request.files:
                    print("No file in request")
                    return "No file uploaded", 400
                
                file = request.files["file"]
                if file.filename == '':
                    print("Empty filename")
                    return "No file selected", 400
                
                print(f"File received: {file.filename}")
                
                env_values = dotenv_values(".env")
                project_Path = env_values["PATH"]+"app/static/imgToGray/"
                print(f"Project path: {project_Path}")
                
                uid = str(uuid.uuid4())
                
                if not os.path.exists(project_Path):
                    os.makedirs(project_Path)
                if not os.path.exists(project_Path+"uploads/"):
                    os.makedirs(project_Path+"uploads/")
                if not os.path.exists(project_Path+"downloads/"):
                    os.makedirs(project_Path+"downloads/")
                
                input_path = project_Path+"uploads/" +uid+ secure_filename(file.filename)
                file.save(input_path )
                print(f"File saved to: {input_path}")
                
                output_path = project_Path+"downloads/"+uid + secure_filename(file.filename)
                
                img = Image.open(input_path).convert('L')
                img.save(output_path)
                print(f"Grayscale image saved to: {output_path}")
                
                file_path = "imgToGray/downloads/"+uid + secure_filename(file.filename)
                db.session.add(filesModel(file_path))
                db.session.commit()
                print("file success created")
                print(f"Redirecting to download page with file: {file_path}")
                return render_template("imgtogray/imgtograydownload.html", file = file_path)
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                print(f"Error traceback: {traceback.format_exc()}")
                return f"Error processing image: {str(e)}", 500

