from flask import Blueprint, request, render_template, url_for, redirect, flash
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
    form = docForm()
    if request.method == "GET":
        return render_template("docToPdf/docToPdfForm.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                
                
                env_values = dotenv_values(".env")
                project_Path = env_values["PATH"]+"app/static/wortToPdf/"
                
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
                file = "wortToPdf/downloads/"+uid+secure_filename(file.filename)+".pdf"
                
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                
                return render_template("docToPdf/docToPdfDownload.html", file = file)
            except Exception as e:
                print(e)
                return "Error"
        else:
            flash("File tidak valid")
            return redirect(request.url)
        
        
        
        
        

    