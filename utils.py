from functools import wraps
from flask import redirect, session

def requiere_rol(*roles_requeridos):
    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            rol_actual = session.get('rol', '')
            if rol_actual is None:
                rol_actual = ''
            rol_actual = rol_actual.strip().lower()
            roles_permitidos = [r.strip().lower() for r in roles_requeridos]
            print("Rol actual en sesión:", rol_actual)
            if not rol_actual or rol_actual not in roles_permitidos:
                return redirect('/login')
            return f(*args, **kwargs)
        return envoltura
    return decorador


