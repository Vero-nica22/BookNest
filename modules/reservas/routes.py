
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify
from utils import requiere_rol
from modules.reservas import services
from modules.reservas.services import ReservaError
import mysql.connector
from config import DB_CONFIG

reservas_bp = Blueprint('reservas', __name__)

def _get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def _obtener_libro(id_libro: int):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros WHERE id_libro = %s", (id_libro,))
    libro = cursor.fetchone()
    cursor.close()
    conn.close()
    return libro


def _obtener_usuario(id_usuario: int):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario


def _get_request_data():
    data = request.get_json(silent=True)
    return data if data is not None else request.form


def _check_api_roles(*roles):
    rol_actual = session.get('rol', '')
    if rol_actual is None:
        rol_actual = ''
    rol_actual = rol_actual.strip().lower()
    roles_permitidos = [r.strip().lower() for r in roles]
    if not rol_actual or rol_actual not in roles_permitidos:
        return jsonify({'error': 'No autorizado', 'required_roles': roles_permitidos}), 401
    return None


def _serializar_reservas(reservas):
    from datetime import timedelta
    
    resultado = []
    for reserva in reservas:
        reserva_dict = dict(reserva) if hasattr(reserva, 'items') else reserva
        for clave, valor in reserva_dict.items():
            if valor is not None:
                if isinstance(valor, timedelta):
                    reserva_dict[clave] = str(valor)
                elif hasattr(valor, 'isoformat'):
                    reserva_dict[clave] = valor.isoformat()
        resultado.append(reserva_dict)
    return resultado


def _serializar_datos(datos):
    from datetime import datetime, time, timedelta
    
    if isinstance(datos, dict):
        resultado = {}
        for clave, valor in datos.items():
            resultado[clave] = _serializar_datos(valor)
        return resultado
    elif isinstance(datos, list):
        resultado = []
        for item in datos:
            if isinstance(item, dict):
                item_dict = dict(item) if hasattr(item, 'items') else item
                for clave, valor in item_dict.items():
                    if valor is not None:
                        if isinstance(valor, timedelta):
                            item_dict[clave] = str(valor)
                        elif hasattr(valor, 'isoformat'):
                            item_dict[clave] = valor.isoformat()
                resultado.append(item_dict)
            else:
                resultado.append(_serializar_datos(item))
        return resultado
    elif isinstance(datos, timedelta):
        return str(datos)
    elif hasattr(datos, 'isoformat'):
        return datos.isoformat()
    else:
        return datos


@reservas_bp.route('/api/libros', methods=['GET'])
def api_listar_libros():
    error = _check_api_roles('cliente', 'gerente', 'administrador')
    if error:
        return error

    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    conn.close()
    libros_serializados = _serializar_datos(libros)
    return jsonify({'libros': libros_serializados})


@reservas_bp.route('/api/libro/<int:id_libro>', methods=['GET'])
def api_obtener_libro(id_libro: int):
    error = _check_api_roles('cliente', 'gerente', 'administrador')
    if error:
        return error

    libro = _obtener_libro(id_libro)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    libro_serializado = _serializar_datos(libro)
    return jsonify({'libro': libro_serializado})


@reservas_bp.route('/api/mis-reservas', methods=['GET'])
def api_mis_reservas():
    error = _check_api_roles('cliente')
    if error:
        return error

    id_usuario = session.get('usuario_id')
    if not id_usuario:
        return jsonify({'error': 'No autenticado'}), 401

    lista = services.obtener_mis_reservas(id_usuario)
    lista_serializada = _serializar_reservas(lista)
    return jsonify({'reservas': lista_serializada})


@reservas_bp.route('/api/crear/<int:id_libro>', methods=['POST'])
def api_crear_reserva(id_libro: int):
    error = _check_api_roles('cliente', 'gerente', 'administrador')
    if error:
        return error

    id_usuario = session.get('usuario_id')
    if not id_usuario:
        return jsonify({'error': 'No autenticado'}), 401

    data = _get_request_data()
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')

    if not fecha or not hora_inicio or not hora_fin:
        return jsonify({'error': 'Faltan datos: fecha, hora_inicio y hora_fin son requeridos.'}), 400

    try:
        services.crear_reserva(id_usuario, id_libro, fecha, hora_inicio, hora_fin)
        return jsonify({'message': 'Reserva creada exitosamente.'}), 201
    except ReservaError as e:
        return jsonify({'error': str(e)}), 400


@reservas_bp.route('/api/cancelar/<int:id_reserva>', methods=['POST'])
def api_cancelar_reserva(id_reserva: int):
    error = _check_api_roles('cliente')
    if error:
        return error

    try:
        services.cancelar_reserva_cliente(id_reserva)
        return jsonify({'message': 'Reserva cancelada.'}), 200
    except ReservaError as e:
        return jsonify({'error': str(e)}), 400


@reservas_bp.route('/api/gestion', methods=['GET'])
def api_gestion_reservas():
    error = _check_api_roles('gerente', 'administrador')
    if error:
        return error

    filtro_estado = request.args.get('estado', 'todos')
    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_libro = request.args.get('libro', '').strip()

    lista = services.obtener_reservas_filtradas(filtro_estado, filtro_usuario, filtro_libro)
    lista_serializada = _serializar_reservas(lista)
    return jsonify({'reservas': lista_serializada})


