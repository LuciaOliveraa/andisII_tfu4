import requests
import json
import time

BASE_URL = "http://localhost:8000"

def demo_valet_and_gatekeeper():
    print("\n--- Demostración de los patrones Gatekeeper + Valet Key ---\n")

    #Solicitar un token temporal 
    print("Solicitando un token con permiso 'recipes:read'")
    response = requests.post(f"{BASE_URL}/valet/token", json={"scopes": ["recipes:read"]})
    valet_key = response.json().get("token")
    print(f"Token recibido: {valet_key[:40]}")

    #Usar el token para acceder a un endpoint protegido por Gatekeeper
    print("\n Accediendo a /recipes con token válido (permiso correcto)")
    headers = {"Authorization": f"Bearer {valet_key}"}
    r = requests.get(f"{BASE_URL}/recipes", headers=headers)
    print(f" Respuesta ({r.status_code}): {r.text}")

    #Probar acceso SIN token
    print("\n Intentando acceder sin token...")
    r = requests.get(f"{BASE_URL}/recipes")
    print(f" Respuesta ({r.status_code}): {r.text}")

    #Probar acceso con un token con permisos insuficientes
    print("\n Solicitando token con permiso 'recipes:delete' (sin permiso de lectura)...")
    response = requests.post(f"{BASE_URL}/valet/token", json={"scopes": ["recipes:delete"]})
    bad_token = response.json().get("token")

    print(" Intentando acceder a /recipes con token incorrecto...")
    headers = {"Authorization": f"Bearer {bad_token}"}
    r = requests.get(f"{BASE_URL}/recipes", headers=headers)
    print(f" Respuesta ({r.status_code}): {r.text}")


if __name__ == "__main__":
    demo_valet_and_gatekeeper()
