from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required

from db import db
from models import StoreModel
from schemas import StoreSchema

blp = Blueprint("stores", __name__, description="Operations on stores.")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):  # has been took from get_store() due "<string:store_id>"
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, 294
    

@blp.route("/store")
class StoreList(MethodView):
    @jwt_required()
    @blp.response(201, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400, 
                message="Store with that name already exists."
                )
        except SQLAlchemyError:
            abort(500, message="An error occured creating the store.")

        return store, 201