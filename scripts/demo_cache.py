import time
from app import create_app
from app.cache import cache


fake_database = {
    1: {"id": 1, "name": "Pasta"},
    2: {"id": 2, "name": "Asado"},
    3: {"id": 3, "name": "Sushi"},
}


def get_recipe_from_db(recipe_id):
    """Simula una consulta lenta a la base de datos."""
    print(f"[DB] Consultando receta {recipe_id} en la base de datos")
    time.sleep(1)  
    return fake_database.get(recipe_id)


def get_recipe(recipe_id):
    """Implementa el patrón Cache-Aside."""
    cache_key = f"recipe:{recipe_id}"

    #Buscar primero en caché
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"[CACHE HIT] Receta {recipe_id} encontrada en caché")
        return cached_data

    #Si no está, buscar en la bd
    print(f"[CACHE MISS] Receta {recipe_id} no está en caché")
    recipe = get_recipe_from_db(recipe_id)
    if recipe:
        #Guardar en caché para futuras consultas
        cache.set(cache_key, str(recipe), ex=30)
        print(f"[CACHE SET] Receta {recipe_id} guardada en caché")
        return recipe
    else:
        print(f"[DB] Receta {recipe_id} no encontrada")
        return None


if __name__ == "__main__":
    print("\n--- Demostración del patrón Cache-Aside ---\n")

    app = create_app()
    with app.app_context():
        cache.init_app(app)

        # Primera consulta (debería venir de la DB)
        print("\n Primera solicitud de la receta 1")
        recipe = get_recipe(1)
        print("Resultado:", recipe)

        # Segunda consulta (debería venir del caché)
        print("\n Segunda solicitud de la receta 1")
        recipe = get_recipe(1)
        print("Resultado:", recipe)

