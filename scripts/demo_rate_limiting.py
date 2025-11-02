# scripts/demo_rate_limiter.py
import requests
import time

BASE_URL = "http://localhost:8000"  

def demo_rate_limiting():
    print("\n--- Demostración del patrón Rate Limiting ---\n")
    for i in range(15):  
        response = requests.get(f"{BASE_URL}/")
        print(f"Request {i+1}: {response.status_code} -> {response.text}")
        if response.status_code == 429:  
            print("Límite de peticiones alcanzado: bloqueo de solicitudes.")
            break
        time.sleep(0.5)  

if __name__ == "__main__":
    demo_rate_limiting()
