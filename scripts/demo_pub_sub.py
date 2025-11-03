import threading
import time
import json
from app import create_app
from app.events import events
from app.cache import cache


def subscriber_demo():
    """Simula un worker que escucha eventos de recetas."""
    print("[Subscriber] Esperando mensajes en el canal 'recipes'\n")
    for message in events.subscribe("recipes"):
        print(f"[Subscriber] Recibido: {message}")
        if message.get("action") == "created":
            print(f"[Subscriber] Nueva receta creada con ID {message['id']}")
        elif message.get("action") == "deleted":
            print(f"[Subscriber] Receta eliminada con ID {message['id']}")


def publisher_demo():
    """Simula la publicación de eventos desde el servidor Flask."""
    time.sleep(2)  #espera a que el suscriptor se conecte
    for i in range(3):
        event = {"action": "created", "id": i + 1}
        print(f"[Publisher] Publicando evento: {event}")
        events.publish("recipes", event)
        time.sleep(1)

    #envía un evento de eliminación como ejemplo
    deleted = {"action": "deleted", "id": 2}
    print(f"[Publisher] Publicando evento: {deleted}")
    events.publish("recipes", deleted)


if __name__ == "__main__":
    print("\n--- Demostración del patrón Publisher/Subscriber ---\n")

    app = create_app()
    with app.app_context():
        #inicializacion de redis a través de cache
        cache.init_app(app)
        events.init_app(app)

        #hilo 1 - suscriptor
        sub_thread = threading.Thread(target=subscriber_demo, daemon=True)
        sub_thread.start()

        #hilo 2 - publicador 
        publisher_demo()

        print("\n El worker recibió los eventos publicados.\n")
        time.sleep(2)
