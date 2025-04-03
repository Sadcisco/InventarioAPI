from . import db
from datetime import datetime
from flask_marshmallow import Marshmallow
import bcrypt

ma = Marshmallow()

class Usuario(db.Model):
    __tablename__ = 'usuarios_sistema'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contraseña_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100))
    id_sucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id_sucursal'))
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    sucursal = db.relationship('Sucursal', foreign_keys=[id_sucursal], backref='usuarios')

    def set_password(self, password):
        self.contraseña_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.contraseña_hash.encode('utf-8'))

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))

class Area(db.Model):
    __tablename__ = 'areas'
    id_area = db.Column(db.Integer, primary_key=True)
    nombre_area = db.Column(db.String(100), nullable=False)

class Sucursal(db.Model):
    __tablename__ = 'sucursales'
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre_sucursal = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255))
    region = db.Column(db.String(100))
    telefono_contacto = db.Column(db.String(50))

class InventarioGeneral(db.Model):
    __tablename__ = 'inventario_general'
    id_inventario = db.Column(db.Integer, primary_key=True)
    tipo_equipo = db.Column(db.Enum('Computacional', 'Celular', 'Impresora'), nullable=False)
    id_registro = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Enum('DeBaja', 'Asignado', 'SinAsignar', 'EnReparacion'), default='SinAsignar')
    id_usuario_responsable = db.Column(db.Integer, db.ForeignKey('usuarios_sistema.id'))
    id_area_responsable = db.Column(db.Integer, db.ForeignKey('areas.id_area'))
    id_sucursal_ubicacion = db.Column(db.Integer, db.ForeignKey('sucursales.id_sucursal'))
    fecha_ingreso = db.Column(db.Date)
    observaciones = db.Column(db.Text)

    # Relaciones
    usuario_responsable = db.relationship('Usuario', backref='equipos_asignados')
    area_responsable = db.relationship('Area', backref='equipos_asignados')
    sucursal = db.relationship('Sucursal', backref='equipos_ubicados')

class EquipoComputacional(db.Model):
    __tablename__ = 'equipos_computacionales'
    id_equipo = db.Column(db.Integer, primary_key=True)
    codigo_interno = db.Column(db.String(50), unique=True, nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    procesador = db.Column(db.String(100))
    ram = db.Column(db.String(50))
    disco_duro = db.Column(db.String(100))
    sistema_operativo = db.Column(db.String(100))
    office = db.Column(db.String(100))
    antivirus = db.Column(db.String(100))
    drive = db.Column(db.String(100))
    nombre_equipo = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    fecha_revision = db.Column(db.Date)
    entregado_por = db.Column(db.String(100))
    comentarios = db.Column(db.Text)

class Celular(db.Model):
    __tablename__ = 'celulares'
    id_celular = db.Column(db.Integer, primary_key=True)
    codigo_interno = db.Column(db.String(50), unique=True, nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    imei = db.Column(db.String(50))
    numero_linea = db.Column(db.String(20))
    sistema_operativo = db.Column(db.String(100))
    capacidad_almacenamiento = db.Column(db.String(50))
    comentarios = db.Column(db.Text)

class Impresora(db.Model):
    __tablename__ = 'impresoras'
    id_impresora = db.Column(db.Integer, primary_key=True)
    codigo_interno = db.Column(db.String(50), unique=True, nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    tipo_conexion = db.Column(db.String(50))
    ip_asignada = db.Column(db.String(50))
    serial_number = db.Column(db.String(100))
    observaciones = db.Column(db.Text)

class Consumible(db.Model):
    __tablename__ = 'consumibles'
    id_consumible = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('Toner', 'Tambor'), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    id_sucursal_stock = db.Column(db.Integer, db.ForeignKey('sucursales.id_sucursal'))
    
    # Relación
    sucursal = db.relationship('Sucursal', backref='consumibles')

class HistorialMovimiento(db.Model):
    __tablename__ = 'historial_movimientos'
    id = db.Column(db.Integer, primary_key=True)
    tipo_equipo = db.Column(db.String(50), nullable=False)
    id_equipo = db.Column(db.Integer, nullable=False)
    responsable_anterior = db.Column(db.Integer, db.ForeignKey('usuarios_sistema.id'))
    responsable_nuevo = db.Column(db.Integer, db.ForeignKey('usuarios_sistema.id'))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text)

# Schemas para serialización
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        exclude = ('contraseña_hash',)

class RolSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rol

class AreaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Area

class SucursalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sucursal

class EquipoComputacionalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EquipoComputacional

class CelularSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Celular

class ImpresoraSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Impresora

class ConsumibleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Consumible

class HistorialMovimientoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HistorialMovimiento
