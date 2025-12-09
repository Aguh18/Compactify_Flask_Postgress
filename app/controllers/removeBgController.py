import os
import uuid
from dotenv import dotenv_values
from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from PIL import Image
from werkzeug.utils import secure_filename
from app.config.database import db
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
from app.models.validate.imageValidation import imageForm
base_controller = BaseController('removeBgController')
def removeBg():
    from rembg import remove
    if request.method == "GET":
        return render_template("removeBackground/removeBgForm.html")
    elif request.method == "POST":
        try:
            env_values = dotenv_values(".env")
            project_Path = "/app/app/static/removeBackground/"
            uid = str(uuid.uuid4())
            if not os.path.exists(project_Path):
                os.makedirs(project_Path)
            if not os.path.exists(project_Path + "uploads/"):
                os.makedirs(project_Path + "uploads/")
            if not os.path.exists(project_Path + "downloads/"):
                os.makedirs(project_Path + "downloads/")
            file = request.files["file"]
            input_path = (
                project_Path + "uploads/" + uid + secure_filename(file.filename)
            )
            file.save(input_path)
            output_path = (
                project_Path
                + "downloads/"
                + uid
                + secure_filename(file.filename)
                + ".png"
            )
            input = Image.open(input_path)
            output = remove(input)
            output.save(output_path)
            file_db = (
                "removeBackground/downloads/"
                + uid
                + secure_filename(file.filename)
                + ".png"
            )
            base_controller.save_to_database(filename, uid)
            print("file success created")
            return render_template(
                "removeBackground/removeBgDownload.html", file=file_db
            )
        except Exception as e:
            return str(e)
def render_download_page(file):
    filename = os.path.basename(file)
    return render_template(
        "removeBackground/removeBgDownload.html", filename=filename, file=file
    )
def download_file(file):
    return base_controller.download_file(file)