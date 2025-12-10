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
                name, ext = os.path.splitext(filename)
                compressed_filename = f"{name}_compressed{ext}"
                output_key = base_controller.save_processed_file(file, compressed_filename, uid)

                # Save to database and get direct download URL
                file_db = base_controller.save_to_database(output_key, uid)
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
    return render_template("CompressAudio/CompressAudioDownload.html", file=file)

def download_file(file):
    return base_controller.download_file(file)