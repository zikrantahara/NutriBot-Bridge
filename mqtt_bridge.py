import paho.mqtt.client as mqtt
import requests
import threading
import os
from flask import Flask

# --- 1. DUMMY WEB SERVER (Agar tidak dimatikan Cloud) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "✅ NutriBot Bridge is Running 24/7!"

def run_web():
    # Render otomatis memberikan port secara acak, kita harus menangkapnya
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. LOGIKA MQTT & FIREBASE ---
FIREBASE_URL = "https://nutribot-18e6e-default-rtdb.firebaseio.com/NutriBot_Node1/sensor_aktual"

def on_connect(client, userdata, flags, rc):
    print("[STATUS] Terhubung ke MQTT Broker Cloud!")
    client.subscribe("nutribot/sensor/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    firebase_path = ""
    if topic == "nutribot/sensor/volume_air": firebase_path = "/volume_air_persen.json"
    elif topic == "nutribot/sensor/level_nutrisi": firebase_path = "/level_nutrisi_persen.json"
    elif topic == "nutribot/sensor/suhu": firebase_path = "/suhu_air.json"
    elif topic == "nutribot/sensor/ph": firebase_path = "/ph_air.json"

    if firebase_path:
        requests.put(FIREBASE_URL + firebase_path, data=payload)

if __name__ == "__main__":
    # Jalankan web server di jalur (thread) terpisah
    threading.Thread(target=run_web).start()
    
    # Jalankan kurir MQTT di jalur utama
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()