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
            from app.service.r2_helper import get_r2_helper
            input_result = get_r2_helper().download_file(input_key)

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

            # Calculate file sizes BEFORE cleaning up
            original_size = os.path.getsize(temp_input_path)
            compressed_size = os.path.getsize(temp_output_path)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            # Upload processed image to R2
            output_key = base_controller.save_processed_file(temp_output_path, processed_filename, uid)

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            # Save to database and get direct download URL
            file_db = base_controller.save_to_database(
                output_key, 
                uid,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio
            )
            print("file success created")
            # Return download page URL instead of direct file URL
            download_url = url_for('removebg_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print(f"Error in removeBg: {e}")
            return jsonify({"error": str(e)}), 400

def render_download_page(file):
    from app.models.fileModel import filesModel
    from app.config.database import db

    # Get file record from database
    file_record = db.session.query(filesModel).filter_by(file=file).first()
    
    # Format file sizes for display
    def format_size(bytes):
        if not bytes:
            return "0 Bytes"
        sizes = ["Bytes", "KB", "MB", "GB"]
        i = 0
        while bytes >= 1024 and i < len(sizes) - 1:
            bytes /= 1024.0
            i += 1
        return f"{bytes:.2f} {sizes[i]}"

    return render_template(
        "removeBackground/removeBgDownload.html", 
        file=file,
        file_record=file_record,
        format_size=format_size
    )
def download_file(file):
    return base_controller.download_file(file)