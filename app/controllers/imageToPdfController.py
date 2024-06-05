from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
import img2pdf
from PIL import Image
import os
from dotenv import dotenv_values
import uuid









def imageTopdf():
    form = imageForm()
    if request.method == "GET":
        return render_template("imagetopdf/imageToPdfForm.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                
                env_values = dotenv_values(".env")
                project_Path = env_values["PATH"]+"app/static/imageToPdf/"
                
               
                
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
                output_path = project_Path+"downloads/"+uid + secure_filename(file.filename)+".pdf"
                
                
                image = Image.open(input_path)
                pdf_bytes = img2pdf.convert(image.filename)
                pdf = open(output_path, "wb")
                
                # writing pdf pdfs with chunks
                pdf.write(pdf_bytes)
                
                # closing image pdf
                image.close()
                
                # closing pdf pdf
                pdf.close()
                
                # output
                print("Successfully made pdf file")
                            
                file = "imageToPdf/downloads/"+uid+secure_filename(file.filename)+".pdf"
                
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                
                return render_template("imagetopdf/imageToPdfDownload.html", file = file)
            except Exception as e:
                print(e)
                return "Error"
        else:
            flash("File tidak valid")
            return redirect(request.url)
        
        
        
        
        

    