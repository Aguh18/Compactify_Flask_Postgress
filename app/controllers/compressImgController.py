from flask import request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from werkzeug.utils import secure_filename
from rembg import remove
from app.config.database import db
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
from PIL import Image
import os
import uuid
from dotenv import dotenv_values
base_controller = BaseController('compressImgController')

try:
    RESAMPLING_FILTER = Image.LANCZOS
except AttributeError:
    RESAMPLING_FILTER = Image.ANTIALIAS

def imageCompress():
    from flask import jsonify
    form = imageForm()
    if request.method == "GET":
        return render_template("CompressImg/comressImgForm.html" , form = form)
    elif request.method == "POST":
        try:
            uid = str(uuid.uuid4())
            file = request.files["file"]
            input_path, filename, uid = base_controller.save_uploaded_file(file, uid)
            paths = base_controller.get_download_paths(uid, filename)
            output_Path = paths['output_path']
            quality_level = request.form.get('quality', 'medium')
            if quality_level == 'high':
                quality = 85
                new_size_ratio = 0.9
            elif quality_level == 'low':
                quality = 30
                new_size_ratio = 0.7
            else:
                quality = 60
                new_size_ratio = 0.8
            compressed_filename = compress_img(filename, input_path, output_Path, new_size_ratio=new_size_ratio, quality=quality, width=None, height=None, to_jpg=True)
            file_db = base_controller.save_to_database(compressed_filename, uid)
            print("nama file adalah", file_db)
            print("file succes created")
            download_url = url_for('compressimg_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            print("Ini ada eror")
            print(e)
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    return render_template("CompressImg/compressImgDownload.html", file=file)
def download_file(file):
    return base_controller.download_file(file)

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"
def compress_img(filename, input_path, output_path, new_size_ratio=0.9, quality=50, width=None, height=None, to_jpg=True):
    img = Image.open(input_path)
    print("[*] Image shape:", img.size)
    image_size = os.path.getsize(input_path)
    print("[*] Size before compression:", get_size_format(image_size))
    if new_size_ratio < 1.0:
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), RESAMPLING_FILTER)
        print("[+] New Image shape:", img.size)
    elif width and height:
        img = img.resize((width, height), RESAMPLING_FILTER)
        print("[+] New Image shape:", img.size)
    filename, ext = os.path.splitext(filename)
    if to_jpg:
        new_filename = f"{filename}_compressed.jpg"
    else:
        new_filename = f"{filename}_compressed{ext}"
    try:
        output_file_path = output_path + secure_filename(new_filename)
        img.save(output_file_path, quality=quality, optimize=True)
    except OSError:
        img = img.convert("RGB")
        output_file_path = output_path + secure_filename(new_filename)
        img.save(output_file_path, quality=quality, optimize=True)
    new_image_size = os.path.getsize(output_file_path)
    print("[*] Size after compression:", get_size_format(new_image_size))
    compression_ratio = (1 - new_image_size / image_size) * 100
    print(f"[*] Compression ratio: {compression_ratio:.2f}%")
    return secure_filename(new_filename)