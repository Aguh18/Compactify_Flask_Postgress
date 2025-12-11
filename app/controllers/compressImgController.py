from flask import request, render_template, url_for
from app.models.validate.imageValidation import imageForm
from werkzeug.utils import secure_filename
from app.config.database import db
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
from PIL import Image
import os
import uuid
import tempfile
base_controller = BaseController('compressImgController')

try:
    RESAMPLING_FILTER = Image.LANCZOS
except AttributeError:
    RESAMPLING_FILTER = Image.ANTIALIAS

def imageCompress():
    from flask import jsonify
    form = imageForm()
    if request.method == "GET":
        return render_template("CompressImg/comressImgForm.html" , form = form)
    elif request.method == "POST":
        try:
            # Validate single file upload
            if 'file' not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

            file = request.files["file"]
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400

            # Check if multiple files are uploaded
            if len(request.files.getlist('file')) > 1:
                return jsonify({"error": "Only single file upload is supported"}), 400

            # Validate file is an image
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({"error": "Only image files are supported (.jpg, .jpeg, .png, .gif, .webp, .bmp, .tiff)"}), 400

            uid = str(uuid.uuid4())

            # Save to R2 storage
            input_key, filename, uid = base_controller.save_uploaded_file(file, uid)

            # Download file from R2 for processing
            from app.service.r2_helper import get_r2_helper
            input_result = get_r2_helper().download_file(input_key)

            if not input_result['success']:
                return jsonify({"error": "Failed to retrieve file from storage"}), 500

            # Create temporary file for processing
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_input:
                tmp_input.write(input_result['file_obj'].read())
                temp_input_path = tmp_input.name

            # Get quality value (1-100 percentage)
            try:
                quality = int(request.form.get('quality', 85))
                # Ensure quality is within valid range
                quality = max(1, min(100, quality))

                # Calculate new_size_ratio based on quality
                # Higher quality = less resizing, lower quality = more resizing
                if quality >= 85:
                    new_size_ratio = 0.95  # Very high quality - minimal resizing
                elif quality >= 70:
                    new_size_ratio = 0.9   # High quality
                elif quality >= 50:
                    new_size_ratio = 0.8   # Medium quality
                elif quality >= 30:
                    new_size_ratio = 0.7   # Low quality
                else:
                    new_size_ratio = 0.6   # Very low quality - more resizing

            except (ValueError, TypeError):
                # Fallback to default values
                quality = 85
                new_size_ratio = 0.9

            # Create temporary output path
            temp_output_path = tempfile.mktemp(suffix='_compressed.jpg')

            # Process image with custom quality
            print(f"Processing image with quality: {quality}% and size ratio: {new_size_ratio}")
            compressed_filename = compress_img(filename, temp_input_path, temp_output_path, new_size_ratio=new_size_ratio, quality=quality, width=None, height=None, to_jpg=True)

            # Calculate file sizes BEFORE cleaning up
            original_size = os.path.getsize(temp_input_path)
            compressed_size = os.path.getsize(temp_output_path)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 2)

            print(f"[*] Original size: {original_size} bytes")
            print(f"[*] Compressed size: {compressed_size} bytes")
            print(f"[*] Compression ratio: {compression_ratio}%")

            # Upload compressed file to R2
            output_key = base_controller.save_processed_file(temp_output_path, compressed_filename, uid)

            # Save to database with size information
            file_db = base_controller.save_to_database(
                output_key,
                uid,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                quality=quality
            )
            print("nama file adalah", file_db)
            print("file success created")
            # Return download page URL instead of direct file URL
            download_url = url_for('compressimg_download', file=file_db)
            return jsonify({"download_url": download_url})

        except Exception as e:
            print("Ini ada eror")
            print(e)
            return jsonify({"error": str(e)}), 400
        finally:
            # Clean up temporary files
            try:
                if 'temp_input_path' in locals():
                    os.unlink(temp_input_path)
                if 'temp_output_path' in locals():
                    os.unlink(temp_output_path)
            except:
                pass

def render_download_page(file):
    from app.models.fileModel import filesModel
    from app.config.database import db
    from sqlalchemy.exc import OperationalError, DisconnectionError
    import time

    # Get file record from database with retry mechanism
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            file_record = db.session.query(filesModel).filter_by(file=file).first()
            break

        except (OperationalError, DisconnectionError) as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed when fetching file record (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2
                file_record = None
                continue
            else:
                print(f"Database connection failed after {max_retries} attempts when fetching file record")
                file_record = None
                break

        except Exception as e:
            print(f"Unexpected database error when fetching file record: {e}")
            file_record = None
            break

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

    return render_template("CompressImg/compressImgDownload.html",
                         file=file,
                         file_record=file_record,
                         format_size=format_size)
def download_file(file):
    return base_controller.download_file(file)

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"
def compress_img(filename, input_path, output_path, new_size_ratio=0.9, quality=50, width=None, height=None, to_jpg=True):
    img = Image.open(input_path)
    print(f"[*] Processing image: {filename}")
    print(f"[*] Original shape: {img.size}")
    image_size = os.path.getsize(input_path)
    print(f"[*] Size before compression: {get_size_format(image_size)}")
    print(f"[*] Compression quality: {quality}%")

    original_shape = img.size
    if new_size_ratio < 1.0:
        new_shape = (int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio))
        img = img.resize(new_shape, RESAMPLING_FILTER)
        print(f"[+] Resized from {original_shape} to {img.size} (ratio: {new_size_ratio})")
    elif width and height:
        img = img.resize((width, height), RESAMPLING_FILTER)
        print(f"[+] Resized from {original_shape} to {img.size} (custom size)")

    filename, ext = os.path.splitext(filename)
    if to_jpg:
        new_filename = f"{filename}_compressed.jpg"
    else:
        new_filename = f"{filename}_compressed{ext}"

    try:
        img.save(output_path, quality=quality, optimize=True)
    except OSError:
        img = img.convert("RGB")
        img.save(output_path, quality=quality, optimize=True)
        print("[+] Converted to RGB for JPEG compression")

    new_image_size = os.path.getsize(output_path)
    compression_ratio = (1 - new_image_size / image_size) * 100
    print(f"[*] Size after compression: {get_size_format(new_image_size)}")
    print(f"[*] Compression ratio: {compression_ratio:.2f}%")

    return secure_filename(new_filename)