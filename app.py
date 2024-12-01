import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
import models
# models have to be imported before we initialize the SQLAlchemy extension (so it see them)
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from blocklist import BLOCKLIST


# factory-pattern:
def create_app(db_url=None):
    app = Flask(__name__) 
    
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    # ^^^ if we passed db_url arg it will works, otherwise it will env-variable from environment(&), otherwise it will be next (2nd) arg of os.getenv...
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # it slows down SQLAlchemy if it's =True
    db.init_app(app)  # initializes the Flask SQLAlchemy extension
    migrate = Migrate(app, db)
    api = Api(app)

    # app.config["JWT_SECRET_KEY"] = secrets.SystemRandom().getrandbits(128)
    app.config["JWT_SECRET_KEY"] = "197852340355645079694175195097410712361"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "toden_revoked"}
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            {"description": "The token is not fresh", "error": "fresh_token_required"},
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # Look in the db and see whether the user is an admin before saving thisinfo in JWT
        if identity == "1":
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    # В примере выше ^^^ хеадер и пэйлоад в аргументах, т.к. jwt есть, валиден, но истёк, а в примерах ниже его либо нет, либо он невалиден, поэтому в аргументы передаётся просто ошибка.
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed.", "error": "invalid_token"}),
            401,
        )
    

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request does not contain an access token.", 
                    "error": "authorization_required"
                }
            ),
            401,
        )

    # commented because no need when using Flask-Migrate to create our database tables // instead of it type in terminal "flask db init" (allow us interact with Alimbic)(create "migrations" folder and "mitrations/versions/"-which will contain all the changes that we make to our db)
    # # creating all tables in our database (if they aren't exist):
    # with app.app_context():
    #     db.create_all()
    
    
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    
    return app