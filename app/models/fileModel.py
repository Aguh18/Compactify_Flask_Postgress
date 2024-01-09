from app.config.database import db


class filesmodel(db.Model):
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file = db.Column(db.String())


    def __init__(self, file):
        self.file = file
       

    def __repr__(self):
        return f"<file {self.name}>"