from app.config.database import db


class filesModel(db.Model):
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file = db.Column(db.String())
    original_size = db.Column(db.BigInteger())
    compressed_size = db.Column(db.BigInteger())
    compression_ratio = db.Column(db.Float())
    quality = db.Column(db.Integer())


    def __init__(self, file, original_size=None, compressed_size=None, compression_ratio=None, quality=None):
        self.file = file
        self.original_size = original_size
        self.compressed_size = compressed_size
        self.compression_ratio = compression_ratio
        self.quality = quality


    def __repr__(self):
        return f"<file {self.file}>"
    
    