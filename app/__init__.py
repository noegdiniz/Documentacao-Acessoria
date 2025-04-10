from flask import Flask
from app.ext import db, migrate
from app.blueprints import bps
from app.mail import mail
import os
def create_app():
    app = Flask(__name__)

    btdb = os.environ.get("BTDB", "sqlite:///app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = btdb

    app.config.from_object("config")

    db.configure(app)
    migrate.configure(app)
    bps.configure(app)
    mail.configure(app)
    
    return app
