from app import app
from app.controllers import indexcontroller
from app.controllers import removeBgController
from app.controllers import compressImgController
from app.controllers import wordToPDFController
from app.controllers import compressPdfController
from app.controllers import imageToPdfController
from app.controllers import zipController
from app.controllers import imageToGrayscaleController

@app.route("/", methods=["GET"], endpoint="home")
def index_route():
    return indexcontroller.user_list()




# Remove Background
@app.route("/removebg", methods=["GET", "POST"], endpoint="removebg")
def removebg_route():
    return removeBgController.removeBg()

# Compress Image
@app.route("/compressimg", methods=["GET", "POST"], endpoint="compressImg")
def compressImg_route():
    return compressImgController.imageCompress()

# Word to PDF
@app.route("/wordtopdf", methods=["GET", "POST"], endpoint="wordToPDF")
def wordToPDF_route():
    return wordToPDFController.wordToPDF()

# Image to pdf
@app.route("/imagetopdf", methods=["GET", "POST"], endpoint="imageToPdf")
def compressPdf_route():
    return imageToPdfController.imageTopdf()

# Compress PDF
@app.route("/compresspdf", methods=["GET", "POST"], endpoint="compressPdf")
def compressPdf_route():
    return compressPdfController.compressPdf()

#  Zip
@app.route("/zip", methods=["GET", "POST"], endpoint="zip")
def zip_route():
    return  zipController.zip()

@app.route("/imgtogray", methods=["GET", "POST"], endpoint="imgtogray")
def imgtogray_route():
    return  imageToGrayscaleController.imgtogray()
