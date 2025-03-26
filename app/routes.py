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
                detalle = {
                    "tipo": "Computacional",
                    "codigo": equipo.codigo_interno,
                    "marca": equipo.marca,
                    "modelo": equipo.modelo,
                    "procesador": equipo.procesador,
                    "ram": equipo.ram,
                    "sistema_operativo": equipo.sistema_operativo
                }
            elif item.tipo_equipo == "Celular":
                cel = Celular.query.get(item.id_registro)
                detalle = {
                    "tipo": "Celular",
                    "codigo": cel.codigo_interno,
                    "marca": cel.marca,
                    "modelo": cel.modelo,
                    "imei": cel.imei,
                    "numero_linea": cel.numero_linea
                }
            elif item.tipo_equipo == "Impresora":
                imp = Impresora.query.get(item.id_registro)
                detalle = {
                    "tipo": "Impresora",
                    "codigo": imp.codigo_interno,
                    "marca": imp.marca,
                    "modelo": imp.modelo,
                    "ip": imp.ip_asignada
                }

            data.append({
                "id": item.id_inventario,
                "estado": item.estado,
                "fecha_ingreso": item.fecha_ingreso,
                "observaciones": item.observaciones,
                "detalle": detalle
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
