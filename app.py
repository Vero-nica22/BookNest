# from flask import Flask
# from routes.auth import auth
# from models.database import probar_conexion

# app = Flask(__name__)

# app.register_blueprint(auth, url_prefix="/auth")
# @app.route("/")
# def home():
#     return "Bienvenido a BookNest"


# if __name__ == '__main__':
#     app.run(debug=True)
#     # app.run(port=3000)
#     probar_conexion()

# from flask import Flask, render_template, request, redirect, session
# from werkzeug.security import generate_password_hash, check_password_hash
# import mysql.connector

# app = Flask(__name__)
# app.secret_key = 'tu_llave_secreta'

# # Configurar conexión a la base de datos
# db = mysql.connector.connect(
#     host="localhost",
#     user="miusuario",
#     password="22",
#     database="booknest"
# )

# @app.route('/registro', methods=['GET', 'POST'])
# def registro():
#     if request.method == 'POST':
#         nombre = request.form['nombre']
#         apellido = request.form['apellido']
#         documento = request.form['documento']
#         celular = request.form['celular']
#         correo = request.form['correo']
#         contrasena = generate_password_hash(request.form['contrasena'])

#         cursor = db.cursor()
#         try:
#             cursor.execute("""
#                 INSERT INTO usuarios (nombre, apellido, documento_identidad, celular, correo, contrasena)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """, (nombre, apellido, documento, celular, correo, contrasena))
#             db.commit()
#             return redirect('/login')
#         except mysql.connector.Error as err:
#             return f"Error: {err}"
#     return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         correo = request.form['correo']
#         contrasena = request.form['contrasena']

#         cursor = db.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
#         usuario = cursor.fetchone()
#         if usuario and check_password_hash(usuario['contrasena'], contrasena):
#             session['usuario_id'] = usuario['id_usuario']
#             return redirect('/')
#         else:
#             return "Credenciales incorrectas"
#     return render_template('login.html')

# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask
from modules.auth import auth  # Importa el Blueprint de auth

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta'

# Registra el Blueprint
app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)


