
from flask import  request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from werkzeug.utils import secure_filename 
from rembg import remove 
from app.config.database import db
from app.models.fileModel import filesModel
from PIL import Image 
import os
import uuid
from dotenv import dotenv_values

# Handle PIL version compatibility
try:
    # For Pillow >= 10.0.0
    RESAMPLING_FILTER = Image.LANCZOS
except AttributeError:
    # For older Pillow versions
    RESAMPLING_FILTER = Image.ANTIALIAS









def imageCompress():
    from flask import jsonify
    form = imageForm()
    if request.method == "GET":
        return render_template("CompressImg/comressImgForm.html" , form = form)
    elif request.method == "POST":
        try:
            env_values = dotenv_values(".env")
            # Use path that matches docker-compose volume mount
            project_Path = "/app/app/static/CompressImg/"
            
            if not os.path.exists(project_Path):
                os.makedirs(project_Path)
            if not os.path.exists(project_Path+"uploads/"):
                os.makedirs(project_Path+"uploads/")
            if not os.path.exists(project_Path+"downloads/"):
                os.makedirs(project_Path+"downloads/")
            
            uid = str(uuid.uuid4())
            
            file = request.files["file"]
            input_path = project_Path+"uploads/" +uid+ secure_filename(file.filename)
            file.save(input_path)
            output_Path = project_Path +"downloads/"
           
            filename = secure_filename(file.filename)
            
            # Get quality parameter from form
            quality_level = request.form.get('quality', 'medium')
            
            # Set compression parameters based on quality level
            if quality_level == 'high':
                quality = 85
                new_size_ratio = 0.9
            elif quality_level == 'low':
                quality = 30
                new_size_ratio = 0.7
            else:  # medium/balanced
                quality = 60
                new_size_ratio = 0.8
            
            compressed_filename = compress_img(filename,input_path, output_Path,uid, new_size_ratio=new_size_ratio, quality=quality, width=None, height=None, to_jpg=True)
            file_db = "CompressImg/downloads/"+compressed_filename
            print("nama file adalah", file_db)
            
            db.session.add(filesModel(file_db))
            db.session.commit()
            print("file succes created")
            
            # Kembalikan URL halaman download (bukan file langsung)
            download_url = url_for('compressimg_download', file=file_db)
            return jsonify({"download_url": download_url})
        except Exception as e:
            print("Ini ada eror")
            print(e)
            return jsonify({"error": str(e)}), 400


def render_download_page(file):
    return render_template("CompressImg/compressImgDownload.html", file=file)


def download_file(file):
    from flask import send_file, jsonify
    import os
    from dotenv import dotenv_values
    
    try:
        # Use correct path that matches docker-compose volume
        file_path = "/app/" + file
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
            
        filename = os.path.basename(file)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"compressed_{filename}",
            mimetype="image/jpeg"
        )
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def compress_img(filename,input_path,output_path,uid, new_size_ratio=0.9, quality=50, width=None, height=None, to_jpg=True):
    # load the image to memory
    img = Image.open(input_path)
    # print the original image shape
    print("[*] Image shape:", img.size)
    # get the original image size in bytes
    image_size = os.path.getsize(input_path)
    # print the size before compression/resizing
    print("[*] Size before compression:", get_size_format(image_size))
    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), RESAMPLING_FILTER)
        # print new image shape
        print("[+] New Image shape:", img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), RESAMPLING_FILTER)
        # print new image shape
        print("[+] New Image shape:", img.size)
    # split the filename and extension
    filename, ext = os.path.splitext(filename)
    # make new filename appending _compressed to the original file name
    if to_jpg:
        # change the extension to JPEG
        new_filename = f"{filename}_compressed.jpg"
    else:
        # retain the same extension of the original image
        new_filename = f"{filename}_compressed{ext}"
    try:
        # save the image with the corresponding quality and optimize set to True
        output_file_path = output_path+uid+secure_filename(new_filename)
        img.save(output_file_path, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        output_file_path = output_path+uid+secure_filename(new_filename)
        img.save(output_file_path, quality=quality, optimize=True)
    
    # get the size after compression
    new_image_size = os.path.getsize(output_file_path)
    print("[*] Size after compression:", get_size_format(new_image_size))
    
    # calculate compression ratio
    compression_ratio = (1 - new_image_size / image_size) * 100
    print(f"[*] Compression ratio: {compression_ratio:.2f}%")
   
    return uid+secure_filename(new_filename)
