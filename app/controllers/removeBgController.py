import os
import uuid
import threading
import time
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

# Global variables for caching models
_rembg_model_lock = threading.Lock()
_rembg_model_loaded = False
_rembg_model = None

def preload_rembg_model():
    """Preload rembg model to avoid download delays"""
    global _rembg_model_loaded, _rembg_model

    with _rembg_model_lock:
        if not _rembg_model_loaded:
            try:
                print("Preloading rembg model...")
                from rembg import remove, new_session
                # Create session which will download and cache the model
                session = new_session('u2net')
                _rembg_model = session
                _rembg_model_loaded = True
                print("Rembg model loaded successfully!")
            except Exception as e:
                print(f"Failed to preload rembg model: {e}")
                # Fallback to default behavior
                _rembg_model_loaded = True  # Mark as loaded to avoid repeated attempts
def removeBg():
    import tempfile

    if request.method == "GET":
        # Start model preloading in background when user visits the page
        if not _rembg_model_loaded:
            threading.Thread(target=preload_rembg_model, daemon=True).start()
        return render_template("removeBackground/removeBgForm.html")
    elif request.method == "POST":
        from rembg import remove
        try:
            # Check if model is loaded, if not, load it now
            if not _rembg_model_loaded:
                preload_rembg_model()

            file = request.files["file"]
            uid = str(uuid.uuid4())

            # Validate file
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400

            # Validate file size (limit to 10MB to prevent timeout)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer

            if file_size > 10 * 1024 * 1024:  # 10MB
                return jsonify({"error": "File too large. Maximum size is 10MB"}), 400

            # Validate file extension
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({"error": "Invalid file type. Only images are allowed"}), 400

            print(f"[*] Processing file: {file.filename} ({file_size / 1024 / 1024:.2f} MB)")

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

            print("[*] Starting background removal...")
            start_time = time.time()

            # Load and resize image (resize large images to improve performance)
            input_img = Image.open(temp_input_path)

            # Resize if image is too large (max 1024px on the longest side)
            max_size = 1024
            if max(input_img.size) > max_size:
                ratio = max_size / max(input_img.size)
                new_size = tuple(int(dim * ratio) for dim in input_img.size)
                input_img = input_img.resize(new_size, Image.LANCZOS)
                print(f"[*] Resized image from {input_img.size} to {new_size}")

            # Process image background removal
            if _rembg_model:
                # Use preloaded model for faster processing
                output = remove(input_img, session=_rembg_model)
            else:
                # Fallback to default behavior
                output = remove(input_img)

            # Create temporary output file
            temp_output_path = tempfile.mktemp(suffix='.png')
            output.save(temp_output_path, optimize=True)

            processing_time = time.time() - start_time
            print(f"[*] Background removal completed in {processing_time:.2f} seconds")

            # Create proper filename for processed file
            name, ext = os.path.splitext(filename)
            processed_filename = f"{name}_nobg.png"

            # Calculate file sizes BEFORE cleaning up
            original_size = os.path.getsize(temp_input_path)
            compressed_size = os.path.getsize(temp_output_path)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            print(f"[*] Original size: {original_size / 1024:.2f} KB")
            print(f"[*] Processed size: {compressed_size / 1024:.2f} KB")

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
            print("[*] File success created")
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