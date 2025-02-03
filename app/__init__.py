from flask import Flask
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    # MongoDB connection
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB")
    client = MongoClient(mongo_uri)
    app.db = client[mongo_db]

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
