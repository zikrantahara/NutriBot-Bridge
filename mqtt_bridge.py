import paho.mqtt.client as mqtt
import requests
import os
import multiprocessing
from flask import Flask

# --- 1. DUMMY WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ NutriBot Bridge is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Memulai web server di port {port}...")
    # Menonaktifkan reloader agar tidak menjalankan ulang MQTT process
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# --- 2. LOGIKA MQTT & FIREBASE ---
FIREBASE_URL = "https://nutribot-18e6e-default-rtdb.firebaseio.com/NutriBot_Node1/sensor_aktual"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[STATUS] Terhubung ke MQTT Broker Cloud!")
        client.subscribe("nutribot/sensor/#")
    else:
        print(f"[ERROR] Gagal terhubung ke MQTT Broker. Kode: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    firebase_path = ""
    if topic == "nutribot/sensor/volume_air": firebase_path = "/volume_air_persen.json"
    elif topic == "nutribot/sensor/level_nutrisi": firebase_path = "/level_nutrisi_persen.json"
    elif topic == "nutribot/sensor/tds": firebase_path = "/tds.json"
    elif topic == "nutribot/sensor/ph": firebase_path = "/ph_air.json"

    if firebase_path:
        url = FIREBASE_URL + firebase_path
        try:
            response = requests.put(url, data=payload)
            print(f"[FIREBASE UPDATE] {topic} -> {payload} (Status: {response.status_code})")
        except Exception as e:
            print(f"[ERROR FIREBASE] Gagal memperbarui {topic}: {e}")

def run_mqtt():
    print("Menghubungkan ke broker MQTT...")
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message
    
    # Menggunakan loop_forever() karena sudah berada di process terpisah
    try:
        client.connect("broker.hivemq.com", 1883, 60)
        client.loop_forever()
    except Exception as e:
        print(f"[ERROR MQTT] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    # Menjalankan MQTT dan Flask pada Process yang benar-benar terpisah
    mqtt_process = multiprocessing.Process(target=run_mqtt)
    flask_process = multiprocessing.Process(target=run_flask)

    mqtt_process.start()
    flask_process.start()

    mqtt_process.join()
    flask_process.join()