from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import DB_CONFIG
from utils import requiere_rol
db = mysql.connector.connect(**DB_CONFIG)


auth = Blueprint('auth', __name__)


db = mysql.connector.connect(
    host="localhost",
    user="miusuario",
    password="22",
    database="booknest"
)

@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = None
    mensaje_class = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        documento = request.form['documento']
        celular = request.form['celular']
        correo = request.form['correo']
        contrasena = generate_password_hash(request.form['contrasena'])

        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (nombre, apellido, documento_identidad, celular, correo, contrasena)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, apellido, documento, celular, correo, contrasena))
            db.commit()
            mensaje = "¡Registro exitoso!"
            mensaje_class = "exito"
        except mysql.connector.Error as err:
            mensaje = f"Error: {err}"
            mensaje_class = "error"
    return render_template('register.html', mensaje=mensaje, mensaje_class=mensaje_class)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT usuarios.id_usuario, usuarios.contrasena, roles.nombre_rol
            FROM usuarios
            INNER JOIN roles ON usuarios.id_rol = roles.id_rol
            WHERE usuarios.correo = %s
        """, (correo,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario['contrasena'], contrasena):
            
            session['usuario_id'] = usuario['id_usuario']
            session['rol'] = usuario['nombre_rol']


            if usuario['nombre_rol'] == 'cliente':
                return redirect('/menu_cliente')
            elif usuario['nombre_rol'] == 'administrador':
                return redirect('/menu_administrador')
            elif usuario['nombre_rol'] == 'gerente':
                return redirect('/menu_gerente')
        else:
            return "Credenciales incorrectas"
    return render_template('login.html')
@auth.route('/menu_cliente')
@requiere_rol('cliente')
def menu_cliente():
    print("Cargando menu_cliente.html")  
    return render_template('menu_cliente.html')

@auth.route('/menu_administrador')
@requiere_rol('administrador')
def menu_administrador():
    print("Cargando menu_administrador.html")  # Depuración
    return render_template('menu_administrador.html')

@auth.route('/menu_gerente')
@requiere_rol('gerente')
def menu_gerente():
    print("Cargando menu_gerente.html")  # Depuración
    return render_template('menu_gerente.html')
