from .db import db
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Table
from sqlalchemy.orm import relationship

# association table for recipe items
class RecipeItem(db.Model):
__tablename__ = 'recipe_items'
id = Column(Integer, primary_key=True)
recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
quantity = Column(Float, nullable=False)

product = relationship('Product')


class Product(db.Model):
__tablename__ = 'products'
id = Column(Integer, primary_key=True)
name = Column(String(255), nullable=False, unique=True)
description = Column(Text)
unit = Column(String(50))


class Recipe(db.Model):
__tablename__ = 'recipes'
id = Column(Integer, primary_key=True)
title = Column(String(255), nullable=False)
instructions = Column(Text)
items = relationship('RecipeItem', cascade='all, delete-orphan')