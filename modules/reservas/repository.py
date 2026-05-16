import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def obtener_reservas_por_usuario(id_usuario: int) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, l.titulo AS titulo_libro,
               r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM reservas r
        INNER JOIN libros l ON r.id_libro = l.id_libro
        WHERE r.id_usuario = %s
        ORDER BY r.fecha_reserva DESC
    """, (id_usuario,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def obtener_reservas_pendientes() -> list:

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, u.nombre, l.titulo,
               r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        JOIN libros l ON r.id_libro = l.id_libro
        WHERE r.estado = 'pendiente'
        ORDER BY r.fecha_reserva, r.hora_inicio
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def obtener_reservas_filtradas(estado: str, usuario: str, libro: str) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT r.id_reserva, u.nombre, l.titulo,
               r.fecha_reserva, r.hora_inicio, r.hora_fin, r.estado
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        JOIN libros   l ON r.id_libro   = l.id_libro
        WHERE 1=1
    """
    params = []

    if estado and estado != 'todos':
        query += " AND r.estado = %s"
        params.append(estado)

    if usuario:
        query += " AND u.nombre LIKE %s"
        params.append(f"%{usuario}%")

    if libro:
        query += " AND l.titulo LIKE %s"
        params.append(f"%{libro}%")

    query += " ORDER BY r.fecha_reserva, r.hora_inicio"

    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def obtener_reservas_confirmadas() -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_reserva, u.nombre, u.apellido,
               l.titulo AS libro, r.fecha_reserva,
               r.hora_inicio, r.hora_fin, r.estado, r.comentarios
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        JOIN libros l ON r.id_libro = l.id_libro
        WHERE r.estado = 'confirmada'
        ORDER BY r.fecha_reserva, r.hora_inicio
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def existe_conflicto_horario(id_libro: int, fecha: str,
                              hora_inicio: str, hora_fin: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM reservas
        WHERE id_libro = %s
          AND fecha_reserva = %s
          AND estado IN ('pendiente', 'confirmada')
          AND (
              (hora_inicio < %s AND hora_fin > %s) OR
              (hora_inicio < %s AND hora_fin > %s) OR
              (hora_inicio >= %s AND hora_fin <= %s)
          )
    """, (id_libro, fecha,
          hora_fin, hora_fin,
          hora_inicio, hora_inicio,
          hora_inicio, hora_fin))
    (count,) = cursor.fetchone()
    cursor.close()
    conn.close()
    return count > 0


def insertar_reserva(id_usuario: int, id_libro: int, fecha: str,
                     hora_inicio: str, hora_fin: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reservas (id_usuario, id_libro, fecha_reserva,
                              hora_inicio, hora_fin, estado)
        VALUES (%s, %s, %s, %s, %s, 'pendiente')
    """, (id_usuario, id_libro, fecha, hora_inicio, hora_fin))
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_estado_reserva(id_reserva: int, nuevo_estado: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reservas SET estado = %s WHERE id_reserva = %s",
        (nuevo_estado, id_reserva)
    )
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_reserva(id_reserva: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (id_reserva,))
    conn.commit()
    cursor.close()
    conn.close()



def obtener_estadisticas() -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.titulo, COUNT(*) AS total_reservas
        FROM reservas r
        JOIN libros l ON r.id_libro = l.id_libro
        GROUP BY r.id_libro
        ORDER BY total_reservas DESC
        LIMIT 5
    """)
    libros_reservados = cursor.fetchall()

    cursor.execute("""
        SELECT estado, COUNT(*) AS total
        FROM reservas
        GROUP BY estado
    """)
    estados_reservas = cursor.fetchall()

    cursor.execute("""
        SELECT DATE_FORMAT(fecha_reserva, '%Y-%m') AS mes, COUNT(*) AS total
        FROM reservas
        GROUP BY mes
        ORDER BY mes
    """)
    reservas_por_mes = cursor.fetchall()

    cursor.close()
    conn.close()
    return {
        'libros_reservados': libros_reservados,
        'estados_reservas': estados_reservas,
        'reservas_por_mes': reservas_por_mes,
    }