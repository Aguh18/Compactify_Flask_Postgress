from app import app
from flask import render_template, request
from app.controllers import indexcontroller
from app.controllers import removeBgController
from app.controllers import compressImgController
from app.controllers import wordToPDFController
from app.controllers import compressPdfController
from app.controllers import imageToPdfController
from app.controllers import zipController
from app.controllers import imageToGrayscaleController
from app.controllers import audiocompressController

# Home Page
@app.route("/", methods=["GET", "POST"], endpoint="home")
def home():
    return indexcontroller.user_list()

# Download Page
@app.route("/download", methods=["GET", "POST"], endpoint="download")
def download():
    return render_template("download.html")

# Remove BG
@app.route("/removebg", methods=["GET", "POST"], endpoint="removebg")
def removeBg_route():
    return removeBgController.removeBg()

# Download page for remove background
@app.route("/removebg/download", methods=["GET"], endpoint="removebg_download")
def removebg_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return removeBgController.render_download_page(file)

# Actual file download for remove background
@app.route("/removebg/download-file", methods=["GET"], endpoint="removebg_download_file")
def removebg_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return removeBgController.download_file(file)

# Model status endpoint for remove background
@app.route("/removebg/status", methods=["GET"], endpoint="removebg_status")
def removebg_status():
    return removeBgController.removebg_status()

# Compress Image
@app.route("/compressimg", methods=["GET", "POST"], endpoint="compressimg")
def compressImg_route():
    return compressImgController.imageCompress()

# Download page for compressed Image
@app.route("/compressimg/download", methods=["GET"], endpoint="compressimg_download")
def compressimg_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return compressImgController.render_download_page(file)

# Actual file download for compressed Image
@app.route("/compressimg/download-file", methods=["GET"], endpoint="compressimg_download_file")
def compressimg_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return compressImgController.download_file(file)

# Word to PDF
@app.route("/wordtopdf", methods=["GET", "POST"], endpoint="wordtopdf")
def wordToPdf_route():
    return wordToPDFController.wordToPDF()

# Download page for word to PDF
@app.route("/wordtopdf/download", methods=["GET"], endpoint="wordtopdf_download")
def wordtopdf_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return wordToPDFController.render_download_page(file)

# Actual file download for word to PDF
@app.route("/wordtopdf/download-file", methods=["GET"], endpoint="wordtopdf_download_file")
def wordtopdf_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return wordToPDFController.download_file(file)

# image to PDF
@app.route("/imagetopdf", methods=["GET", "POST"], endpoint="imagetopdf")
def imagetopdf_route():
    return imageToPdfController.imageTopdf()

# Download page for image to PDF
@app.route("/imagetopdf/download", methods=["GET"], endpoint="imagetopdf_download")
def imagetopdf_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return imageToPdfController.render_download_page(file)

# Actual file download for image to PDF
@app.route("/imagetopdf/download-file", methods=["GET"], endpoint="imagetopdf_download_file")
def imagetopdf_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return imageToPdfController.download_file(file)

# image to Grayscale
@app.route("/imgtogray", methods=["GET", "POST"], endpoint="imgtogray")
def imageToGrayscale_route():
    return imageToGrayscaleController.imgtogray()

# Download page for image to grayscale
@app.route("/imgtogray/download", methods=["GET"], endpoint="imgtogray_download")
def imgtogray_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return imageToGrayscaleController.render_download_page(file)

# Actual file download for image to grayscale
@app.route("/imgtogray/download-file", methods=["GET"], endpoint="imgtogray_download_file")
def imgtogray_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return imageToGrayscaleController.download_file(file)

# Preview image for image to grayscale
@app.route("/imgtogray/preview", methods=["GET"], endpoint="imgtogray_preview")
def imgtogray_preview():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return imageToGrayscaleController.preview_file(file)

# Compress PDF
@app.route("/compresspdf", methods=["GET", "POST"], endpoint="compresspdf")
def compressPdf_route():
    return compressPdfController.compressPdf()

# Download page for PDF Compress
@app.route("/compresspdf/download", methods=["GET"], endpoint="compresspdf_download")
def compresspdf_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return compressPdfController.render_download_page(file)

# Actual file download for PDF Compress
@app.route("/compresspdf/download-file", methods=["GET"], endpoint="compresspdf_download_file")
def compresspdf_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return compressPdfController.download_file(file)

# Zip Compression
@app.route("/compresszip", methods=["GET", "POST"], endpoint="compresszip")
def compressZip_route():
    return zipController.zip()

# Download page for zip compression
@app.route("/compresszip/download", methods=["GET"], endpoint="compresszip_download")
def compresszip_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return zipController.render_download_page(file)

# Actual file download for zip compression
@app.route("/compresszip/download-file", methods=["GET"], endpoint="compresszip_download_file")
def compresszip_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return zipController.download_file(file)

# Zip (alternative endpoint for nav compatibility)
@app.route("/zip", methods=["GET", "POST"], endpoint="zip")
def zip_route():
    return zipController.zip()

# Download page for zip (alternative)
@app.route("/zip/download", methods=["GET"], endpoint="zip_download")
def zip_download():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return zipController.render_download_page(file)

# Actual file download for zip (alternative)
@app.route("/zip/download-file", methods=["GET"], endpoint="zip_download_file")
def zip_download_file():
    file = request.args.get("file")
    if not file:
        return "File not found", 404
    return zipController.download_file(file)

# Audio Compression
@app.route("/compressaudio", methods=["GET", "POST"], endpoint="compressaudio")
def compressAudio_route():
    return audiocompressController.CompressAudio()

# Audio Compress (alternative endpoint for nav compatibility)
@app.route("/audiocompress", methods=["GET", "POST"], endpoint="audiocompress")
def audioCompress_route():
    return audiocompressController.CompressAudio()
