from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # Importar marshmallow después de que se inicializa SQLAlchemy
    from .models import ma
    ma.init_app(app)
    
    # Inicializar las tablas en la base de datos
    with app.app_context():
        db.create_all()
    
    # Registrar blueprints
    from .routes.auth import auth_bp
    from .routes.equipos import equipos_bp
    from .routes.celulares import celulares_bp
    from .routes.impresoras import impresoras_bp
    from .routes.consumibles import consumibles_bp
    from .routes.usuarios import usuarios_bp
    from .routes.historial import historial_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(equipos_bp, url_prefix='/api/equipos')
    app.register_blueprint(celulares_bp, url_prefix='/api/celulares')
    app.register_blueprint(impresoras_bp, url_prefix='/api/impresoras')
    app.register_blueprint(consumibles_bp, url_prefix='/api/consumibles')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(historial_bp, url_prefix='/api/historial')

    return app
