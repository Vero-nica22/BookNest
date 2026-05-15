from flask import Flask
from modules.auth import auth                        
from modules.reservas.routes import reservas_bp      

def create_app():
    app = Flask(__name__)
    app.secret_key = 'booknest_secret_key'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    app.register_blueprint(auth)                                     
    app.register_blueprint(reservas_bp, url_prefix='/reservas')      

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)