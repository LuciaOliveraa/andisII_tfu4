from flask import Blueprint, request, jsonify
from ..models import Recipe, Product, RecipeItem
from ..db import db
from ..schemas import RecipeSchema
from ..utils import retry_on_exception
from ..events import events

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/', methods=['POST'])
@retry_on_exception()
# @rate_limit()
# # @gatekeeper
# @transaction
def create_recipe():
    data = request.json
    recipe = Recipe(name=data['name'], description=data.get('description'))
    db.session.add(recipe)
    db.session.flush()
    events.publish('recipes', {'action': 'created', 'id': recipe.id})
    return jsonify({'message': 'Recipe created', 'id': recipe.id}), 201

@recipes_bp.route('/<int:id>', methods=['PUT'])
@retry_on_exception()
# @gatekeeper
# @transaction
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    data = request.json
    recipe.name = data.get('name', recipe.name)
    recipe.description = data.get('description', recipe.description)
    db.session.commit()
    return jsonify({'message': 'Recipe updated'})

@recipes_bp.route('/<int:id>', methods=['DELETE'])
@retry_on_exception()
# @gatekeeper
# @transaction
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    # publish_event('recipe_deleted', {'recipe_id': id})
    return jsonify({'message': 'Recipe deleted'})

@recipes_bp.route('/<int:id>/products', methods=['POST'])
@retry_on_exception()
# @transaction
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
# @cache_get('recipes_list')
def list_recipes():
    recipes = Recipe.query.all()
    return jsonify([{ 'id': r.id, 'name': r.name, 'description': r.description } for r in recipes])

@recipes_bp.route('/<int:id>', methods=['GET'])
@retry_on_exception()
# @cache_get('recipe_detail')
def get_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return jsonify({ 'id': recipe.id, 'name': recipe.name, 'description': recipe.description })
