
from datetime import datetime, timedelta
from reservas import repository


ESTADOS_VALIDOS = {'pendiente', 'confirmada', 'completada', 'cancelada'}

DURACION_MAXIMA_HORAS = 4

FMT_HORA = "%H:%M"

class ReservaError(Exception):
    """Excepción de dominio para errores de negocio en reservas."""
    pass


def _parsear_horas(hora_inicio: str, hora_fin: str):
    try:
        inicio = datetime.strptime(hora_inicio, FMT_HORA)
        fin = datetime.strptime(hora_fin, FMT_HORA)
    except ValueError:
        raise ReservaError("Formato de hora inválido. Usa HH:MM.")
    return inicio, fin


def _validar_rango_horario(inicio: datetime, fin: datetime) -> None:
    if fin <= inicio:
        raise ReservaError("La hora de fin debe ser posterior a la hora de inicio.")
    if (fin - inicio) > timedelta(hours=DURACION_MAXIMA_HORAS):
        raise ReservaError(
            f"La duración máxima de una reserva es de {DURACION_MAXIMA_HORAS} horas."
        )

def _validar_estado(estado: str) -> None:
    if estado not in ESTADOS_VALIDOS:
        raise ReservaError(
            f"Estado inválido '{estado}'. Opciones: {', '.join(ESTADOS_VALIDOS)}."
        )

def crear_reserva(id_usuario: int, id_libro: int,
                  fecha: str, hora_inicio: str, hora_fin: str) -> None:
    inicio, fin = _parsear_horas(hora_inicio, hora_fin)
    _validar_rango_horario(inicio, fin)

    if repository.existe_conflicto_horario(id_libro, fecha, hora_inicio, hora_fin):
        raise ReservaError("Este horario ya está reservado. Elige otro.")

    repository.insertar_reserva(id_usuario, id_libro, fecha, hora_inicio, hora_fin)


def cambiar_estado_reserva(id_reserva: int, nuevo_estado: str) -> None:
    _validar_estado(nuevo_estado)
    repository.actualizar_estado_reserva(id_reserva, nuevo_estado)


def cancelar_reserva_cliente(id_reserva: int) -> None:
    repository.actualizar_estado_reserva(id_reserva, 'cancelada')


def eliminar_reserva(id_reserva: int) -> None:
    repository.eliminar_reserva(id_reserva)

def obtener_mis_reservas(id_usuario: int) -> list:
    return repository.obtener_reservas_por_usuario(id_usuario)

def obtener_reservas_pendientes() -> list:
    return repository.obtener_reservas_pendientes()

def obtener_reservas_confirmadas() -> list:
    return repository.obtener_reservas_confirmadas()

def obtener_estadisticas() -> dict:
    return repository.obtener_estadisticas()


