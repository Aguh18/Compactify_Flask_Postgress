from flask import request, render_template, url_for, redirect, flash, jsonify
from app.models.validate.AudioValidation import Audioform
from werkzeug.utils import secure_filename
from app.config.database import db
from app.models.fileModel import filesModel
from app.controllers.base_controller import BaseController
import os
import uuid

base_controller = BaseController('audiocompressController')

def CompressAudio():
    form = Audioform()
    if request.method == "GET":
        print("ini berjalan")
        return render_template("CompressAudio/CompressAudioForm.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                print("Ini jalan")
                file = request.files["file"]
                uid = str(uuid.uuid4())

                # Save to R2 storage
                input_key, filename, uid = base_controller.save_uploaded_file(file, uid)

                # TODO: Implement actual audio compression here
                # For now, just save the original file with compressed suffix
                # We need to calculate size. Since file is a FileStorage object, we can get length
                file.seek(0, os.SEEK_END)
                original_size = file.tell()
                file.seek(0) # Reset cursor

                name, ext = os.path.splitext(filename)
                compressed_filename = f"{name}_compressed{ext}"
                
                # In this dummy implementation, compressed size = original size
                compressed_size = original_size
                compression_ratio = 0.0

                output_key = base_controller.save_processed_file(file, compressed_filename, uid)

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
                download_url = url_for('audiocompress_download', file=file_db)
                return jsonify({"download_url": download_url})
            except Exception as e:
                print("Ini ada eror")
                print(e)
                return jsonify({"error": str(e)}), 400
        else:
            flash("File tidak valid")
            return redirect(request.url)

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
        "CompressAudio/CompressAudioDownload.html", 
        file=file,
        file_record=file_record,
        format_size=format_size
    )

def download_file(file):
    return base_controller.download_file(file)