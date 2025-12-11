from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.pdfValidation import pdfForm
from app.config.database import db
from werkzeug.utils import secure_filename
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
import argparse
import os
import shutil
import subprocess
import sys
from dotenv import dotenv_values
import uuid
import tempfile
base_controller = BaseController('compressPdfController')
def compress(input_file_path, output_file_path, power=0):
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file.", input_file_path)
        sys.exit(1)
    if power < 0 or power > len(quality) - 1:
        print("Error: invalid compression level, run pdfc -h for options.", power)
        sys.exit(1)
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print(f"Error: input file is not a PDF.", input_file_path)
        sys.exit(1)
    gs = get_ghostscript_path()
    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality[power]),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(output_file_path),
            input_file_path,
        ]
    )
def get_ghostscript_path():
    gs_names = ["gs", "gswin32", "gswin64"]
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(
        f"No GhostScript executable was found on path ({'/'.join(gs_names)})"
    )
def compressPdf():
    from flask import send_file, jsonify

    if request.method == "GET":
        return render_template("compressPdf/compressPdfForm.html")
    elif request.method == "POST":
        try:
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

            # Create temporary files for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
                tmp_input.write(input_result['file_obj'].read())
                temp_input_path = tmp_input.name

            temp_output_path = tempfile.mktemp(suffix='_compressed.pdf')

            # Process PDF
            quality_map = {"high": 1, "medium": 2, "low": 3}
            power = quality_map.get(request.form.get("quality", "low"), 3)
            compress(temp_input_path, temp_output_path, power=power)

            # Upload compressed file to R2
            name, ext = os.path.splitext(filename)
            compressed_filename = f"{name}_compressed{ext}"
            output_key = base_controller.save_processed_file(temp_output_path, compressed_filename, uid)

            # Calculate file sizes
            original_size = os.path.getsize(temp_input_path)
            compressed_size = os.path.getsize(temp_output_path)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            # Force garbage collection before saving to database
            import gc
            gc.collect()

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(
                output_key,
                uid,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio
            )
            print("file success created")

            # Final garbage collection to free all memory
            gc.collect()

            # Return download page URL instead of direct file URL
            download_url = url_for('compresspdf_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    from app.models.fileModel import filesModel
    from app.config.database import db

    # Get file record from database
    file_record = db.session.query(filesModel).filter_by(file=file).first()
    
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

    return render_template(
        "compressPdf/compresspdfDownload.html", 
        file=file,
        file_record=file_record,
        format_size=format_size
    )
def download_file(file):
    return base_controller.download_file(file)