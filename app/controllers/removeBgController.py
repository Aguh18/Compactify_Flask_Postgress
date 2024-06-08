from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from rembg import remove 
from PIL import Image 
import os
import uuid
from dotenv import dotenv_values







def removeBg():
   
    if request.method == "GET":
        return render_template("removeBackground/removeBgForm.html" )
    elif request.method == "POST":

            try:
                env_values = dotenv_values(".env")
                project_Path = env_values["PATH"]+"app/static/removeBackground/"
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
                output_path = project_Path+"downloads/"+uid + secure_filename(file.filename)+".png"
                
                input = Image.open(input_path) 
                output = remove(input) 
                output.save(output_path) 
                file = "removeBackground/downloads/"+uid+secure_filename(file.filename)+".png"
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                return render_template("removeBackground/removeBgDownload.html", file = file)
            except Exception as e:
                return str(e)
