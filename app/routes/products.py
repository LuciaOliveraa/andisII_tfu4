from flask import Blueprint, request, jsonify
from ..models import Product
from ..db import db
from ..schemas import ProductSchema
from ..utils import retry_on_exception

bp = Blueprint('products', __name__)
product_schema = ProductSchema()


@bp.route('/', methods=['POST'])
@retry_on_exception()
def create_product():
data = request.get_json() or {}
validated = product_schema.load(data)
# transaction
with db.session.begin():
p = Product(**validated)
db.session.add(p)
return product_schema.dump(p), 201


@bp.route('/<int:product_id>', methods=['PUT'])
@retry_on_exception()
def edit_product(product_id):
data = request.get_json() or {}
p = db.session.get(Product, product_id)
if not p:
return {'message': 'Product not found'}, 404
for k, v in data.items():
setattr(p, k, v)
with db.session.begin():
db.session.add(p)
return product_schema.dump(p)


@bp.route('/<int:product_id>', methods=['DELETE'])
@retry_on_exception()
def delete_product(product_id):
p = db.session.get(Product, product_id)
if not p:
return {'message': 'Product not found'}, 404
with db.session.begin():
db.session.delete(p)
return '', 204


@bp.route('/', methods=['GET'])
def list_products():
products = Product.q