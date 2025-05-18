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
    user="",
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
        cursor.close()
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
        cursor.close()

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
            flash("Credenciales incorrectas", "error")
            return render_template('login.html')
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

        filename = None
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            imagen.save(imagen_path)

        cursor.execute("INSERT INTO productos (nombre, descripcion, imagen_nombre) VALUES (%s, %s, %s)",
                    (nombre, descripcion, filename))
        db.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('auth.productos'))

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    return render_template('productos_admi.html', productos=productos)

@auth.route('/eliminar_producto/<int:id_producto>', methods=['POST'])
@requiere_rol('administrador')
def eliminar_producto(id_producto):
    cursor = db.cursor(dictionary=True)

    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    db.commit()
    cursor.close()

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
    cursor.close()
    return render_template('actualizar_producto.html', producto=producto)


@auth.route('/libros', methods=['GET', 'POST'])
@requiere_rol('administrador')
def libros():
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        sinopsis = request.form.get('sinopsis', '')
        imagen = request.files.get('imagen')

        filename = None
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            imagen.save(imagen_path)

        cursor.execute("""
            INSERT INTO libros (titulo, autor, sinopsis, imagen) VALUES (%s, %s, %s, %s)
        """, (titulo, autor, sinopsis, filename))
        db.commit()
        flash('Libro agregado exitosamente', 'success')
        return redirect(url_for('auth.libros'))

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    return render_template('libros.html', libros=libros)

@auth.route('/eliminar_libro/<int:id>', methods=['POST'])
@requiere_rol('administrador')
def eliminar_libro(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM libros WHERE id_libro = %s", (id,))
    db.commit()
    cursor.close()
    flash('Libro eliminado', 'success')
    return redirect(url_for('auth.libros'))

@auth.route('/actualizar_libro/<int:id_libro>', methods=['POST'])
def actualizar_libro(id_libro):
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        sinopsis = request.form['sinopsis']
        imagen_nueva = request.files.get('imagen')
        filename = None

        if imagen_nueva and allowed_file(imagen_nueva.filename):
            filename = secure_filename(imagen_nueva.filename)
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            imagen_nueva.save(imagen_path)

        cursor = db.cursor()
        if filename:
            cursor.execute("""
                UPDATE libros
                SET titulo = %s, autor = %s, sinopsis = %s,
                    imagen = %s
                WHERE id_libro = %s
            """, (titulo, autor, sinopsis, filename, id_libro))
        else:
            cursor.execute("""
                UPDATE libros
                SET titulo = %s, autor = %s, sinopsis = %s
                WHERE id_libro = %s
            """, (titulo, autor, sinopsis, id_libro))

        db.commit()
        cursor.close()
        flash('Libro actualizado exitosamente', 'success')
    return redirect(url_for('auth.libros'))

@auth.route('/editar_libro/<int:id_libro>', methods=['GET'])
@requiere_rol('administrador')
def editar_libro(id_libro):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros WHERE id_libro = %s", (id_libro,))
    libro = cursor.fetchone()
    cursor.close()
    if not libro:
        flash('Libro no encontrado', 'error')
        return redirect(url_for('auth.libros'))
    return render_template('editar_libro.html', libro=libro)