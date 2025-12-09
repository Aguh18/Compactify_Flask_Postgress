
from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.pdfValidation import pdfForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
import argparse
import os.path
import shutil
import subprocess
import sys
from dotenv import dotenv_values
import uuid

def compress(input_file_path, output_file_path, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file.", input_file_path)
        sys.exit(1)

    # Check compression level
    if power < 0 or power > len(quality) - 1:
        print("Error: invalid compression level, run pdfc -h for options.", power)
        sys.exit(1)

    # Check if file is a PDF by extension
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
            env_values = dotenv_values(".env")
            project_Path = "." 
            # Use relative path instead of PATH from .env+"app/static/compressPdf/"
            uid = str(uuid.uuid4())
            if not os.path.exists(project_Path):
                os.makedirs(project_Path)
            if not os.path.exists(project_Path+"uploads/"):
                os.makedirs(project_Path+"uploads/")
            if not os.path.exists(project_Path+"downloads/"):
                os.makedirs(project_Path+"downloads/")
            file = request.files["file"]
            input_path = project_Path+"uploads/" +uid+ secure_filename(file.filename)
            file.save(input_path)
            output_path = project_Path+"downloads/"+uid + secure_filename(file.filename)

            # Ambil level kompresi dari form (default: 3/ebook)
            quality_map = {"high": 1, "medium": 2, "low": 3}
            power = quality_map.get(request.form.get("quality", "low"), 3)
            compress(input_path, output_path, power=power)

            file_db = "compressPdf/downloads/"+uid+secure_filename(file.filename)
            db.session.add(filesModel(file_db))
            db.session.commit()
            print("file succes created")

            # Kembalikan URL halaman download (bukan file langsung)
            download_url = url_for('compresspdf_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400


def render_download_page(file):
    return render_template("compressPdf/compresspdfDownload.html", file=file)


def download_file(file):
    from flask import send_file, jsonify
    import os
    from dotenv import dotenv_values
    
    try:
        env_values = dotenv_values(".env")
        project_Path = "." 
            # Use relative path instead of PATH from .env+"app/static/"
        file_path = project_Path + file
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
            
        filename = os.path.basename(file)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"compressed_{filename}",
            mimetype="application/pdf"
        )
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400