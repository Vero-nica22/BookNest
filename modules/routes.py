# from utils import requiere_rol
# from functools import wraps
# from flask import render_template
from utils import requiere_rol

@auth.route('/menu_cliente')
@requiere_rol('cliente')
def menu_cliente():
    return render_template('menu_cliente.html')

@auth.route('/menu_administrador')
@requiere_rol('administrador')
def menu_administrador():
    return render_template('menu_administrador.html')

@auth.route('/menu_gerente')
@requiere_rol('gerente')
def menu_gerente():
    return render_template('menu_gerente.html')
