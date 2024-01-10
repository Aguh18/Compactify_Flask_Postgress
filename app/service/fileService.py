
from app.config.database import db
from app.models.fileModel import filesmodel


def create(file):
    try:
        file = filesmodel(file)
        db.session.add(file)
        db.session.commit()
        print("file created")
        return True
    except Exception as e:
        print(e)
        return False