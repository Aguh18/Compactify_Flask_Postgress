from flask import Blueprint, request, render_template, url_for, redirect, flash, jsonify
from app.models.validate.docValidation import docForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
from spire.doc import *
from spire.doc.common import *
import os
import uuid
import tempfile
from dotenv import dotenv_values

base_controller = BaseController('wordToPDFController')

def wordToPDF():
    if request.method == "GET":
        return render_template("docToPdf/docToPdfForm.html")
    elif request.method == "POST":
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file uploaded"}), 400
                
            file = request.files["file"]
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
                
            uid = str(uuid.uuid4())
            
            # Save to R2 storage
            input_key, filename, uid = base_controller.save_uploaded_file(file, uid)

            # Download file from R2 for processing
            from app.service.r2_helper import get_r2_helper
            input_result = get_r2_helper().download_file(input_key)

            if not input_result['success']:
                return jsonify({"error": "Failed to retrieve file from storage"}), 500

            # Create temporary files
            # Determine extension from filename
            ext = os.path.splitext(filename)[1]
            if not ext:
                ext = '.doc' # Default fallback
                
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_input:
                tmp_input.write(input_result['file_obj'].read())
                temp_input_path = tmp_input.name
                
            temp_output_path = tempfile.mktemp(suffix='.pdf')

            # Process Word to PDF
            document = Document()
            document.LoadFromFile(temp_input_path)
            document.SaveToFile(temp_output_path, FileFormat.PDF)
            document.Close()

            # Upload PDF to R2
            name = os.path.splitext(filename)[0]
            output_filename = f"{name}.pdf"
            output_key = base_controller.save_processed_file(temp_output_path, output_filename, uid)

            # Calculate sizes
            original_size = os.path.getsize(temp_input_path)
            compressed_size = os.path.getsize(temp_output_path)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            # Clean up
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)
            
            # Save to database
            file_db = base_controller.save_to_database(
                output_key, 
                uid,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio
            )
            print("file success created")
            
            # Return download page URL
            download_url = url_for('wordtopdf_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error in wordToPDF: {e}")
            return jsonify({"error": str(e)}), 500

def render_download_page(file):
    from app.models.fileModel import filesModel
    
    # Get file record from database
    file_record = db.session.query(filesModel).filter_by(file=file).first()
    
    filename = os.path.basename(file)
    
    # Format file sizes for display
    def format_size(bytes):
        if not bytes:
            return "0 Bytes"
        sizes = ["Bytes", "KB", "MB", "GB"]
        i = 0
        while bytes >= 1024 and i < len(sizes) - 1:
            bytes /= 1024.0
            i += 1
        return f"{bytes:.2f} {sizes[i]}"
        
    return render_template("docToPdf/docToPdfDownload.html", 
                         filename=filename, 
                         file=file,
                         file_record=file_record,
                         format_size=format_size)

def download_file(file):
    return base_controller.download_file(file)
        
        
        
        
        

    