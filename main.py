import os
from datetime import timedelta
from flask import Flask,jsonify
from flask_cors import CORS
from flasgger import Swagger
from models import *
from auth.auth import auth
from oauth.api import oauth
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)
db.init_app(app)
migrate = Migrate(app,db)
app.register_blueprint(auth)
app.register_blueprint(oauth)

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#TODO: add a streaming functionality