from flask import Blueprint, jsonify
from .models import InventarioGeneral, EquipoComputacional, Celular, Impresora
from . import db

api = Blueprint('api', __name__)

@api.route("/inventario", methods=["GET"])
def get_inventario_general():
    try:
        inventario = InventarioGeneral.query.all()
        data = []

        for item in inventario:
            detalle = {}
            if item.tipo_equipo == "Computacional":
                equipo = EquipoComputacional.query.get(item.id_registro)
                if equipo:
                    detalle = {
                        "tipo": "Computacional",
                        "codigo": equipo.codigo_interno,
                        "marca": equipo.marca,
                        "modelo": equipo.modelo,
                        "procesador": equipo.procesador,
                        "ram": equipo.ram,
                        "disco_duro": equipo.disco_duro,
                        "sistema_operativo": equipo.sistema_operativo,
                        "office": equipo.office,
                        "antivirus": equipo.antivirus,
                        "drive": equipo.drive,
                        "nombre_equipo": equipo.nombre_equipo,
                        "serial_number": equipo.serial_number,
                        "fecha_revision": equipo.fecha_revision.isoformat() if equipo.fecha_revision else None,
                        "entregado_por": equipo.entregado_por,
                        "comentarios": equipo.comentarios
                    }
                else:
                    detalle = {
                        "tipo": "Computacional",
                        "error": f"Equipo ID {item.id_registro} no encontrado en tabla 'equipos_computacionales'"
                    }

            elif item.tipo_equipo == "Celular":
                cel = Celular.query.get(item.id_registro)
                if cel:
                    detalle = {
                        "tipo": "Celular",
                        "codigo": cel.codigo_interno,
                        "marca": cel.marca,
                        "modelo": cel.modelo,
                        "imei": cel.imei,
                        "numero_linea": cel.numero_linea
                    }
                else:
                    detalle = {
                        "tipo": "Celular",
                        "error": f"Celular ID {item.id_registro} no encontrado"
                    }

            elif item.tipo_equipo == "Impresora":
                imp = Impresora.query.get(item.id_registro)
                if imp:
                    detalle = {
                        "tipo": "Impresora",
                        "codigo": imp.codigo_interno,
                        "marca": imp.marca,
                        "modelo": imp.modelo,
                        "ip": imp.ip_asignada
                    }
                else:
                    detalle = {
                        "tipo": "Impresora",
                        "error": f"Impresora ID {item.id_registro} no encontrada"
                    }

            data.append({
                "id": item.id_inventario,
                "estado": item.estado,
                "fecha_ingreso": item.fecha_ingreso.isoformat() if item.fecha_ingreso else None,
                "observaciones": item.observaciones,
                "detalle": detalle
            })

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
