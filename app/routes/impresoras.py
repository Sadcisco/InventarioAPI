from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import (
    Impresora, ImpresoraSchema, 
    InventarioGeneral, Usuario, HistorialMovimiento
)
from .. import db
from datetime import datetime

impresoras_bp = Blueprint('impresoras', __name__)
impresora_schema = ImpresoraSchema()
impresoras_schema = ImpresoraSchema(many=True)

# Verificar permisos por rol
def check_admin_permission(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario or usuario.id_rol != 1:  # Asumimos que rol_id 1 es Administrador
        return False
    return True

@impresoras_bp.route('/', methods=['GET'])
@jwt_required()
def get_impresoras():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no autorizado"}), 401
            
        # Filtrar por sucursal activa del usuario
        id_sucursal = usuario.sucursal_activa

        # Obtener todos los registros de inventario general que sean impresoras
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Impresora', 
            id_sucursal_ubicacion=id_sucursal
        ).all()
        
        result = []
        for item in inventario:
            impresora = Impresora.query.get(item.id_registro)
            if impresora:
                impresora_data = impresora_schema.dump(impresora)
                impresora_data.update({
                    "id_inventario": item.id_inventario,
                    "estado": item.estado,
                    "id_usuario_responsable": item.id_usuario_responsable,
                    "id_area_responsable": item.id_area_responsable,
                    "id_sucursal_ubicacion": item.id_sucursal_ubicacion,
                    "fecha_ingreso": item.fecha_ingreso.isoformat() if item.fecha_ingreso else None,
                    "observaciones": item.observaciones
                })
                result.append(impresora_data)
                
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@impresoras_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_impresora(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Buscar la impresora en el inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Impresora',
            id_registro=id
        ).first()
        
        if not inventario:
            return jsonify({"error": "Impresora no encontrada"}), 404
            
        # Verificar acceso por sucursal
        usuario = Usuario.query.get(usuario_id)
        if usuario.sucursal_activa != inventario.id_sucursal_ubicacion and not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para ver esta impresora"}), 403
            
        # Obtener detalles de la impresora
        impresora = Impresora.query.get(id)
        if not impresora:
            return jsonify({"error": "Detalles de la impresora no encontrados"}), 404
            
        # Combinar datos
        impresora_data = impresora_schema.dump(impresora)
        impresora_data.update({
            "id_inventario": inventario.id_inventario,
            "estado": inventario.estado,
            "id_usuario_responsable": inventario.id_usuario_responsable,
            "id_area_responsable": inventario.id_area_responsable,
            "id_sucursal_ubicacion": inventario.id_sucursal_ubicacion,
            "fecha_ingreso": inventario.fecha_ingreso.isoformat() if inventario.fecha_ingreso else None,
            "observaciones": inventario.observaciones
        })
        
        return jsonify(impresora_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@impresoras_bp.route('/', methods=['POST'])
@jwt_required()
def add_impresora():
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar si es admin o tiene permisos para crear
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para agregar impresoras"}), 403
            
        data = request.get_json()
        
        # Crear el registro de la impresora
        nueva_impresora = Impresora(
            codigo_interno=data.get('codigo_interno'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            tipo_conexion=data.get('tipo_conexion'),
            ip_asignada=data.get('ip_asignada'),
            serial_number=data.get('serial_number'),
            observaciones=data.get('observaciones_tecnicas')
        )
        
        db.session.add(nueva_impresora)
        db.session.flush()  # Para obtener el ID generado
        
        # Crear el registro en inventario general
        nuevo_inventario = InventarioGeneral(
            tipo_equipo='Impresora',
            id_registro=nueva_impresora.id_impresora,
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
            "mensaje": "Impresora agregada correctamente",
            "id_impresora": nueva_impresora.id_impresora,
            "id_inventario": nuevo_inventario.id_inventario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@impresoras_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_impresora(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar permisos
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para editar impresoras"}), 403
            
        # Verificar que la impresora exista
        impresora = Impresora.query.get(id)
        if not impresora:
            return jsonify({"error": "Impresora no encontrada"}), 404
            
        # Buscar el registro en inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Impresora',
            id_registro=id
        ).first()
        
        if not inventario:
            return jsonify({"error": "Registro de inventario no encontrado"}), 404
            
        data = request.get_json()
        
        # Actualizar la impresora
        if 'codigo_interno' in data:
            impresora.codigo_interno = data['codigo_interno']
        if 'marca' in data:
            impresora.marca = data['marca']
        if 'modelo' in data:
            impresora.modelo = data['modelo']
        if 'tipo_conexion' in data:
            impresora.tipo_conexion = data['tipo_conexion']
        if 'ip_asignada' in data:
            impresora.ip_asignada = data['ip_asignada']
        if 'serial_number' in data:
            impresora.serial_number = data['serial_number']
        if 'observaciones_tecnicas' in data:
            impresora.observaciones = data['observaciones_tecnicas']
            
        # Actualizar inventario
        if 'estado' in data:
            inventario.estado = data['estado']
        if 'id_usuario_responsable' in data:
            # Registrar cambio de responsable en el historial
            if inventario.id_usuario_responsable != data['id_usuario_responsable']:
                historial = HistorialMovimiento(
                    tipo_equipo='Impresora',
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
        
        return jsonify({"mensaje": "Impresora actualizada correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@impresoras_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_impresora(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar permisos de administrador
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para eliminar impresoras"}), 403
            
        # Buscar la impresora
        impresora = Impresora.query.get(id)
        if not impresora:
            return jsonify({"error": "Impresora no encontrada"}), 404
            
        # Buscar el registro en inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Impresora',
            id_registro=id
        ).first()
        
        if inventario:
            db.session.delete(inventario)
            
        db.session.delete(impresora)
        db.session.commit()
        
        return jsonify({"mensaje": "Impresora eliminada correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
