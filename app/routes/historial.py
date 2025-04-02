from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import HistorialMovimiento, HistorialMovimientoSchema, Usuario
from .. import db

historial_bp = Blueprint('historial', __name__)
historial_schema = HistorialMovimientoSchema()
historiales_schema = HistorialMovimientoSchema(many=True)

# Verificar permisos por rol
def check_admin_permission(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario or usuario.id_rol != 1:  # Asumimos que rol_id 1 es Administrador
        return False
    return True

@historial_bp.route('/', methods=['GET'])
@jwt_required()
def get_historial():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no autorizado"}), 401
        
        # Parámetros de filtrado opcionales
        tipo_equipo = request.args.get('tipo_equipo')
        id_equipo = request.args.get('id_equipo')
        
        # Consulta base
        query = HistorialMovimiento.query
        
        # Aplicar filtros si existen
        if tipo_equipo:
            query = query.filter_by(tipo_equipo=tipo_equipo)
        if id_equipo:
            query = query.filter_by(id_equipo=id_equipo)
            
        # Si no es admin, mostrar solo los de su sucursal (asumiendo que esta información se puede obtener)
        if not check_admin_permission(usuario_id):
            # Esta lógica depende de cómo estén relacionados los movimientos con las sucursales
            # Asumimos que se puede obtener a través de los usuarios relacionados
            pass
            
        # Ordenar por fecha descendente
        query = query.order_by(HistorialMovimiento.fecha.desc())
        
        # Ejecutar consulta
        historial = query.all()
        
        return jsonify(historiales_schema.dump(historial)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@historial_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_movimiento(id):
    try:
        usuario_id = get_jwt_identity()
        
        movimiento = HistorialMovimiento.query.get(id)
        if not movimiento:
            return jsonify({"error": "Registro de movimiento no encontrado"}), 404
            
        # Verificar permisos (asumiendo que los administradores pueden ver todos los movimientos)
        if not check_admin_permission(usuario_id):
            # Si no es admin, verificar si el usuario está relacionado con este movimiento
            # Esta lógica depende de cómo estén relacionados los movimientos con los usuarios
            pass
            
        return jsonify(historial_schema.dump(movimiento)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@historial_bp.route('/', methods=['POST'])
@jwt_required()
def add_movimiento():
    try:
        usuario_id = get_jwt_identity()
        
        # Solo administradores y usuarios autorizados pueden registrar movimientos manualmente
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para registrar movimientos"}), 403
            
        data = request.get_json()
        
        nuevo_movimiento = HistorialMovimiento(
            tipo_equipo=data.get('tipo_equipo'),
            id_equipo=data.get('id_equipo'),
            responsable_anterior=data.get('responsable_anterior'),
            responsable_nuevo=data.get('responsable_nuevo'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(nuevo_movimiento)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Movimiento registrado correctamente",
            "id": nuevo_movimiento.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
