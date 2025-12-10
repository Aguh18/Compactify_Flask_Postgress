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
base_controller = BaseController('wordToPDFController')
def wordToPDF():
    from flask import jsonify
    import tempfile

    if request.method == "GET":
        return render_template("docToPdf/docToPdfForm.html")
    elif request.method == "POST":
        try:
            file = request.files["file"]
            uid = str(uuid.uuid4())

            # Save to R2 storage
            input_key, filename, uid = base_controller.save_uploaded_file(file, uid)

            # Download file from R2 for processing
            from app.service.r2_helper import r2_helper
            input_result = r2_helper.download_file(input_key)

            if not input_result['success']:
                return jsonify({"error": "Failed to retrieve file from storage"}), 500

            # Create temporary files for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_input:
                tmp_input.write(input_result['file_obj'].read())
                temp_input_path = tmp_input.name

            temp_output_path = tempfile.mktemp(suffix='.pdf')

            # Process Word to PDF
            document = Document()
            document.LoadFromFile(temp_input_path)
            document.SaveToFile(temp_output_path, FileFormat.PDF)
            document.Close()

            # Create proper filename for converted file
            name, ext = os.path.splitext(filename)
            pdf_filename = f"{name}_converted.pdf"

            # Upload PDF to R2
            output_key = base_controller.save_processed_file(temp_output_path, pdf_filename, uid)

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(output_key, uid)
            print("file success created")
            # Return download page URL instead of direct file URL
            download_url = url_for('wordtopdf_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("docToPdf/docToPdfDownload.html", filename=filename, file=file)
def download_file(file):
    return base_controller.download_file(file)