from app import app
from app.controllers import indexcontroller
from app.controllers import removeBgController

@app.route("/", methods=["GET"])
def index_route():
    return indexcontroller.user_list()



# Remove Background
@app.route("/removebg", methods=["GET", "POST"], endpoint="removebg")
def removebg_route():
    return removeBgController.removeBg()
