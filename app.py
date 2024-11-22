import os

from flask import Flask
from flask_smorest import Api

from db import db
import models
# models have to be imported before we initialize the SQLAlchemy extension (so it see them)
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint


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
    # ^^^ if we passed db_url arg it will works, otherwise it will env-variable from environment(&), otherwise
    # it will be next (2nd) arg of os.getenv...
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # it slows down SQLAlchemy if it's =True
    db.init_app(app)  # initializes the Flask SQLAlchemy extension

    # creating all tables in our database (if they aren't exist):
    with app.app_context():
        db.create_all()
    
    api = Api(app)
    
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    
    return app