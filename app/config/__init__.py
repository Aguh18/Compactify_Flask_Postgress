from flask import Flask
from .database import db
from app import app
from flask_migrate import Migrate








app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/compactify"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "app/"
app.config['SECRET_KEY'] = 'teguh'






db.init_app(app) # to add the app inside SQLAlchemy()


migrate = Migrate(app, db)












