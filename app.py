import os
from flask import Flask
from flask_cors import CORS
from models import init_db
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supportflow-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supportflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app)
    
    # Initialize database
    init_db()
    
    # Register routes
    register_routes(app)
    
    @app.route('/')
    def index():
        return {'message': 'SupportFlow API is running', 'version': '1.0.0'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)