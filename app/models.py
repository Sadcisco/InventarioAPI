from . import db

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
    id_usuario_responsable = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    id_area_responsable = db.Column(db.Integer, db.ForeignKey('areas.id_area'))
    id_sucursal_ubicacion = db.Column(db.Integer, db.ForeignKey('sucursales.id_sucursal'))
    fecha_ingreso = db.Column(db.Date)
    observaciones = db.Column(db.Text)

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

