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

# Global variables for caching models (with memory management)
_rembg_model_lock = threading.Lock()
_rembg_model_loaded = False
_rembg_model = None
_rembg_last_used = None
_model_ttl = 180  # Keep model in memory for 3 minutes (extended due to universal preload)

def cleanup_rembg_model():
    """Cleanup rembg model from memory to save RAM"""
    global _rembg_model, _rembg_model_loaded, _rembg_last_used

    with _rembg_model_lock:
        if _rembg_model is not None:
            try:
                import gc
                # Clear model from memory
                _rembg_model = None
                _rembg_model_loaded = False
                _rembg_last_used = None
                gc.collect()
                print("Rembg model cleaned up from memory")
            except Exception as e:
                print(f"Error cleaning up rembg model: {e}")

def update_model_usage():
    """Update the last used timestamp for the model"""
    global _rembg_last_used
    with _rembg_model_lock:
        _rembg_last_used = time.time()

def periodic_memory_cleanup():
    """Periodic cleanup to prevent memory leaks"""
    current_time = time.time()
    if (_rembg_last_used is not None and
        current_time - _rembg_last_used > _model_ttl and
        _rembg_model is not None):
        print("[*] Periodic cleanup: Model TTL expired")
        cleanup_rembg_model()

def preload_rembg_model():
    """Lazy load rembg model only when needed"""
    global _rembg_model_loaded, _rembg_model, _rembg_last_used

    with _rembg_model_lock:
        current_time = time.time()

        # Check if model needs to be cleaned up (TTL expired)
        if (_rembg_last_used is not None and
            current_time - _rembg_last_used > _model_ttl and
            _rembg_model is not None):
            print("Model TTL expired, cleaning up...")
            cleanup_rembg_model()

        if not _rembg_model_loaded:
            try:
                print("Loading rembg model (lazy loading)...")
                from rembg import remove, new_session
                import gc
                # Create session which will download and cache the model
                session = new_session('u2net')
                _rembg_model = session
                _rembg_model_loaded = True
                _rembg_last_used = current_time
                # Force garbage collection after loading
                gc.collect()
                print("Rembg model loaded successfully!")
            except Exception as e:
                print(f"Failed to load rembg model: {e}")
                # Fallback to default behavior
                _rembg_model_loaded = True  # Mark as loaded to avoid repeated attempts
def removeBg():
    import tempfile

    if request.method == "GET":
        # Model should already be preloaded by universal trigger
        # Just show the form
        print("[*] Remove BG form accessed - model status:", "loaded" if _rembg_model_loaded else "loading")
        return render_template("removeBackground/removeBgForm.html")
    elif request.method == "POST":
        from rembg import remove
        try:
            # Ensure model is loaded with timeout
            model_load_start = time.time()

            # Wait up to 10 seconds for model to load
            max_wait = 10
            while not _rembg_model_loaded and (time.time() - model_load_start) < max_wait:
                print(f"[*] Waiting for model to load... ({int(time.time() - model_load_start)}s)")
                time.sleep(0.5)
                preload_rembg_model()

            if not _rembg_model_loaded:
                print("[*] Model loading timeout, proceeding with default loading...")

            update_model_usage()  # Update last used time

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
                print("[*] Using cached rembg model")
                output = remove(input_img, session=_rembg_model)
            else:
                # Fallback to default behavior
                print("[*] Using new rembg model session")
                output = remove(input_img)

            # Create temporary output file
            temp_output_path = tempfile.mktemp(suffix='.png')
            output.save(temp_output_path, optimize=True)

            processing_time = time.time() - start_time
            print(f"[*] Background removal completed in {processing_time:.2f} seconds")

            # Force garbage collection to free memory immediately after processing
            import gc
            gc.collect()

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
            print(f"[*] Database entry created: {file_db}")
            # Return download page URL instead of direct file URL
            download_url = url_for('removebg_download', file=file_db)
            print(f"[*] Returning download URL: {download_url}")

            response_data = {"download_url": download_url}
            print(f"[*] Response data: {response_data}")

            # Schedule aggressive cleanup after response
            def delayed_cleanup():
                import time
                time.sleep(30)  # Wait 30 seconds after processing
                cleanup_rembg_model()

            import threading
            threading.Thread(target=delayed_cleanup, daemon=True).start()

            return jsonify(response_data)

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

def removebg_status():
    """API endpoint to check model loading status"""
    global _rembg_model_loaded, _rembg_last_used, _rembg_model

    # Perform periodic cleanup on status check
    periodic_memory_cleanup()

    # Calculate memory usage info
    import psutil
    import os
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    # Check if model should be cleaned up
    current_time = time.time()
    cleanup_needed = (_rembg_last_used is not None and
                     current_time - _rembg_last_used > _model_ttl and
                     _rembg_model is not None)

    status = {
        'model_loaded': _rembg_model_loaded,
        'last_used': _rembg_last_used,
        'ready': _rembg_model_loaded and _rembg_model is not None,
        'memory_mb': round(memory_info.rss / 1024 / 1024, 1),
        'memory_vms_mb': round(memory_info.vms / 1024 / 1024, 1),
        'model_ttl_seconds': _model_ttl,
        'cleanup_needed': cleanup_needed,
        'timestamp': current_time
    }

    return jsonify(status)