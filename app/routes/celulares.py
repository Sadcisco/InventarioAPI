from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import (
    Celular, CelularSchema, 
    InventarioGeneral, Usuario, HistorialMovimiento
)
from .. import db
from datetime import datetime

celulares_bp = Blueprint('celulares', __name__)
celular_schema = CelularSchema()
celulares_schema = CelularSchema(many=True)

# Verificar permisos por rol
def check_admin_permission(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario or usuario.id_rol != 1:  # Asumimos que rol_id 1 es Administrador
        return False
    return True

@celulares_bp.route('/', methods=['GET'])
@jwt_required()
def get_celulares():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no autorizado"}), 401
            
        # Filtrar por sucursal activa del usuario
        id_sucursal = usuario.sucursal_activa

        # Obtener todos los registros de inventario general que sean celulares
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Celular', 
            id_sucursal_ubicacion=id_sucursal
        ).all()
        
        result = []
        for item in inventario:
            celular = Celular.query.get(item.id_registro)
            if celular:
                celular_data = celular_schema.dump(celular)
                celular_data.update({
                    "id_inventario": item.id_inventario,
                    "estado": item.estado,
                    "id_usuario_responsable": item.id_usuario_responsable,
                    "id_area_responsable": item.id_area_responsable,
                    "id_sucursal_ubicacion": item.id_sucursal_ubicacion,
                    "fecha_ingreso": item.fecha_ingreso.isoformat() if item.fecha_ingreso else None,
                    "observaciones": item.observaciones
                })
                result.append(celular_data)
                
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@celulares_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_celular(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Buscar el celular en el inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Celular',
            id_registro=id
        ).first()
        
        if not inventario:
            return jsonify({"error": "Celular no encontrado"}), 404
            
        # Verificar acceso por sucursal
        usuario = Usuario.query.get(usuario_id)
        if usuario.sucursal_activa != inventario.id_sucursal_ubicacion and not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para ver este celular"}), 403
            
        # Obtener detalles del celular
        celular = Celular.query.get(id)
        if not celular:
            return jsonify({"error": "Detalles del celular no encontrados"}), 404
            
        # Combinar datos
        celular_data = celular_schema.dump(celular)
        celular_data.update({
            "id_inventario": inventario.id_inventario,
            "estado": inventario.estado,
            "id_usuario_responsable": inventario.id_usuario_responsable,
            "id_area_responsable": inventario.id_area_responsable,
            "id_sucursal_ubicacion": inventario.id_sucursal_ubicacion,
            "fecha_ingreso": inventario.fecha_ingreso.isoformat() if inventario.fecha_ingreso else None,
            "observaciones": inventario.observaciones
        })
        
        return jsonify(celular_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@celulares_bp.route('/', methods=['POST'])
@jwt_required()
def add_celular():
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar si es admin o tiene permisos para crear
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para agregar celulares"}), 403
            
        data = request.get_json()
        
        # Crear el registro del celular
        nuevo_celular = Celular(
            codigo_interno=data.get('codigo_interno'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            imei=data.get('imei'),
            numero_linea=data.get('numero_linea'),
            sistema_operativo=data.get('sistema_operativo'),
            capacidad_almacenamiento=data.get('capacidad_almacenamiento'),
            comentarios=data.get('comentarios')
        )
        
        db.session.add(nuevo_celular)
        db.session.flush()  # Para obtener el ID generado
        
        # Crear el registro en inventario general
        nuevo_inventario = InventarioGeneral(
            tipo_equipo='Celular',
            id_registro=nuevo_celular.id_celular,
            estado=data.get('estado', 'SinAsignar'),
            id_usuario_responsable=data.get('id_usuario_responsable'),
            id_area_responsable=data.get('id_area_responsable'),
            id_sucursal_ubicacion=data.get('id_sucursal_ubicacion'),
            fecha_ingreso=datetime.now(),
            observaciones=data.get('observaciones', '')
        )
        
        db.session.add(nuevo_inventario)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Celular agregado correctamente",
            "id_celular": nuevo_celular.id_celular,
            "id_inventario": nuevo_inventario.id_inventario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@celulares_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_celular(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar permisos
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para editar celulares"}), 403
            
        # Verificar que el celular exista
        celular = Celular.query.get(id)
        if not celular:
            return jsonify({"error": "Celular no encontrado"}), 404
            
        # Buscar el registro en inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Celular',
            id_registro=id
        ).first()
        
        if not inventario:
            return jsonify({"error": "Registro de inventario no encontrado"}), 404
            
        data = request.get_json()
        
        # Actualizar el celular
        if 'codigo_interno' in data:
            celular.codigo_interno = data['codigo_interno']
        if 'marca' in data:
            celular.marca = data['marca']
        if 'modelo' in data:
            celular.modelo = data['modelo']
        if 'imei' in data:
            celular.imei = data['imei']
        if 'numero_linea' in data:
            celular.numero_linea = data['numero_linea']
        if 'sistema_operativo' in data:
            celular.sistema_operativo = data['sistema_operativo']
        if 'capacidad_almacenamiento' in data:
            celular.capacidad_almacenamiento = data['capacidad_almacenamiento']
        if 'comentarios' in data:
            celular.comentarios = data['comentarios']
            
        # Actualizar inventario
        if 'estado' in data:
            inventario.estado = data['estado']
        if 'id_usuario_responsable' in data:
            # Registrar cambio de responsable en el historial
            if inventario.id_usuario_responsable != data['id_usuario_responsable']:
                historial = HistorialMovimiento(
                    tipo_equipo='Celular',
                    id_equipo=id,
                    responsable_anterior=inventario.id_usuario_responsable,
                    responsable_nuevo=data['id_usuario_responsable'],
                    fecha=datetime.now(),
                    observaciones=data.get('observaciones_cambio', 'Cambio de responsable')
                )
                db.session.add(historial)
            inventario.id_usuario_responsable = data['id_usuario_responsable']
        if 'id_area_responsable' in data:
            inventario.id_area_responsable = data['id_area_responsable']
        if 'id_sucursal_ubicacion' in data:
            inventario.id_sucursal_ubicacion = data['id_sucursal_ubicacion']
        if 'observaciones' in data:
            inventario.observaciones = data['observaciones']
            
        db.session.commit()
        
        return jsonify({"mensaje": "Celular actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@celulares_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_celular(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar permisos de administrador
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para eliminar celulares"}), 403
            
        # Buscar el celular
        celular = Celular.query.get(id)
        if not celular:
            return jsonify({"error": "Celular no encontrado"}), 404
            
        # Buscar el registro en inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Celular',
            id_registro=id
        ).first()
        
        if inventario:
            db.session.delete(inventario)
            
        db.session.delete(celular)
        db.session.commit()
        
        return jsonify({"mensaje": "Celular eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
