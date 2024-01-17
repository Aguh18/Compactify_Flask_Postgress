from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
import os
import zipfile
from datetime import datetime, timedelta






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
            # Mengambil waktu saat ini
            now = datetime.now()
  
            pathfile = request.files["file[0]"]
            input_path = "/home/guhh/Documents/All project/mvc-flask-master/app/static/uploads/zip/"+secure_filename(pathfile.filename)+str(now)
            os.mkdir(input_path)
            output_path = "/home/guhh/Documents/All project/mvc-flask-master/app/static/zip/"+secure_filename(pathfile.filename)+".zip"
            
            for i in range(0, int(request.form["length"])):
                file = request.files["file["+ str(i) +"]"]
                file.save(input_path+"/" + secure_filename(file.filename))
                
                
            file = secure_filename(pathfile.filename)+".zip"
            create_zip(input_path, output_path)
            return render_template("zip/zipDownload.html", file = file)
        except Exception as e:
           
            return str(e)
    
   