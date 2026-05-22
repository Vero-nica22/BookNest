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
- `modules/auth.py`: Rutas principales de autenticación y gestión.
- `modules/reservas/`: Rutas y servicios relacionados con reservas y libros.
- `utils.py`: Decoradores y utilidades (por ejemplo, control de acceso por rol).
- `static/`: Archivos estáticos (CSS, imágenes, uploads).
- `templates/`: Plantillas HTML para las vistas.

## Dependencias necesarias

- Python 3.7+ recomendado
- Flask
- mysql-connector-python
- werkzeug

Instala las dependencias con:

```bash
pip install flask mysql-connector-python werkzeug
```

## Configuración

1. Clona el repositorio.
2. Actualiza los datos de conexión en `config.py`:
   - `host`
   - `user`
   - `password`
   - `database`
3. Asegúrate de tener una base de datos MySQL con las tablas necesarias:
   - `usuarios`
   - `roles`
   - `libros`
   - `productos`
   - `reservas`
   - `resenas`
4. Si usas carga de archivos, verifica que la carpeta `static/uploads/` exista.

## Pasos para ejecutar el proyecto

Desde la raíz del proyecto:

```bash
python app.py
```

Luego abre en el navegador:

```text
http://localhost:5000/login
```

## Uso

- Regístrate como usuario o inicia sesión con un usuario existente.
- Navega según el rol asignado: cliente, administrador o gerente.
- El menú y las acciones disponibles cambian según tu rol.

## Ejemplos de llamadas a la API (cliente)

1. Inicia la aplicación

Ejecuta desde la raíz del proyecto:

```bash
python app.py
```

Verifica que responde en:

```text
http://127.0.0.1:5000
http://localhost:5000
```

2. Autenticar en Postman

- Endpoint: `POST http://127.0.0.1:5000/api/login`
- Body: selecciona `Body > raw > JSON`

```json
{
  "correo": "usuario@ejemplo.com",
  "contrasena": "tuPassword"
}
```

Resultado esperado:

- `200 OK` si las credenciales son correctas
- JSON de respuesta:

```json
{
  "message": "Autenticación exitosa.",
  "rol": "cliente"
}
```

Importante: la app usa sesiones de Flask. En Postman debes conservar cookies entre peticiones para que las siguientes llamadas sean autorizadas.

### Listar libros

- Método: `GET`
- URL: `http://127.0.0.1:5000/reservas/api/libros`

### Obtener un libro

- Método: `GET`
- URL: `http://127.0.0.1:5000/reservas/api/libro/<id_libro>`

### Crear reserva

- Método: `POST`
- URL: `http://127.0.0.1:5000/reservas/api/crear/<id_libro>`
- Body: `raw JSON` o `x-www-form-urlencoded`

Ejemplo JSON:

```json
{
  "fecha": "2026-06-01",
  "hora_inicio": "10:00",
  "hora_fin": "12:00"
}
```

### Ver mis reservas

- Método: `GET`
- URL: `http://127.0.0.1:5000/reservas/api/mis-reservas`

### Cancelar reserva

- Método: `POST`
- URL: `http://127.0.0.1:5000/reservas/api/cancelar/<id_reserva>`

## Rutas de búsqueda para cliente

Las dos rutas principales que puede usar un cliente para buscar o consultar libros son:

- `GET /reservas/api/libros`
- `GET /reservas/api/libro/<id_libro>`

> Nota: también existen otras rutas útiles para reservas, como `/reservas/api/crear/<id_libro>` y `/reservas/api/mis-reservas`.

## Notas finales

Este proyecto utiliza Flask, MySQL y HTML/CSS/JS para la interfaz.

# Muchas gracias
