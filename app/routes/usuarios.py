from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Usuario, UsuarioSchema, Rol
from .. import db

usuarios_bp = Blueprint('usuarios', __name__)
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# Verificar permisos por rol
def check_admin_permission(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario or usuario.id_rol != 1:  # Asumimos que rol_id 1 es Administrador
        return False
    return True

@usuarios_bp.route('/', methods=['GET'])
@jwt_required()
def get_usuarios():
    try:
        usuario_id = get_jwt_identity()
        
        # Solo los administradores pueden ver todos los usuarios
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para ver usuarios"}), 403
            
        usuarios = Usuario.query.all()
        return jsonify(usuarios_schema.dump(usuarios)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Solo los administradores pueden ver detalles de otros usuarios
        if usuario_id != id and not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para ver este usuario"}), 403
            
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        return jsonify(usuario_schema.dump(usuario)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/', methods=['POST'])
@jwt_required()
def add_usuario():
    try:
        usuario_id = get_jwt_identity()
        
        # Solo los administradores pueden crear usuarios
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para crear usuarios"}), 403
            
        data = request.get_json()
        
        # Verificar que el nombre de usuario no exista ya
        if Usuario.query.filter_by(usuario=data.get('usuario')).first():
            return jsonify({"error": "El nombre de usuario ya existe"}), 400
            
        nuevo_usuario = Usuario(
            usuario=data.get('usuario'),
            nombre=data.get('nombre'),
            id_rol=data.get('id_rol'),
            id_sucursal=data.get('id_sucursal'),
            sucursal_activa=data.get('id_sucursal'),  # Por defecto, la sucursal activa es la misma que la asignada
            activo=True
        )
        nuevo_usuario.set_password(data.get('password'))
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Usuario creado correctamente",
            "id": nuevo_usuario.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Solo los administradores pueden editar otros usuarios
        if usuario_id != id and not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para editar este usuario"}), 403
            
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        data = request.get_json()
        
        # Verificar si se está cambiando el nombre de usuario
        if 'usuario' in data and data['usuario'] != usuario.usuario:
            if Usuario.query.filter_by(usuario=data['usuario']).first():
                return jsonify({"error": "El nombre de usuario ya existe"}), 400
            usuario.usuario = data['usuario']
            
        if 'nombre' in data:
            usuario.nombre = data['nombre']
            
        # Solo un administrador puede cambiar el rol
        if 'id_rol' in data and check_admin_permission(usuario_id):
            usuario.id_rol = data['id_rol']
            
        # Solo un administrador puede cambiar la sucursal
        if 'id_sucursal' in data and check_admin_permission(usuario_id):
            usuario.id_sucursal = data['id_sucursal']
            
        if 'sucursal_activa' in data:
            # Verificar que la sucursal exista y el usuario tenga permiso
            if usuario.id_sucursal == data['sucursal_activa'] or check_admin_permission(usuario_id):
                usuario.sucursal_activa = data['sucursal_activa']
                
        if 'activo' in data and check_admin_permission(usuario_id):
            usuario.activo = data['activo']
            
        if 'password' in data:
            # Solo el propio usuario o un administrador puede cambiar la contraseña
            if usuario_id == id or check_admin_permission(usuario_id):
                usuario.set_password(data['password'])
                
        db.session.commit()
        
        return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Solo los administradores pueden eliminar usuarios
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para eliminar usuarios"}), 403
            
        # No se puede eliminar el propio usuario
        if usuario_id == id:
            return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400
            
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
