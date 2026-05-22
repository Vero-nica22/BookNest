from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import DB_CONFIG
from utils import requiere_rol
from flask import redirect, url_for, session
from flask import request
import os
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


@auth.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or request.form
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    if not correo or not contrasena:
        return jsonify({'error': 'Correo y contraseña son requeridos.'}), 400

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
        return jsonify({'message': 'Autenticación exitosa.', 'rol': usuario['nombre_rol']}), 200

    return jsonify({'error': 'Credenciales incorrectas.'}), 401

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

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


#@auth.route('/libros')
#@requiere_rol('gerente', 'administrador')
#def libros():
#    return redirect(url_for('reservas.listar_libros_reservables'))

@auth.route('/libros', methods=['GET', 'POST'])
@requiere_rol('gerente', 'administrador')
def libros():
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        sinopsis = request.form['sinopsis']
        imagen = request.files['imagen']
        nombre_imagen = imagen.filename        
        cursor.execute(
            "INSERT INTO libros (titulo, autor, sinopsis, imagen) VALUES (%s, %s, %s, %s)",
            (titulo, autor, sinopsis, nombre_imagen)
        )
        db.commit()

        return redirect(url_for('auth.libros'))

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('libros.html', libros=libros)


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

@auth.route('/eliminar_libro/<int:id_libro>', methods=['POST'])
@requiere_rol('administrador')
def eliminar_libro(id_libro):
    cursor = db.cursor()
    cursor.execute("DELETE FROM libros WHERE id_libro = %s", (id_libro,))
    db.commit()
    cursor.close()
    flash('Libro eliminado correctamente', 'success')
    return redirect(url_for('auth.libros'))

@auth.route('/libros_cliente')
@requiere_rol('cliente', 'administrador', 'gerente') 
def libros_cliente():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    return render_template('libros_cliente.html', libros=libros)

@auth.route('/libro/<int:id_libro>', methods=['GET', 'POST'])
@requiere_rol('cliente', 'administrador', 'gerente')  
def detalle_libro(id_libro):
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        comentario = request.form['comentario']
        calificacion = request.form['calificacion']
        id_cliente = session.get('usuario_id')

        if not id_cliente:
            flash('Debes iniciar sesión para dejar una reseña.', 'error')
            return redirect(url_for('auth.login'))

        cursor.execute("""
            INSERT INTO resenas (id_libro, id_cliente, comentario, calificacion)
            VALUES (%s, %s, %s, %s)
        """, (id_libro, id_cliente, comentario, calificacion))
        db.commit()
        flash('¡Reseña enviada!', 'success')
        return redirect(url_for('auth.detalle_libro', id_libro=id_libro))

    cursor.execute("SELECT * FROM libros WHERE id_libro = %s", (id_libro,))
    libro = cursor.fetchone()

    cursor.execute("""
        SELECT r.comentario, r.calificacion, r.fecha, u.nombre
        FROM resenas r
        JOIN usuarios u ON r.id_cliente = u.id_usuario
        WHERE r.id_libro = %s
        ORDER BY r.fecha DESC
    """, (id_libro,))
    resenas = cursor.fetchall()
    cursor.close()

    return render_template('detalle_libro.html', libro=libro, resenas=resenas)

@auth.route('/gestion_reservas')
@requiere_rol('gerente', 'administrador')
def gestion_reservas_redirect():
    return redirect(url_for('reservas.gestion_reservas'))


@auth.route('/estadisticas')
@requiere_rol('administrador')
def estadisticas_redirect():
    return redirect(url_for('reservas.estadisticas'))


@auth.route('/productos', methods=['GET', 'POST'])
@requiere_rol('gerente', 'administrador')
def productos():
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        imagen = request.files.get('imagen')

        if imagen and imagen.filename != '':
            imagen_nombre = imagen.filename
            imagen.save(os.path.join('static/uploads', imagen_nombre))
        else:
            imagen_nombre = None

        cursor.execute("INSERT INTO productos (nombre, descripcion, imagen_nombre) VALUES (%s, %s, %s)", 
                    (nombre, descripcion, imagen_nombre))
        db.commit()
        flash('Producto agregado exitosamente', 'success')
        
        return redirect(url_for('auth.productos'))

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    return render_template('productos_admi.html', productos=productos)

@auth.route('/ver_productos')
@requiere_rol('cliente', 'gerente', 'administrador')
def ver_productos():
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('productos.html', productos=productos)

@auth.route('/eliminar_producto/<int:id_producto>', methods=['POST'])
@requiere_rol('gerente', 'administrador')
def eliminar_producto(id_producto):
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    db.commit()
    
    flash('Success', 'El producto fue eliminado')
    
    return redirect(url_for('auth.productos')) 

@auth.route('/actualizar_producto/<int:id>', methods=['GET', 'POST'])
@requiere_rol('gerente', 'administrador')
def actualizar_producto(id):
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        imagen = request.files.get('imagen')

        if imagen and imagen.filename != '':
            imagen_nombre = imagen.filename
            imagen.save(os.path.join('static/uploads', imagen_nombre))

        cursor.execute("""
            UPDATE productos 
            SET nombre = %s, descripcion = %s, imagen_nombre = %s 
            WHERE id_producto = %s
        """, (nombre, descripcion, imagen_nombre, id))
        db.commit()
        flash('Producto actualizado con éxito', 'success')
        return redirect(url_for('auth.productos'))

    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    return render_template('actualizar_producto.html', producto=producto)
