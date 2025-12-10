from flask import Blueprint, request, render_template, url_for, redirect, flash
from app.models.validate.imageValidation import imageForm
from app.config.database import db
from werkzeug.utils import secure_filename 
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
import img2pdf
from PIL import Image
import os
from dotenv import dotenv_values
import uuid
base_controller = BaseController('imageToPdfController')
def imageTopdf():
    from flask import jsonify
    import tempfile

    if request.method == "GET":
        return render_template("imagetopdf/imageToPdfForm.html")
    elif request.method == "POST":
        try:
            uid = str(uuid.uuid4())
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({"error": "No files selected"}), 400

            image_paths = []
            saved_files = []

            for file in files:
                if file and file.filename:
                    # Save to R2 storage
                    input_key, filename, file_uid = base_controller.save_uploaded_file(file, uid)

                    # Download from R2 for processing
                    from app.service.r2_helper import r2_helper
                    input_result = r2_helper.download_file(input_key)

                    if not input_result['success']:
                        return jsonify({"error": f"Failed to retrieve {filename} from storage"}), 500

                    # Create temporary file for processing
                    temp_input_path = tempfile.mktemp(suffix='.jpg')
                    with open(temp_input_path, 'wb') as tmp_file:
                        tmp_file.write(input_result['file_obj'].read())

                    image_paths.append(temp_input_path)

            # Convert images to PDF
            pdf_bytes = img2pdf.convert(image_paths)

            # Create temporary output file
            temp_output_path = tempfile.mktemp(suffix='.pdf')
            with open(temp_output_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)

            print("Successfully created PDF file")

            # Clean up temporary image files
            for img_path in image_paths:
                try:
                    os.remove(img_path)
                except:
                    pass

            # Upload PDF to R2
            output_filename = f"converted_images_{uid}.pdf"
            output_key = base_controller.save_processed_file(temp_output_path, output_filename, uid)

            # Clean up temporary PDF file
            os.remove(temp_output_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(output_key, uid)
            print("file success created")

            # Return download page URL instead of direct file URL
            download_url = url_for('imagetopdf_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
def render_download_page(file):
    filename = os.path.basename(file)
    return render_template("imagetopdf/download.html", filename=filename, file=file)
def download_file(file):
    return base_controller.download_file(file)