import os
from flask import Flask,jsonify
from flask_cors import CORS
from flasgger import Swagger
app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401




if __name__ == '__main__':
    app.run(debug=True)