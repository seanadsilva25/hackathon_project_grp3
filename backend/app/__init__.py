from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    CORS(app)

    from .health import main
    from .auth_routes import auth
    from .routes.complaints_api import complaints_api

    app.register_blueprint(main, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(complaints_api, url_prefix="/api/complaints")

    return app