from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config  # ← esto es clave

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # ← esto también es clave

    CORS(app)
    db.init_app(app)

    from .routes import api
    app.register_blueprint(api)

    return app
