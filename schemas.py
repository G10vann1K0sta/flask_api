from marshmallow import Schema, fields


# Before using SQLAlchemy (relationtip -> nestet store object in ItemModel and vice versa)
# +вероятно т.к. мы нам store_id будет валидироваться в другой таблице БД(?). Но как выяснилось позже валидация store_id будет в отдельном наследованном классе:
# class ItemSchema(Schema):
#     id = fields.Str(dump_only=True)
#     name = fields.Str(required=True)
#     price = fields.Float(required=True)
#     store_id = fields.Str(required=True)
# After (new item schema doesn't deal with stores at all):
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema))


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))
    tags = fields.List(fields.Nested(PlainTagSchema, dump_only=True))


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)
