from flask import Blueprint, request, jsonify
from ..models import Recipe, Product, RecipeItem
from ..db import db
from ..schemas import RecipeSchema
from ..utils import retry_on_exception
from ..events import events
from ..cache import cache
import json
from app.auth import gatekeeper

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/', methods=['POST'])
@retry_on_exception()
def create_recipe():
    data = request.json
    recipe = Recipe(name=data['name'], description=data.get('description'))
    db.session.add(recipe)
    db.session.flush()
    events.publish('recipes', {'action': 'created', 'id': recipe.id})

    cache.delete("recipes:list")
    return jsonify({'message': 'Recipe created', 'id': recipe.id}), 201

@recipes_bp.route('/<int:id>', methods=['PUT'])
@retry_on_exception()
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    data = request.json
    recipe.name = data.get('name', recipe.name)
    recipe.description = data.get('description', recipe.description)
    db.session.commit()
    return jsonify({'message': 'Recipe updated'})

@recipes_bp.route('/<int:id>', methods=['DELETE'])
@retry_on_exception()
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    # publish_event('recipe_deleted', {'recipe_id': id})
    return jsonify({'message': 'Recipe deleted'})

@recipes_bp.route('/<int:id>/products', methods=['POST'])
@retry_on_exception()
def add_product_to_recipe(id):
    data = request.json
    recipe = Recipe.query.get_or_404(id)
    product = Product.query.get_or_404(data['product_id'])
    db.session.execute(RecipeItem.insert().values(recipe_id=recipe.id, product_id=product.id, quantity=data['quantity']))
    db.session.commit()
    # publish_event('recipe_product_added', {'recipe_id': recipe.id, 'product_id': product.id})
    return jsonify({'message': 'Product added to recipe'})

@recipes_bp.route('/', methods=['GET'])
@retry_on_exception()
@gatekeeper('recipes:read')
def list_recipes():
    cache_key = "recipes:list"
    cached_data = cache.get(cache_key)

    if cached_data:
        return jsonify(json.loads(cached_data))
    
    recipes = Recipe.query.all()
    data = [{'id': r.id, 'name': r.name, 'description': r.description} for r in recipes]
    cache.set(cache_key, json.dumps(data), ex=60)
    return jsonify(data)

@recipes_bp.route('/<int:id>', methods=['GET'])
@retry_on_exception()
def get_recipe(id):
    cache_key = f"recipe:{id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return jsonify(json.loads(cached_data))
    
    recipe = Recipe.query.get_or_404(id)
    data = {'id': recipe.id, 'name': recipe.name, 'description': recipe.description}
    cache.set(cache_key, json.dumps(data), ex=60)
    return jsonify(data)
