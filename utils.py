from functools import wraps
from flask import redirect, session

def requiere_rol(rol_requerido):
    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            # Depuración: imprime valores en consola
            print("Rol actual en sesión:", session.get('rol'))
            if 'rol' not in session or session['rol'] != rol_requerido:
                return redirect('/login')  # Redirige si no tiene el rol requerido
            return f(*args, **kwargs)
        return envoltura
    return decorador

