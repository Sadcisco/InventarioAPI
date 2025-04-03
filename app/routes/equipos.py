from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import (
    InventarioGeneral, EquipoComputacional, Celular, Impresora,
    Usuario, Area, Sucursal, EquipoComputacionalSchema, HistorialMovimiento
)
from datetime import datetime

equipos_bp = Blueprint('equipos', __name__)
equipo_schema = EquipoComputacionalSchema()
equipos_schema = EquipoComputacionalSchema(many=True)

# Verificar permisos por rol
def check_admin_permission(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario or usuario.id_rol != 1:  # Asumimos que rol_id 1 es Administrador
        return False
    return True

@equipos_bp.route('/', methods=['GET'])
def get_equipos():
    try:
        # Obtener todos los equipos
        equipos = db.session.query(InventarioGeneral).all()
        print(f"Se encontraron {len(equipos)} equipos")
        result = []

        for equipo in equipos:
            # Preparar el resultado base
            equipo_data = {
                'id': equipo.id_inventario,
                'tipo': equipo.tipo_equipo,
                'estado': equipo.estado,
                'fecha_ingreso': equipo.fecha_ingreso.strftime('%Y-%m-%d') if equipo.fecha_ingreso else None,
                'observaciones': equipo.observaciones
            }

            # Obtener detalles específicos según el tipo
            try:
                if equipo.tipo_equipo == 'Computacional':
                    equipo_detalle = db.session.query(EquipoComputacional).get(equipo.id_registro)
                    if equipo_detalle:
                        equipo_data['detalle'] = {
                            'codigo_interno': equipo_detalle.codigo_interno,
                            'marca': equipo_detalle.marca,
                            'modelo': equipo_detalle.modelo,
                            'procesador': equipo_detalle.procesador,
                            'ram': equipo_detalle.ram,
                            'disco_duro': equipo_detalle.disco_duro,
                            'sistema_operativo': equipo_detalle.sistema_operativo,
                            'office': equipo_detalle.office,
                            'antivirus': equipo_detalle.antivirus,
                            'drive': equipo_detalle.drive,
                            'nombre_equipo': equipo_detalle.nombre_equipo,
                            'serial_number': equipo_detalle.serial_number,
                            'fecha_revision': equipo_detalle.fecha_revision.strftime('%Y-%m-%d') if equipo_detalle.fecha_revision else None,
                            'entregado_por': equipo_detalle.entregado_por,
                            'comentarios': equipo_detalle.comentarios
                        }
                elif equipo.tipo_equipo == 'Celular':
                    equipo_detalle = db.session.query(Celular).get(equipo.id_registro)
                    if equipo_detalle:
                        equipo_data['detalle'] = {
                            'codigo_interno': equipo_detalle.codigo_interno,
                            'marca': equipo_detalle.marca,
                            'modelo': equipo_detalle.modelo,
                            'imei': equipo_detalle.imei,
                            'numero_linea': equipo_detalle.numero_linea,
                            'sistema_operativo': equipo_detalle.sistema_operativo,
                            'capacidad_almacenamiento': equipo_detalle.capacidad_almacenamiento,
                            'comentarios': equipo_detalle.comentarios
                        }
                elif equipo.tipo_equipo == 'Impresora':
                    equipo_detalle = db.session.query(Impresora).get(equipo.id_registro)
                    if equipo_detalle:
                        equipo_data['detalle'] = {
                            'codigo_interno': equipo_detalle.codigo_interno,
                            'marca': equipo_detalle.marca,
                            'modelo': equipo_detalle.modelo,
                            'tipo_conexion': equipo_detalle.tipo_conexion,
                            'ip_asignada': equipo_detalle.ip_asignada,
                            'serial_number': equipo_detalle.serial_number,
                            'observaciones': equipo_detalle.observaciones
                        }
            except Exception as e:
                print(f"Error al obtener detalles del equipo {equipo.id_inventario}: {str(e)}")
                equipo_data['detalle'] = {}

            # Obtener información del usuario responsable
            try:
                if equipo.id_usuario_responsable:
                    usuario = db.session.query(Usuario).get(equipo.id_usuario_responsable)
                    if usuario:
                        equipo_data['usuario_responsable'] = {
                            'id': usuario.id,
                            'nombre': usuario.nombre,
                            'usuario': usuario.usuario
                        }
            except Exception as e:
                print(f"Error al obtener usuario del equipo {equipo.id_inventario}: {str(e)}")

            # Obtener información del área
            try:
                if equipo.id_area_responsable:
                    area = db.session.query(Area).get(equipo.id_area_responsable)
                    if area:
                        equipo_data['area_responsable'] = {
                            'id': area.id_area,
                            'nombre': area.nombre_area
                        }
            except Exception as e:
                print(f"Error al obtener área del equipo {equipo.id_inventario}: {str(e)}")

            # Obtener información de la sucursal
            try:
                if equipo.id_sucursal_ubicacion:
                    sucursal = db.session.query(Sucursal).get(equipo.id_sucursal_ubicacion)
                    if sucursal:
                        equipo_data['sucursal'] = {
                            'id': sucursal.id_sucursal,
                            'nombre': sucursal.nombre_sucursal,
                            'direccion': sucursal.direccion,
                            'region': sucursal.region
                        }
            except Exception as e:
                print(f"Error al obtener sucursal del equipo {equipo.id_inventario}: {str(e)}")



            result.append(equipo_data)

        print(f"Se procesaron {len(result)} equipos correctamente")
        return jsonify(result)
    except Exception as e:
        print(f"Error general en get_equipos: {str(e)}")
        return jsonify({
            'error': str(e),
            'tipo': type(e).__name__,
            'detalles': getattr(e, 'args', [])
        }), 500

@equipos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_equipo(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Buscar el equipo en el inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Computacional',
            id_registro=id
        ).first()
        
        if not inventario:
            return jsonify({"error": "Equipo no encontrado"}), 404
            
        # Verificar acceso por sucursal
        usuario = Usuario.query.get(usuario_id)
        if usuario.sucursal_activa != inventario.id_sucursal_ubicacion and not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para ver este equipo"}), 403
            
        # Obtener detalles del equipo
        equipo = EquipoComputacional.query.get(id)
        if not equipo:
            return jsonify({"error": "Detalles del equipo no encontrados"}), 404
            
        # Combinar datos
        equipo_data = equipo_schema.dump(equipo)
        equipo_data.update({
            "id_inventario": inventario.id_inventario,
            "estado": inventario.estado,
            "id_usuario_responsable": inventario.id_usuario_responsable,
            "id_area_responsable": inventario.id_area_responsable,
            "id_sucursal_ubicacion": inventario.id_sucursal_ubicacion,
            "fecha_ingreso": inventario.fecha_ingreso.isoformat() if inventario.fecha_ingreso else None,
            "observaciones": inventario.observaciones
        })
        
        return jsonify(equipo_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@equipos_bp.route('/', methods=['POST'])
@jwt_required()
def add_equipo():
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar si es admin o tiene permisos para crear
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para agregar equipos"}), 403
            
        data = request.get_json()
        
        # Crear el registro del equipo
        nuevo_equipo = EquipoComputacional(
            codigo_interno=data.get('codigo_interno'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            procesador=data.get('procesador'),
            ram=data.get('ram'),
            disco_duro=data.get('disco_duro'),
            sistema_operativo=data.get('sistema_operativo'),
            office=data.get('office'),
            antivirus=data.get('antivirus'),
            drive=data.get('drive'),
            nombre_equipo=data.get('nombre_equipo'),
            serial_number=data.get('serial_number'),
            fecha_revision=datetime.strptime(data.get('fecha_revision'), '%Y-%m-%d') if data.get('fecha_revision') else None,
            entregado_por=data.get('entregado_por'),
            comentarios=data.get('comentarios')
        )
        
        db.session.add(nuevo_equipo)
        db.session.flush()  # Para obtener el ID generado
        
        # Crear el registro en inventario general
        nuevo_inventario = InventarioGeneral(
            tipo_equipo='Computacional',
            id_registro=nuevo_equipo.id_equipo,
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
            "mensaje": "Equipo agregado correctamente",
            "id_equipo": nuevo_equipo.id_equipo,
            "id_inventario": nuevo_inventario.id_inventario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@equipos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_equipo(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar permisos
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para editar equipos"}), 403
            
        # Verificar que el equipo exista
        equipo = EquipoComputacional.query.get(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
            
        # Buscar el registro en inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Computacional',
            id_registro=id
        ).first()
        
        if not inventario:
            return jsonify({"error": "Registro de inventario no encontrado"}), 404
            
        data = request.get_json()
        
        # Actualizar el equipo
        if 'codigo_interno' in data:
            equipo.codigo_interno = data['codigo_interno']
        if 'marca' in data:
            equipo.marca = data['marca']
        if 'modelo' in data:
            equipo.modelo = data['modelo']
        if 'procesador' in data:
            equipo.procesador = data['procesador']
        if 'ram' in data:
            equipo.ram = data['ram']
        if 'disco_duro' in data:
            equipo.disco_duro = data['disco_duro']
        if 'sistema_operativo' in data:
            equipo.sistema_operativo = data['sistema_operativo']
        if 'office' in data:
            equipo.office = data['office']
        if 'antivirus' in data:
            equipo.antivirus = data['antivirus']
        if 'drive' in data:
            equipo.drive = data['drive']
        if 'nombre_equipo' in data:
            equipo.nombre_equipo = data['nombre_equipo']
        if 'serial_number' in data:
            equipo.serial_number = data['serial_number']
        if 'fecha_revision' in data and data['fecha_revision']:
            equipo.fecha_revision = datetime.strptime(data['fecha_revision'], '%Y-%m-%d')
        if 'entregado_por' in data:
            equipo.entregado_por = data['entregado_por']
        if 'comentarios' in data:
            equipo.comentarios = data['comentarios']
            
        # Actualizar inventario
        if 'estado' in data:
            inventario.estado = data['estado']
        if 'id_usuario_responsable' in data:
            # Registrar cambio de responsable en el historial
            if inventario.id_usuario_responsable != data['id_usuario_responsable']:
                historial = HistorialMovimiento(
                    tipo_equipo='Computacional',
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
        
        return jsonify({"mensaje": "Equipo actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@equipos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_equipo(id):
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar permisos de administrador
        if not check_admin_permission(usuario_id):
            return jsonify({"error": "No tienes permiso para eliminar equipos"}), 403
            
        # Buscar el equipo
        equipo = EquipoComputacional.query.get(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
            
        # Buscar el registro en inventario
        inventario = InventarioGeneral.query.filter_by(
            tipo_equipo='Computacional',
            id_registro=id
        ).first()
        
        if inventario:
            db.session.delete(inventario)
            
        db.session.delete(equipo)
        db.session.commit()
        
        return jsonify({"mensaje": "Equipo eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
