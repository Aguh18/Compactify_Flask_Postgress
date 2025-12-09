from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.pdfValidation import pdfForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
import argparse
import os.path
import shutil
import subprocess
import sys
from dotenv import dotenv_values
import uuid
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
            env_values = dotenv_values(".env")
            directories = base_controller.setup_directories()
            file = request.files["file"]
            uid = str(uuid.uuid4())
            input_path, filename, uid = base_controller.save_uploaded_file(file, uid)
            paths = base_controller.get_download_paths(uid, filename)
            output_Path = paths['output_path']
            quality_map = {"high": 1, "medium": 2, "low": 3}
            power = quality_map.get(request.form.get("quality", "low"), 3)
            compress(input_path, output_path, power=power)
            compressed_filename = secure_filename(file.filename)
            file_db = base_controller.save_to_database(compressed_filename, uid)
            print("file succes created")
            download_url = url_for('compresspdf_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    return render_template("compressPdf/compresspdfDownload.html", file=file)
def download_file(file):
    return base_controller.download_file(file)