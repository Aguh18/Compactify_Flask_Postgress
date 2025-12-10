import os
import uuid
from dotenv import dotenv_values
from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from PIL import Image
from werkzeug.utils import secure_filename
from app.config.database import db
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
from app.models.validate.imageValidation import imageForm
base_controller = BaseController('removeBgController')
def removeBg():
    from rembg import remove
    import tempfile

    if request.method == "GET":
        return render_template("removeBackground/removeBgForm.html")
    elif request.method == "POST":
        try:
            file = request.files["file"]
            uid = str(uuid.uuid4())

            # Save to R2 storage
            input_key, filename, uid = base_controller.save_uploaded_file(file, uid)

            # Download file from R2 for processing
            from app.service.r2_helper import r2_helper
            input_result = r2_helper.download_file(input_key)

            if not input_result['success']:
                return jsonify({"error": "Failed to retrieve file from storage"}), 500

            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False) as tmp_input:
                tmp_input.write(input_result['file_obj'].read())
                temp_input_path = tmp_input.name

            # Process image background removal
            input = Image.open(temp_input_path)
            output = remove(input)

            # Create temporary output file
            temp_output_path = tempfile.mktemp(suffix='.png')
            output.save(temp_output_path)

            # Create proper filename for processed file
            name, ext = os.path.splitext(filename)
            processed_filename = f"{name}_nobg.png"

            # Upload processed image to R2
            output_key = base_controller.save_processed_file(temp_output_path, processed_filename, uid)

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(output_key, uid)
            print("file success created")
            # Return download page URL instead of direct file URL
            download_url = url_for('removebg_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error in removeBg: {e}")
            return jsonify({"error": str(e)}), 400
def render_download_page(file):
    filename = os.path.basename(file)
    return render_template(
        "removeBackground/removeBgDownload.html", filename=filename, file=file
    )
def download_file(file):
    return base_controller.download_file(file)