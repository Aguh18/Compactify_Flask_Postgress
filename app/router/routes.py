from app import app
from app.controllers import indexcontroller
from app.controllers import removeBgController
from app.controllers import compressImgController
from app.controllers import wordToPDFController
from app.controllers import compressPdfController

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

# Compress PDF
@app.route("/compresspdf", methods=["GET", "POST"], endpoint="compressPdf")
def compressPdf_route():
    return compressPdfController.compressPdf()
