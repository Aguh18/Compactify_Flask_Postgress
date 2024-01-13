from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.docValidation import docForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from spire.doc import *
from spire.doc.common import *











def wordToPDF():
    form = docForm()
    if request.method == "GET":
        return render_template("docToPdf/docToPdfForm.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                file = request.files["file"]
                file.save("app/static/uploads/" + secure_filename(file.filename) )
                input_path = "app/static/uploads/" + secure_filename(file.filename)
                output_path = "app/static/wordtopdf/" + secure_filename(file.filename)+".pdf"
                document = Document()
                document.LoadFromFile(input_path)
                # Or load a Word DOC file
                #document.LoadFromFile("Sample.doc")

                # Save the file to a PDF file
                document.SaveToFile(output_path, FileFormat.PDF)
                document.Close()
                file = secure_filename(file.filename)+".pdf"
                
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                
                return render_template("docToPdf/docToPdfDownload.html", file = file)
            except Exception as e:
                print(e)
                return "Error"
        else:
            flash("File tidak valid")
            return redirect(request.url)
        
        
        
        
        

    