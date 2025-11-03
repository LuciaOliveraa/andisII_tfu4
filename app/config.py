import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/recipes')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATE_LIMITS = os.getenv('RATE_LIMITS', '10/hour')
    CACHE_DEFAULT_TTL = 60 
    VALET_TOKEN_TTL = 300