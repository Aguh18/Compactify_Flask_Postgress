from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from PIL import Image
from dotenv import dotenv_values
import uuid
import os


def imgtogray():
    form = imageForm()
    if request.method == "GET":
        return render_template("imgtogray/imgtograyform.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                
                
                env_values = dotenv_values(".env")
                project_Path = env_values["PATH"]+"app/static/imgToGray/"
                
                uid = str(uuid.uuid4())
                
                if not os.path.exists(project_Path):
                    os.makedirs(project_Path)
                if not os.path.exists(project_Path+"uploads/"):
                    os.makedirs(project_Path+"uploads/")
                if not os.path.exists(project_Path+"downloads/"):
                    os.makedirs(project_Path+"downloads/")
                
                file = request.files["file"]
                input_path = project_Path+"uploads/" +uid+ secure_filename(file.filename)
                file.save(input_path )
                output_path = project_Path+"downloads/"+uid + secure_filename(file.filename)
                
                img = Image.open(input_path).convert('L')
                img.save(output_path)
                file = "imgToGray/downloads/"+uid + secure_filename(file.filename)
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                return render_template("imgtogray/imgtograydownload.html", file = file)
            except Exception as e:
                return str(e)
        else:
            flash("File tidak valid")
            return redirect(request.url)
