from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..models import Usuario, UsuarioSchema
from .. import db

auth_bp = Blueprint('auth', __name__)
usuario_schema = UsuarioSchema()

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'password' not in data:
            return jsonify({"error": "Usuario y contraseña son requeridos"}), 400
            
        usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
        
        if not usuario or not usuario.check_password(data['password']):
            return jsonify({"error": "Credenciales inválidas"}), 401
            
        if not usuario.activo:
            return jsonify({"error": "Usuario desactivado"}), 403
            
        # Crear tokens JWT
        access_token = create_access_token(identity=usuario.id)
        refresh_token = create_refresh_token(identity=usuario.id)
        
        # Respuesta con información del usuario
        usuario_data = usuario_schema.dump(usuario)
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario": usuario_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        "access_token": access_token
    }), 200

@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        return jsonify(usuario_schema.dump(usuario)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/cambiar-sucursal', methods=['POST'])
@jwt_required()
def cambiar_sucursal_activa():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'id_sucursal' not in data:
            return jsonify({"error": "ID de sucursal es requerido"}), 400
            
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Verificar que la sucursal exista y el usuario tenga permiso
        if usuario.id_sucursal != data['id_sucursal']:
            return jsonify({"error": "No tienes permiso para acceder a esta sucursal"}), 403
            
        usuario.sucursal_activa = data['id_sucursal']
        db.session.commit()
        
        return jsonify({"mensaje": "Sucursal activa actualizada correctamente"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
