from flask import Blueprint, render_template, request, redirect, session, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import DB_CONFIG
from utils import requiere_rol
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

db = mysql.connector.connect(**DB_CONFIG)
auth = Blueprint('auth', __name__)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
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

@auth.route('/ver_productos', methods=['GET'])
@requiere_rol('cliente', 'gerente') 
def ver_productos():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    return render_template('productos.html', productos=productos)


@auth.route('/libros', methods=['GET', 'POST'])
@requiere_rol('administrador', 'gerente')
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


@auth.route('/reservas', methods=['GET'])
@requiere_rol('cliente')
def reservas():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    return render_template('reservas.html', libros=libros)



@auth.route('/formulario_reserva/<int:id_libro>', methods=['GET'])
def formulario_reserva(id_libro):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para reservar un libro', 'error')
        return redirect(url_for('auth.login'))

    id_usuario = session['usuario_id']

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()

    
    cursor.execute("SELECT * FROM libros WHERE id_libro = %s", (id_libro,))
    libro = cursor.fetchone()
    cursor.close()

    return render_template('formulario_reserva.html', usuario=usuario, libro=libro)



@auth.route('/crear_reserva/<int:id_libro>', methods=['POST'])
@requiere_rol(('cliente', 'gerente', 'administrador'))
def crear_reserva(id_libro):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para reservar', 'error')
        return redirect(url_for('auth.login'))

    id_usuario = session['usuario_id']

    fecha = request.form['fecha']
    hora_inicio = request.form['hora_inicio']
    hora_fin = request.form['hora_fin']

    
    fmt = "%H:%M"
    try:
        inicio = datetime.strptime(hora_inicio, fmt)
        fin = datetime.strptime(hora_fin, fmt)
    except ValueError:
        flash("Formato de hora inválido. Usa HH:MM.", "error")
        return redirect(url_for('auth.formulario_reserva', id_libro=id_libro))

    if (fin - inicio) > timedelta(hours=4) or (fin <= inicio):
        flash("La duración máxima de una reserva es de 4 horas y la hora de fin debe ser posterior a la de inicio.", "error")
        return redirect(url_for('auth.formulario_reserva', id_libro=id_libro))

    
    cursor = db.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM reservas
        WHERE id_libro = %s AND fecha_reserva = %s AND estado IN ('pendiente', 'confirmada')
        AND (
            (hora_inicio < %s AND hora_fin > %s) OR
            (hora_inicio < %s AND hora_fin > %s) OR
            (hora_inicio >= %s AND hora_fin <= %s)
        )
    """, (id_libro, fecha, hora_fin, hora_fin, hora_inicio, hora_inicio, hora_inicio, hora_fin))
    (count,) = cursor.fetchone()
    if count > 0:
        flash("Este horario ya está reservado. Elige otro.", "error")
        cursor.close()
        return redirect(url_for('auth.formulario_reserva', id_libro=id_libro))


    cursor.execute("""
        INSERT INTO reservas (id_usuario, id_libro, fecha_reserva, hora_inicio, hora_fin, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_usuario, id_libro, fecha, hora_inicio, hora_fin, 'pendiente')) 
    db.commit()
    cursor.close()

    flash("Reserva creada exitosamente.", "success")
    
    if session.get('rol') in ['gerente', 'administrador']:
        return redirect(url_for('auth.gestion_reservas')) 
    else:
        return redirect(url_for('auth.mis_reservas'))

@auth.route('/reservar_libro/<int:id_libro>', methods=['POST'])
@requiere_rol('cliente')
def reservar_libro(id_libro):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para reservar un libro', 'error')
        return redirect(url_for('auth.login'))

    id_usuario = session['usuario_id']
    fecha_reserva = datetime.now().date()
    fecha_vencimiento = fecha_reserva + timedelta(days=7)

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO reservas (id_usuario, id_libro, fecha_reserva, fecha_vencimiento, estado)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_usuario, id_libro, fecha_reserva, fecha_vencimiento, 'pendiente'))

    db.commit()
    cursor.close()
    flash('¡Reserva realizada exitosamente!', 'success')
    return redirect(url_for('auth.mis_reservas'))


@auth.route('/mis_reservas', methods=['GET', 'POST'])
@requiere_rol('cliente')
def mis_reservas():
    id_usuario = session.get('usuario_id')
    
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, l.titulo AS titulo_libro, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM reservas r
        INNER JOIN libros l ON r.id_libro = l.id_libro
        WHERE r.id_usuario = %s
    """, (id_usuario,))
    
    reservas = cursor.fetchall()
    cursor.close()

    return render_template('mis_reservas.html', reservas=reservas)


@auth.route('/guardar_reserva', methods=['POST'])
def guardar_reserva():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para reservar un libro', 'error')
        return redirect(url_for('auth.login'))

    id_usuario = request.form.get('id_usuario')
    id_libro = request.form.get('id_libro')
    fecha = request.form.get('fecha') 
    hora_inicio = request.form.get('hora_inicio')  
    hora_fin = request.form.get('hora_fin')

    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM reservas
        WHERE id_libro = %s
        AND fecha_reserva = %s
        AND estado = 'pendiente'
        AND NOT (
            hora_fin <= %s OR hora_inicio >= %s
        )
    """, (id_libro, fecha, hora_inicio, hora_fin))
    
    existe = cursor.fetchone()[0]

    if existe > 0:
        flash("Ya existe una reserva para ese libro en ese horario.", "error")
        return redirect(url_for('auth.formulario_reserva', id_libro=id_libro))

    
    cursor.execute("""
        INSERT INTO reservas (id_usuario, id_libro, fecha_reserva, hora_inicio, hora_fin, estado)
        VALUES (%s, %s, %s, %s, %s, 'pendiente')
    """, (id_usuario, id_libro, fecha, hora_inicio, hora_fin))
    db.commit()

    flash("Reserva realizada con éxito", "success")
    return redirect(url_for('auth.reservas'))


