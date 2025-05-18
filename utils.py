from functools import wraps
from flask import redirect, session

def requiere_rol(rol_requerido):
    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            print("Rol actual en sesión:", session.get('rol'))
            if 'rol' not in session or session['rol'] != rol_requerido:
                return redirect('/login')  
            return f(*args, **kwargs)
        return envoltura
    return decorador

