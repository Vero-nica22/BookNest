# from models.database import conectar_db
# from flask_bcrypt import Bcrypt

# bcrypt = Bcrypt()

# class Usuario:
#     def __init__(self, nombre, apellido, documento_identidad, celular, correo, contrasena, id_rol=1):
#         self.nombre = nombre
#         self.apellido = apellido
#         self.documento_identidad = documento_identidad
#         self.celular = celular
#         self.correo = correo
#         self.contrasena = bcrypt.generate_password_hash(contrasena).decode('utf-8')  # Encripta la contraseña
#         self.id_rol = id_rol

#     def registrar(self):
#         conexion = conectar_db()
#         cursor = conexion.cursor()

#         # Verificar si el correo ya existe
#         cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (self.correo,))
#         if cursor.fetchone():
#             conexion.close()
#             raise Exception("El correo ya está registrado")

#         # Insertar el usuario si no existe
#         sql = """INSERT INTO usuarios (nombre, apellido, documento_identidad, celular, correo, contrasena, id_rol) 
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
#         valores = (self.nombre, self.apellido, self.documento_identidad, self.celular, self.correo, self.contrasena, self.id_rol)
        
#         cursor.execute(sql, valores)
#         conexion.commit()
#         conexion.close()

#     @staticmethod
#     def autenticar(correo, contrasena):
#         conexion = conectar_db()
#         cursor = conexion.cursor(dictionary=True)
#         sql = "SELECT * FROM usuarios WHERE correo = %s"
#         cursor.execute(sql, (correo,))
#         usuario = cursor.fetchone()
#         conexion.close()

#         if usuario and bcrypt.check_password_hash(usuario['contrasena'], contrasena):
#             return usuario
#         return None
