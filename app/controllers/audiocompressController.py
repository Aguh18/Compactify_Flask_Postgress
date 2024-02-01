
from flask import  request, render_template, url_for, redirect, flash
from app.models.validate.AudioValidation import  Audioform
from werkzeug.utils import secure_filename 
from rembg import remove 
from app.config.database import db
from app.models.fileModel import filesModel
from PIL import Image 
import os









def CompressAudio():
    
    form = Audioform()
    if request.method == "GET":
        print("ini berjalan")
        return render_template("CompressAudio/CompressAudioForm.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                print("Ini jalan")
                file = request.files["file"]
                file.save("app/static/uploads/" + secure_filename(file.filename) )
                input_path = "app/static/uploads/" + secure_filename(file.filename)
                filename = secure_filename(file.filename)
                
               
                
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
        


