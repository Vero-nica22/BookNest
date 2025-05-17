from flask import Blueprint, render_template, request, redirect, session, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import DB_CONFIG
from utils import requiere_rol
import os
from werkzeug.utils import secure_filename

db = mysql.connector.connect(**DB_CONFIG)
auth = Blueprint('auth', __name__)


db = mysql.connector.connect(
    host="localhost",
    user="usuario",
    password="",
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
    print("Cargando menu_administrador.html")  
    return render_template('menu_administrador.html')

@auth.route('/menu_gerente')
@requiere_rol('gerente')
def menu_gerente():
    print("Cargando menu_gerente.html")  
    return render_template('menu_gerente.html')



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/productos', methods=['GET', 'POST'])
@requiere_rol('administrador')
def productos():
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        imagen = request.files['imagen']

        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)  
            imagen.save(imagen_path)
        else:
            filename = None

        cursor.execute("INSERT INTO productos (nombre, descripcion, imagen_nombre) VALUES (%s, %s, %s)", 
                    (nombre, descripcion, filename))
        db.commit()

        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('auth.productos'))

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    return render_template('productos_admi.html', productos=productos)


@auth.route('/eliminar_producto/<int:id_producto>', methods=['POST'])
@requiere_rol('administrador')
def eliminar_producto(id_producto):
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    db.commit()
    
    flash('Success', 'El producto fue eliminado')
    
    return redirect(url_for('auth.productos')) 

@auth.route('/actualizar_producto/<int:id>', methods=['GET', 'POST'])
@requiere_rol('administrador')
def actualizar_producto(id):
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        imagen_url = request.form['imagen_url']

        cursor.execute("""
            UPDATE productos 
            SET nombre = %s, descripcion = %s, imagen_url = %s 
            WHERE id_producto = %s
        """, (nombre, descripcion, imagen_url, id))
        db.commit()
        flash('Producto actualizado con éxito', 'success')
        return redirect(url_for('auth.productos'))

    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    return render_template('actualizar_producto.html', producto=producto)




