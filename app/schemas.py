from marshmallow import Schema, fields, post_load

class ProductSchema(Schema):
id = fields.Int(dump_only=True)
name = fields.Str(required=True)
description = fields.Str()
unit = fields.Str()


class RecipeItemSchema(Schema):
id = fields.Int(dump_only=True)
product_id = fields.Int(required=True)
quantity = fields.Float(required=True)
product = fields.Nested(ProductSchema, dump_only=True)


class RecipeSchema(Schema):
id = fields.Int(dump_only=True)
title = fields.Str(required=True)
instructions = fields.Str()
items = fields.List(fields.Nested(RecipeItemSchema), dump_only=True)