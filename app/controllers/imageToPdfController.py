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
    from flask import jsonify
    if request.method == "GET":
        return render_template("imagetopdf/imageToPdfForm.html" )
    elif request.method == "POST":
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
            
            # Handle multiple files
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({"error": "No files selected"}), 400
            
            # Save all uploaded images
            image_paths = []
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    input_path = project_Path+"uploads/" + uid + "_" + filename
                    file.save(input_path)
                    image_paths.append(input_path)
            
            # Create PDF with orientation
            output_filename = f"converted_images_{uid}.pdf"
            output_path = project_Path+"downloads/" + output_filename
            
            # Convert images to PDF
            pdf_bytes = img2pdf.convert(image_paths)
            
            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)
            
            print("Successfully created PDF file")
            
            # Clean up uploaded images
            for img_path in image_paths:
                try:
                    os.remove(img_path)
                except:
                    pass
                    
            file_db = "imageToPdf/downloads/" + output_filename
            
            db.session.add(filesModel(file_db))
            db.session.commit()
            print("file success created")
            
            # Return download URL
            download_url = url_for('imagetopdf_download', file=file_db)
            return jsonify({"download_url": download_url})
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500


def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("imagetopdf/download.html", filename=filename, file=file)


def download_file(file):
    from flask import send_file, jsonify
    import os
    from dotenv import dotenv_values
    
    try:
        env_values = dotenv_values(".env")
        project_Path = env_values["PATH"]+"app/static/"
        file_path = project_Path + file
        
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found at {file_path}"}), 404
            
        filename = os.path.basename(file)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"converted_{filename}",
            mimetype="application/pdf"
        )
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": str(e)}), 400
        
        
        
        
        

    