@auth.route('/actualizar_reserva_cliente/<int:id_reserva>', methods=['POST'])
def actualizar_reserva_cliente(id_reserva):
    nuevo_estado = request.form['estado']
    cursor = db.cursor()
    cursor.execute("UPDATE reservas SET estado = %s WHERE id_reserva = %s", (nuevo_estado, id_reserva))
    db.commit()
    cursor.close()
    return redirect(url_for('auth.mis_reservas')) 


# @auth.route('/ver_reservas_gerente', methods=['GET', 'POST'])
# # @requiere_rol('gerente')
# def ver_reservas_gerente():
#     estado_filtro = request.form.get('estado')
#     usuario_filtro = request.form.get('usuario')
#     libro_filtro = request.form.get('libro')

#     query = """
#         SELECT r.id_reserva, u.nombre AS nombre_usuario, l.titulo AS titulo_libro, 
#                r.fecha_reserva, r.estado 
#         FROM reservas r
#         INNER JOIN usuarios u ON r.id_usuario = u.id_usuario
#         INNER JOIN libros l ON r.id_libro = l.id_libro
#         WHERE 1=1
#     """
#     params = []

#     if estado_filtro and estado_filtro != "Todos":
#         query += " AND r.estado = %s"
#         params.append(estado_filtro)

#     if usuario_filtro:
#         query += " AND u.nombre LIKE %s"
#         params.append(f"%{usuario_filtro}%")

#     if libro_filtro:
#         query += " AND l.titulo LIKE %s"
#         params.append(f"%{libro_filtro}%")

#     cursor = db.cursor(dictionary=True)
#     cursor.execute(query, params)
#     reservas = cursor.fetchall()
#     cursor.close()

#     return render_template('reservas_gerente.html', reservas=reservas)

@auth.route('/gestion_reservas', methods=['GET', 'POST'])
@requiere_rol('gerente', 'administrador')
def gestion_reservas():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, u.nombre, l.titulo, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        JOIN libros l ON r.id_libro = l.id_libro
        WHERE r.estado = 'pendiente'
    """)
    reservas = cursor.fetchall()
    cursor.close()
    return render_template('gestion_reservas.html', reservas=reservas)

@auth.route('/actualizar_reserva/<int:id_reserva>', methods=['POST'])
def actualizar_reserva(id_reserva):
    nuevo_estado = request.form['estado']
    cursor = db.cursor()
    cursor.execute("UPDATE reservas SET estado = %s WHERE id_reserva = %s", (nuevo_estado, id_reserva))
    db.commit()
    cursor.close()
    return redirect(url_for('auth.gestion_reservas'))

#Gerente, el de abajo poner que se necesita rol de gerente 
@auth.route('/actualizar_estado_reserva/<int:id_reserva>', methods=['POST'])
def actualizar_estado_reserva(id_reserva):
    nuevo_estado = request.form.get('estado')

    cursor = db.cursor()
    cursor.execute("UPDATE reservas SET estado = %s WHERE id_reserva = %s", (nuevo_estado, id_reserva))
    db.commit()
    cursor.close()

    return redirect(url_for('auth.gestion_reservas'))


@auth.route('/reservas_confirmadas')
@requiere_rol('gerente', 'administrador')

def mostrar_reservas_confirmadas():
    cursor = db.cursor(dictionary=True)
    id_usuario = session.get('usuario_id')
    if not id_usuario:
        return redirect('/login')  


    cursor.execute("""
        SELECT r.id_reserva, u.nombre, u.apellido, l.titulo AS libro, 
            r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado, r.comentarios
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        JOIN libros l ON r.id_libro = l.id_libro
        WHERE r.estado = 'confirmada'
        ORDER BY r.fecha_reserva, r.hora_inicio
    """)
    reservas = cursor.fetchall()

    return render_template('reservas_confirmadas.html', reservas=reservas)



@auth.route('/estadisticas')
@requiere_rol('administrador')
def estadisticas():
    cursor = db.cursor(dictionary=True)

    # Libros más reservados
    cursor.execute("""
        SELECT l.titulo, COUNT(*) AS total_reservas
        FROM reservas r
        JOIN libros l ON r.id_libro = l.id_libro
        GROUP BY r.id_libro
        ORDER BY total_reservas DESC
        LIMIT 5
    """)
    libros_reservados = cursor.fetchall()

    # Estado de reservas
    cursor.execute("""
        SELECT estado, COUNT(*) AS total
        FROM reservas
        GROUP BY estado
    """)
    estados_reservas = cursor.fetchall()

    # Reservas por mes
    cursor.execute("""
        SELECT DATE_FORMAT(fecha_reserva, '%Y-%m') AS mes, COUNT(*) AS total
        FROM reservas
        GROUP BY mes
        ORDER BY mes
    """)
    reservas_por_mes = cursor.fetchall()

    cursor.close()

    return render_template('estadisticas_admin.html',
                        libros_reservados=libros_reservados,
                        estados_reservas=estados_reservas,
                        reservas_por_mes=reservas_por_mes)
    
    

@auth.route('/eliminar_reserva/<int:id>', methods=['POST'])
def eliminar_reserva(id):
    if session.get('rol') != 'admin':
        abort(403)  # Prohibido
    
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    return redirect('/gestion_reservas')