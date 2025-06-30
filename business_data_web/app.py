import os
from dotenv import load_dotenv
from flask import Flask

from business_data_web.blueprints.root import root_bp

load_dotenv()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env()
    
    
    app.register_blueprint(root_bp)
    return app