import time
from app import create_app
from app.events import events
from tenacity import retry, wait_fixed, stop_after_attempt
import logging
from app.cache import cache


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = create_app()

def handle_event(event):
    print(f"[Worker] Handling event: {event}")
    # Acá se podría añadir lógica más compleja:
    # - enviar email de notificación
    # - actualizar índices de búsqueda
    # - invalidar cachés
    # - registrar auditorías
    if event.get('action') == 'created':
        print(f"[Worker] Recipe created with ID {event.get('id')}")
    elif event.get('action') == 'deleted':
        print(f"[Worker] Recipe deleted with ID {event.get('id')}")

if __name__ == "__main__":
    with app.app_context():
        print("[Worker] Starting event listener...")
        logger.info("[Worker] Conected to Redis, starting event listener...")
        for event in events.subscribe('recipes'):
            handle_event(event)
            time.sleep(0.1)  # pequeño delay para simular trabajo
