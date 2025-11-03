from flask import Blueprint, request, jsonify
import random
from ..models import Product
from ..db import db
from ..schemas import ProductSchema
from ..utils import retry_on_exception
from ..cache import cache
from ..events import events

bp = Blueprint('products', __name__)
product_schema = ProductSchema()


@bp.route('/', methods=['POST'])
@retry_on_exception()
def create_product():
    data = request.get_json() or {}
    validated = product_schema.load(data)
    # Simulate a transient error randomly to demonstrate retry behavior
    # ~50% chance to raise an exception so the retry decorator (tenacity)
    # will attempt the function again before a final failure is returned.
    if random.random() < 0.5:
        print('  [create_product] simulated transient error, raising...')
        raise Exception('Simulated transient error')
    with db.session.begin():
        p = Product(**validated)
        db.session.add(p)
    return product_schema.dump(p), 201


@bp.route('/<int:product_id>', methods=['PUT'])
@retry_on_exception()
def edit_product(product_id):
    data = request.get_json() or {}

    # Buscar el producto
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Actualizar solo los campos válidos
    valid_fields = {'name', 'description', 'unit'}
    for key, value in data.items():
        if key in valid_fields:
            setattr(product, key, value)

    try:
        db.session.commit()
        return product_schema.dump(product), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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


@bp.route('/cache', methods=['POST'])
def set_cache():
    """Set a key/value pair in Redis via the project's cache wrapper.

    JSON body: {"key": "some:key", "value": "...", "ex": 60}
    """
    data = request.get_json() or {}
    key = data.get('key')
    value = data.get('value')
    ex = data.get('ex')
    if not key or value is None:
        return jsonify({'error': 'key and value are required'}), 400
    # cache.set expects ex in seconds or None
    cache.set(key, value, ex=ex)
    return jsonify({'message': 'cached', 'key': key}), 201


@bp.route('/cache/<path:key>', methods=['GET'])
def get_cache(key):
    """Retrieve a cached value."""
    value = cache.get(key)
    if value is None:
        return jsonify({'message': 'not found'}), 404
    return jsonify({'key': key, 'value': value}), 200


@bp.route('/cache/<path:key>', methods=['DELETE'])
def delete_cache(key):
    cache.delete(key)
    return '', 204


@bp.route('/publish', methods=['POST'])
def publish_event():
    """Publish an event to a Redis channel via the project's events wrapper.

    JSON body: {"channel": "some_channel", "event": {...}}
    """
    data = request.get_json() or {}
    channel = data.get('channel')
    event = data.get('event')
    if not channel or event is None:
        return jsonify({'error': 'channel and event are required'}), 400
    try:
        events.publish(channel, event)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'published', 'channel': channel}), 201