from functools import wraps
from flask import redirect, session

def requiere_rol(*roles_requeridos):
    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            print("Rol actual en sesión:", session.get('rol'))
            if 'rol' not in session or session['rol'] not in roles_requeridos:
                return redirect('/login')  
            return f(*args, **kwargs)
        return envoltura
    return decorador


