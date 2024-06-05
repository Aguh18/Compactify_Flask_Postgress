from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
import os
import zipfile
from datetime import datetime, timedelta
from dotenv import dotenv_values
import uuid

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
            env_values = dotenv_values(".env")
            project_Path = env_values["PATH"]+"app/static/compressZip/"
            uid = str(uuid.uuid4())
            
            if not os.path.exists(project_Path):
                os.makedirs(project_Path)
            if not os.path.exists(project_Path+"uploads/"):
                os.makedirs(project_Path+"uploads/")
            if not os.path.exists(project_Path+"downloads/"):
                os.makedirs(project_Path+"downloads/")
  
            pathfile = request.files["file[0]"]
            input_path = project_Path+"uploads/"+uid+secure_filename(pathfile.filename)
            os.mkdir(input_path)
            output_path = project_Path+"downloads/"+uid+secure_filename(pathfile.filename)+".zip"
            
            for i in range(0, int(request.form["length"])):
                file = request.files["file["+ str(i) +"]"]
                file.save(input_path+"/" + secure_filename(file.filename))
                
                
            file = "compressZip/downloads/"+uid+secure_filename(pathfile.filename)+".zip"
            db.session.add(filesModel(file))
            db.session.commit()
            create_zip(input_path, output_path)
            return render_template("zip/zipDownload.html", file = file)
        except Exception as e:
           
            return str(e)
    
   