from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify, send_file
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
                
                
            file_db = "compressZip/downloads/"+uid+secure_filename(pathfile.filename)+".zip"
            db.session.add(filesModel(file_db))
            db.session.commit()
            create_zip(input_path, output_path)
            
            # Return download URL instead of direct template
            download_url = url_for('zip_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("zip/zipDownload.html", filename=filename, file=file)


def download_file(file):
    try:
        env_values = dotenv_values(".env")
        project_Path = env_values["PATH"]+"app/static/"
        file_path = project_Path + file
        
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found at {file_path}"}), 404
            
        filename = os.path.basename(file)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"compressed_{filename}",
            mimetype="application/zip"
        )
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": str(e)}), 400
    
   