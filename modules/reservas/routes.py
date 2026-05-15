
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
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

@reservas_bp.route('/', methods=['GET'])
@requiere_rol('cliente')
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
    lista = services.obtener_reservas_pendientes()
    return render_template('gestion_reservas.html', reservas=lista)


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
