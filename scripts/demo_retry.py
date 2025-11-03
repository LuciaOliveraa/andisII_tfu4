import random
import time
from app.utils import retry_on_exception  

#función que falla las primeras veces y luego tiene éxito
attempts_needed = 3
current_attempt = 0

@retry_on_exception(attempts=5, wait=1) 
def flaky_function():
    global current_attempt
    current_attempt += 1
    print(f"Intento n{current_attempt}...")
    
    #simulacion de fallo
    if current_attempt < attempts_needed:
        raise ConnectionError("Error simulado")
    
    return "Éxito en el intento n" + str(current_attempt)


if __name__ == "__main__":
    print("\n--- Demostración del patrón Retry ---\n")
    try:
        result = flaky_function()
        print(result)
    except Exception as e:
        print("Falló después de varios reintentos:", e)
