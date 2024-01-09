from app import app
from app.controllers import indexcontroller

@app.route("/", methods=["GET"])
def index_route():
    return indexcontroller.user_list()

    