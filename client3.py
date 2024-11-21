import requests
import random
import time
from datetime import datetime

# URL-ul serverului FastAPI
SERVER_URL = "http://localhost:8000/update"


def generate_random_data():
    """Generează valori aleatorii pentru temperatură, umiditate și adaugă un ID fix."""
    temperature = round(random.uniform(15.0, 20.0), 2)  # Temperatură între 15.0 și 20.0 °C
    humidity = round(random.uniform(30.0, 45.0), 2)     # Umiditate între 30% și 45%
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_value = "raul"  # ID fixat la "alex"
    return {"id": id_value, "temperature": temperature, "humidity": humidity, "timestamp": timestamp}


def send_data():
    """Trimite date către server."""
    while True:
        data = generate_random_data()
        print(f"Sending data: {data}")
        try:
            # Trimiterea datelor ca JSON în corpul cererii
            response = requests.post(SERVER_URL, json=data)
            if response.status_code == 200:
                print(f"Server response: {response.json()}")
            else:
                print(f"Failed to send data. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
        time.sleep(1)  # Așteaptă 1 secundă înainte de a trimite din nou


if __name__ == "__main__":
    send_data()
