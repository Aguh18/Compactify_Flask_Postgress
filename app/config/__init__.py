from flask import Flask
from .database import db
from app import app
from flask_migrate import Migrate
from dotenv import dotenv_values


env_values = dotenv_values(".env")
databaseUrl = env_values["DATABASE_URL"]




app.config['SQLALCHEMY_DATABASE_URI'] = databaseUrl
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "app/"
app.config['SECRET_KEY'] = 'teguh'






db.init_app(app) # to add the app inside SQLAlchemy()


migrate = Migrate(app, db)












