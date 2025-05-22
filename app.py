from flask import Flask
from modules.auth import auth  

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta'
app.config['UPLOAD_FOLDER'] = 'static/uploads'


app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)




