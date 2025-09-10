from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify, send_file
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
                file_db = "removeBackground/downloads/"+uid+secure_filename(file.filename)+".png"
                db.session.add(filesModel(file_db))
                db.session.commit()
                print("file success created")
                
                # Return download URL instead of direct template
                download_url = url_for('removebg_download', file=file_db)
                return jsonify({"download_url": download_url})
            except Exception as e:
                return jsonify({"error": str(e)}), 500


def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("removeBackground/removeBgDownload.html", filename=filename, file=file)


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
            download_name=f"no_bg_{filename}",
            mimetype="image/png"
        )
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": str(e)}), 400
