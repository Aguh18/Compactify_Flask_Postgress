from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from PIL import Image







def imgtogray():
    form = imageForm()
    if request.method == "GET":
        return render_template("imgtogray/imgtograyform.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                file = request.files["file"]
                file.save("app/static/uploads/" + secure_filename(file.filename) )
                input_path = "app/static/uploads/" + secure_filename(file.filename)
                output_path = "app/static/imgtograyscale/" + secure_filename(file.filename)
                img = Image.open(input_path).convert('L')
                img.save(output_path)
                file = secure_filename(file.filename)
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                return render_template("imgtogray/imgtograydownload.html", file = file)
            except Exception as e:
                return str(e)
        else:
            flash("File tidak valid")
            return redirect(request.url)
