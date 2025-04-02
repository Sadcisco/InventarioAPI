from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Consumible, ConsumibleSchema, Usuario
from .. import db

consumibles_bp = Blueprint('consumibles', __name__)
consumible_schema = ConsumibleSchema()
consumibles_schema = ConsumibleSchema(many=True)

# Verificar permisos por rol
def check_admin_permission(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario or usuario.id_rol != 1:  # Asumimos que rol_id 1 es Administrador
        return False
    return True

@consumibles_bp.route('/', methods=['GET'])
@jwt_required()
def get_consumibles():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no autorizado"}), 401
            
        # Filtrar por sucursal activa del usuario
        id_sucursal = usuario.sucursal_activa
        
        consumibles = Consumible.query.filter_by(id_sucursal_stock=id_sucursal).all()
        return jsonify(consumibles_schema.dump(consumibles)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@consumibles_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_consumible(id):
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no autorizado"}), 401
            
        consumible = Consumible.query.get(id)
        if not consumible:
            return jsonify({"error": "Consumible no encontrado"}), 404
            
        # Verificar que el usuario tenga acceso a la sucursal del consumible
        if consumible.id_sucursal_stock != usuario.sucursal_activa and not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para ver este consumible"}), 403
            
        return jsonify(consumible_schema.dump(consumible)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@consumibles_bp.route('/', methods=['POST'])
@jwt_required()
def add_consumible():
    try:
        usuario_id = get_jwt_identity()
        
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para agregar consumibles"}), 403
            
        data = request.get_json()
        
        nuevo_consumible = Consumible(
            tipo=data.get('tipo'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            stock_actual=data.get('stock_actual', 0),
            stock_minimo=data.get('stock_minimo', 0),
            id_sucursal_stock=data.get('id_sucursal_stock')
        )
        
        db.session.add(nuevo_consumible)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Consumible agregado correctamente",
            "id": nuevo_consumible.id_consumible
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@consumibles_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_consumible(id):
    try:
        usuario_id = get_jwt_identity()
        
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para editar consumibles"}), 403
            
        consumible = Consumible.query.get(id)
        if not consumible:
            return jsonify({"error": "Consumible no encontrado"}), 404
            
        data = request.get_json()
        
        if 'tipo' in data:
            consumible.tipo = data['tipo']
        if 'marca' in data:
            consumible.marca = data['marca']
        if 'modelo' in data:
            consumible.modelo = data['modelo']
        if 'stock_actual' in data:
            consumible.stock_actual = data['stock_actual']
        if 'stock_minimo' in data:
            consumible.stock_minimo = data['stock_minimo']
        if 'id_sucursal_stock' in data:
            consumible.id_sucursal_stock = data['id_sucursal_stock']
        
        db.session.commit()
        
        return jsonify({"mensaje": "Consumible actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@consumibles_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_consumible(id):
    try:
        usuario_id = get_jwt_identity()
        
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para eliminar consumibles"}), 403
            
        consumible = Consumible.query.get(id)
        if not consumible:
            return jsonify({"error": "Consumible no encontrado"}), 404
            
        db.session.delete(consumible)
        db.session.commit()
        
        return jsonify({"mensaje": "Consumible eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
