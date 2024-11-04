from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db, bcrypt
from auth import auth, token_required, logger
import jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])
    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    app.register_blueprint(auth)

    @app.route("/")
    def hello_world():
        return jsonify(message="Hello from LECS!")
    
    @app.route("/profile")
    @token_required
    def profile(current_user):
        logger.info(f"Profile accessed with username : ${current_user.username}")
        return jsonify(username = current_user.username)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)