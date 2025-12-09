from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify, send_file
from app.models.validate.docValidation import docForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
from spire.doc import *
from spire.doc.common import *
import os
import uuid
from dotenv import dotenv_values



# Initialize base controller
base_controller = BaseController('wordToPDFController')

def wordToPDF():
    if request.method == "GET":
        return render_template("docToPdf/docToPdfForm.html")
    elif request.method == "POST":
        try:
            uid = str(uuid.uuid4())
            directories = base_controller.setup_directories()

            file = request.files["file"]
            input_path, filename, uid = base_controller.save_uploaded_file(file, uid)
            paths = base_controller.get_download_paths(uid, filename + ".pdf")
            output_Path = paths['output_path']

            document = Document()
            document.LoadFromFile(input_path)

            # Save the file to a PDF file
            document.SaveToFile(output_Path, FileFormat.PDF)
            document.Close()

            pdf_filename = uid + secure_filename(file.filename) + ".pdf"
            file_db = base_controller.save_to_database(pdf_filename, uid)
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
    """
    Download file using base controller
    """
    return base_controller.download_file(file)

        
        
        
        
        

    