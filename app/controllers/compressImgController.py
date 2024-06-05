
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









def imageCompress():
    
    form = imageForm()
    if request.method == "GET":
        return render_template("CompressImg/comressImgForm.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                env_values = dotenv_values(".env")
                project_Path = env_values["PATH"]+"app/static/compressImg/"
                
               
                
                if not os.path.exists(project_Path):
                    os.makedirs(project_Path)
                if not os.path.exists(project_Path+"uploads/"):
                    os.makedirs(project_Path+"uploads/")
                if not os.path.exists(project_Path+"downloads/"):
                    os.makedirs(project_Path+"downloads/")
                
                uid = str(uuid.uuid4())
                    
                file = request.files["file"]
                input_path = project_Path+"uploads/" +uid+ secure_filename(file.filename)
                file.save(input_path )
                output_Path = project_Path +"downloads/"
               
                filename = secure_filename(file.filename)
                
                file = compress_img(filename,input_path, output_Path,uid, new_size_ratio=0.5, quality=50, width=None, height=None, to_jpg=True)
                file = "compressImg/downloads/"+file
                print("nama file adalah", file)
                
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                
                return render_template("CompressImg/compressImgDownload.html", file = file)
            except Exception as e:
                print("Ini ada eror")
                print(e)
                return str(e)
        else:
            flash("File tidak valid")
            return redirect(request.url)
        


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
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.ANTIALIAS)
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
        img.save(output_path+uid+secure_filename(new_filename)
                , quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save( output_path+uid+secure_filename(new_filename), quality=quality, optimize=True)
   
    return uid+secure_filename(new_filename)