@reservas_bp.route('/api/gestion/actualizar/<int:id_reserva>', methods=['POST'])
def api_actualizar_estado(id_reserva: int):
    error = _check_api_roles('gerente', 'administrador')
    if error:
        return error

    data = _get_request_data()
    nuevo_estado = data.get('estado')
    if not nuevo_estado:
        return jsonify({'error': 'El campo estado es requerido.'}), 400

    try:
        services.cambiar_estado_reserva(id_reserva, nuevo_estado)
        return jsonify({'message': f"Reserva actualizada a '{nuevo_estado}'."}), 200
    except ReservaError as e:
        return jsonify({'error': str(e)}), 400


@reservas_bp.route('/api/confirmadas', methods=['GET'])
def api_reservas_confirmadas():
    error = _check_api_roles('gerente', 'administrador')
    if error:
        return error

    lista = services.obtener_reservas_confirmadas()
    lista_serializada = _serializar_reservas(lista)
    return jsonify({'reservas': lista_serializada})


@reservas_bp.route('/api/eliminar/<int:id_reserva>', methods=['POST'])
def api_eliminar_reserva(id_reserva: int):
    error = _check_api_roles('administrador')
    if error:
        return error

    try:
        services.eliminar_reserva(id_reserva)
        return jsonify({'message': 'Reserva eliminada.'}), 200
    except ReservaError as e:
        return jsonify({'error': str(e)}), 400


@reservas_bp.route('/api/estadisticas', methods=['GET'])
def api_estadisticas():
    error = _check_api_roles('administrador')
    if error:
        return error

    datos = services.obtener_estadisticas()
    datos_serializados = _serializar_datos(datos)
    return jsonify(datos_serializados)

@reservas_bp.route('/', methods=['GET'])
@requiere_rol('cliente', 'gerente', 'administrador')
def listar_libros_reservables():
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reservas.html', libros=libros)


@reservas_bp.route('/formulario/<int:id_libro>', methods=['GET'])
@requiere_rol('cliente', 'gerente', 'administrador')
def formulario_reserva(id_libro: int):
    id_usuario = session['usuario_id']
    usuario = _obtener_usuario(id_usuario)
    libro = _obtener_libro(id_libro)

    if not libro:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('reservas.listar_libros_reservables'))

    return render_template('formulario_reserva.html', usuario=usuario, libro=libro)


@reservas_bp.route('/crear/<int:id_libro>', methods=['POST'])
@requiere_rol('cliente', 'gerente', 'administrador')
def crear_reserva(id_libro: int):
    id_usuario = session['usuario_id']
    rol = session.get('rol')

    fecha = request.form['fecha']
    hora_inicio = request.form['hora_inicio']
    hora_fin = request.form['hora_fin']

    try:
        services.crear_reserva(id_usuario, id_libro, fecha, hora_inicio, hora_fin)
        flash("Reserva creada exitosamente.", "success")
    except ReservaError as e:
        flash(str(e), "error")
        return redirect(url_for('reservas.formulario_reserva', id_libro=id_libro))

    if rol in ('gerente', 'administrador'):
        return redirect(url_for('reservas.gestion_reservas'))
    return redirect(url_for('reservas.mis_reservas'))


@reservas_bp.route('/mis-reservas', methods=['GET'])
@requiere_rol('cliente')
def mis_reservas():
    id_usuario = session['usuario_id']
    lista = services.obtener_mis_reservas(id_usuario)
    return render_template('mis_reservas.html', reservas=lista)


@reservas_bp.route('/cancelar/<int:id_reserva>', methods=['POST'])
@requiere_rol('cliente')
def cancelar_reserva(id_reserva: int):
    services.cancelar_reserva_cliente(id_reserva)
    flash("Reserva cancelada.", "info")
    return redirect(url_for('reservas.mis_reservas'))


@reservas_bp.route('/gestion', methods=['GET'])
@requiere_rol('gerente', 'administrador')
def gestion_reservas():
    filtro_estado  = request.args.get('estado',  'todos')
    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_libro   = request.args.get('libro',   '').strip()

    lista = services.obtener_reservas_filtradas(filtro_estado, filtro_usuario, filtro_libro)

    return render_template('reservas_gerente.html',
                            reservas=lista,
                            filtro_estado=filtro_estado,
                            filtro_usuario=filtro_usuario,
                            filtro_libro=filtro_libro)


@reservas_bp.route('/gestion/actualizar/<int:id_reserva>', methods=['POST'])
@requiere_rol('gerente', 'administrador')
def actualizar_estado(id_reserva: int):
    nuevo_estado = request.form['estado']
    try:
        services.cambiar_estado_reserva(id_reserva, nuevo_estado)
        flash(f"Reserva actualizada a '{nuevo_estado}'.", "success")
    except ReservaError as e:
        flash(str(e), "error")
    return redirect(url_for('reservas.gestion_reservas'))


@reservas_bp.route('/confirmadas', methods=['GET'])
@requiere_rol('gerente', 'administrador')
def reservas_confirmadas():
    lista = services.obtener_reservas_confirmadas()
    return render_template('reservas_confirmadas.html', reservas=lista)


@reservas_bp.route('/eliminar/<int:id_reserva>', methods=['POST'])
@requiere_rol('administrador')
def eliminar_reserva(id_reserva: int):
    services.eliminar_reserva(id_reserva)
    flash("Reserva eliminada.", "success")
    return redirect(url_for('reservas.gestion_reservas'))

@reservas_bp.route('/estadisticas', methods=['GET'])
@requiere_rol('administrador')
def estadisticas():
    datos = services.obtener_estadisticas()
    return render_template('estadisticas_admin.html', **datos)
