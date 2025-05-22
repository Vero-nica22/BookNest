# BookNest

BookNest es una aplicación web para la gestión de reservas de libros y productos en una cafetería/librería. Permite a clientes, administradores y gerentes interactuar con el sistema según su rol.

## Características

- Registro e inicio de sesión de usuarios con roles: cliente, administrador, gerente.
- Gestión de libros: agregar, editar, eliminar y visualizar catálogo.
- Gestión de productos: agregar, editar, eliminar y visualizar productos.
- Reservas de libros: los clientes pueden reservar libros, ver y cancelar sus reservas.
- Gestión de reservas: administradores y gerentes pueden confirmar, rechazar y ver reservas.
- Estadísticas para administradores sobre reservas y libros más populares.
- Paneles diferenciados según el rol del usuario.

## Estructura del proyecto

- `app.py`: Punto de entrada de la aplicación Flask.
- `config.py`: Configuración de la base de datos y llaves secretas.
- `modules/`: Módulos de rutas y lógica de negocio.
  - `auth.py`: Rutas principales de autenticación y gestión.
  - `routes.py`: Rutas de menús por rol.
  - `user.py`: (comentado) Lógica de usuario.
- `utils.py`: Decoradores y utilidades (por ejemplo, control de acceso por rol).
- `static/`: Archivos estáticos (CSS, imágenes).
- `templates/`: Plantillas HTML para las vistas.

## Instalación

1. Clona el repositorio.
2. Instala las dependencias necesarias:
   ```sh
   pip install flask mysql-connector-python werkzeug
   ```
3. Configura la base de datos MySQL y actualiza los datos en `config.py` si es necesario.
4. Ejecuta la aplicación:
   ```sh
   python app.py
   ```

## Uso

- Accede a `http://localhost:5000` en tu navegador.
- Regístrate como usuario o inicia sesión con un usuario existente.
- Navega según el rol asignado (cliente, administrador, gerente).

## Estructura de la base de datos

Asegúrate de tener las tablas necesarias: `usuarios`, `roles`, `libros`, `productos`, `reservas`, `resenas`.

---

**Nota:** Este proyecto utiliza Flask, MySQL y HTML/CSS/JS para la interfaz.
