import uuid
from flask import Flask, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema


blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found.")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted"}
        except KeyError:
            abort(404, message="Item not found")

    @blp.arguments(ItemUpdateSchema)
    def put(self, item_data, item_id):
        # item_data = request.get_json()  # # don't use after adding ItemSchema-validation
        try:
            item = items[item_id]
            item |= item_data
    
            return item
        except KeyError:
            abort(404, message="Item not found.")



@blp.route("/item")
class ItemsList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        # return {"items": list(items.values())}  # don't use after marshmellow-validation
        return items.values()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        # item_data = request.get_json()  # don't use after adding ItemSchema-validation
        for item in items.values():
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message="Item already exists.")
    
        # if item_data["store_id"] not in stores:  # Actually stores?!??!!
        #     abort(404, message="Store not found.")  # He have no this validation
    
        item_id = uuid.uuid4().hex
        item = {**item_data, "id": item_id}
        items[item_id] = item
    
        return item, 201