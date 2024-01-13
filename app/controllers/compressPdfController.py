from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.pdfValidation import pdfForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
import os
import sys
from PDFNetPython3.PDFNetPython import PDFDoc, Optimizer, SDFDoc, PDFNet











def compressPdf():
    form = pdfForm()
    if request.method == "GET":
        return render_template("compressPdf/compressPdfForm.html" , form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                file = request.files["file"]
                file.save("app/static/uploads/" + secure_filename(file.filename) )
                input_path = "app/static/uploads/" + secure_filename(file.filename)
                output_path = "app/static/compresspdf/" + secure_filename(file.filename)
                
                compressPdf(input_path, output_path)
               
                file = secure_filename(file.filename)
                
                db.session.add(filesModel(file))
                db.session.commit()
                print("file succes created")
                
                return render_template("compressPdf/compressPdfDownload.html", file = file)
            except Exception as e:
                print(e)
                return "Still Under Dveloptment"
        else:
            flash("File tidak valid")
            return redirect(request.url)
        
        
        
        


def compress_file(input_file, output_file):
    """Compress PDF file"""
    if not output_file:
        output_file = input_file
    
    try:
        # Initialize the library
        PDFNet.Initialize()
        doc = PDFDoc(input_file)
        # Optimize PDF with the default settings
        doc.InitSecurityHandler()
        # Reduce PDF size by removing redundant information and compressing data streams
        Optimizer.Optimize(doc)
        doc.Save(output_file, SDFDoc.e_linearized)
        doc.Close()
    except Exception as e:
        print("Error compress_file=", e)
        doc.Close()
      
    