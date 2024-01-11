from app import app
from app.controllers import indexcontroller
from app.controllers import removeBgController
from app.controllers import compressImgController

@app.route("/", methods=["GET"])
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
