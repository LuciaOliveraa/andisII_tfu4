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
    # return all products
    products = db.session.query(Product).all()
    # use schema with many=True to serialize lists
    return ProductSchema(many=True).dump(products)


# from flask import Blueprint, request, jsonify
# from app import db
# from app.models import Product
# from app.middleware.rate_limit import rate_limit
# from app.middleware.gatekeeper import gatekeeper

# products_bp = Blueprint('products', __name__)

# @products_bp.route('/', methods=['POST'])
# @rate_limit()
# @gatekeeper
# def create_product():
#     data = request.json
#     product = Product(name=data['name'], unit=data['unit'])
#     db.session.add(product)
#     db.session.commit()
#     return jsonify({'message': 'Product created', 'id': product.id}), 201

# @products_bp.route('/<int:id>', methods=['PUT'])
# @rate_limit()
# @gatekeeper
# def edit_product(id):
#     product = Product.query.get_or_404(id)
#     data = request.json
#     product.name = data.get('name', product.name)
#     product.unit = data.get('unit', product.unit)
#     db.session.commit()
#     return jsonify({'message': 'Product updated'})

# @products_bp.route('/<int:id>', methods=['DELETE'])
# @gatekeeper
# def delete_product(id):
#     product = Product.query.get_or_404(id)
#     db.session.delete(product)
#     db.session.commit()
#     return jsonify({'message': 'Product deleted'})