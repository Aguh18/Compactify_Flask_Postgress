from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify, send_file
from app.models.validate.docValidation import docForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from spire.doc import *
from spire.doc.common import *
import os
import uuid
from dotenv import dotenv_values


def wordToPDF():
  
    if request.method == "GET":
        return render_template("docToPdf/docToPdfForm.html" )
    elif request.method == "POST":
       
            try:
                
                
                env_values = dotenv_values(".env")
                project_Path = "/app/app/static/docToPdf/"
            # Use path that matches docker-compose volume mount"
                
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
                output_path = project_Path+"downloads/"+uid + secure_filename(file.filename)+".pdf"
                file = request.files["file"]
              
                document = Document()
                document.LoadFromFile(input_path)
                # Or load a Word DOC file
                #document.LoadFromFile("Sample.doc")

                # Save the file to a PDF file
                document.SaveToFile(output_path, FileFormat.PDF)
                document.Close()
                file_db = "docToPdf/downloads/"+uid+secure_filename(file.filename)+".pdf"
                
                db.session.add(filesModel(file_db))
                db.session.commit()
                print("file success created")
                
                # Redirect to download page directly
                return render_template("docToPdf/docToPdfDownload.html", file=file_db)
            except Exception as e:
                print(e)
                return "Error"


def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("docToPdf/docToPdfDownload.html", filename=filename, file=file)


def download_file(file):
    try:
        env_values = dotenv_values(".env")
        project_Path = "/app/app/static/docToPdf/"
            # Use path that matches docker-compose volume mountpdf"
        )
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": str(e)}), 400

        
        
        
        
        

    