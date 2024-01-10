from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.fileValidate import RemoveBgForm

from werkzeug.utils import secure_filename 

from rembg import remove 
from PIL import Image 







def removeBg():
    form = RemoveBgForm()
    if request.method == "GET":
        return render_template("removeBackground/form.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                file = request.files["file"]
                file.save("app/static/uploads/" + secure_filename(file.filename) )
                input_path = "app/static/uploads/" + secure_filename(file.filename)
                output_path = "app/static/Removebg/" + secure_filename(file.filename)+".png"
                input = Image.open(input_path) 
                output = remove(input) 
                output.save(output_path) 
                file = secure_filename(file.filename)+".png"
                print("file succes created")
                
                return render_template("removeBackground/download.html", file = file)
            except Exception as e:
                print(e)
                return "Error"
        else:
            flash("File tidak valid")
            return redirect(request.url)
