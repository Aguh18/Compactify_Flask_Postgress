from flask import Blueprint, request, render_template, url_for, redirect
from werkzeug.utils import secure_filename 
from rembg import remove 
from PIL import Image 




def removeBg():
    if request.method == "GET":
        return render_template("removeBackground/form.html")
    elif request.method == "POST":
        try:
            file = request.files["file"]
            file.save("app/static/uploads/" + secure_filename(file.filename) )
            input_path = "app/static/uploads/" + secure_filename(file.filename)
            print(input_path)
            output_path = "app/static/Removebg/" + secure_filename(file.filename)+".png"
            input = Image.open(input_path) 
            output = remove(input) 
            output.save(output_path) 
            file = secure_filename(file.filename)+".png"
            
            return render_template("removeBackground/download.html", file = file)
        except Exception as e:
            print(e)
            return "Error"
