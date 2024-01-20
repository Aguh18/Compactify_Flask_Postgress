from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from rembg import remove 
from PIL import Image 







def removeBg():
    form = imageForm()
    if request.method == "GET":
        return render_template("removeBackground/removeBgForm.html" , form = form)
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
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                return render_template("removeBackground/removeBgDownload.html", file = file)
            except Exception as e:
                return str(e)
        else:
            flash("File tidak valid")
            return redirect(request.url)
