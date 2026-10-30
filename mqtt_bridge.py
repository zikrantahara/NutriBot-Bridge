import paho.mqtt.client as mqtt
import requests
import os
from flask import Flask

# --- 1. DUMMY WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ NutriBot Bridge is Running 24/7!"

# --- 2. LOGIKA MQTT & FIREBASE ---
FIREBASE_URL = "https://nutribot-18e6e-default-rtdb.firebaseio.com/NutriBot_Node1/sensor_aktual"

def on_connect(client, userdata, flags, rc, properties=None):
    print("[STATUS] Terhubung ke MQTT Broker Cloud!")
    client.subscribe("nutribot/sensor/#")

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
        # Tembak data ke Firebase
        response = requests.put(url, data=payload)
        # Berikan log di terminal Render agar Anda bisa memantau
        print(f"[FIREBASE UPDATE] {topic} -> {payload} (Status: {response.status_code})")

if __name__ == "__main__":
    # Menghindari error kompatibilitas Paho-MQTT versi 1.x dan 2.x
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message
    
    print("Menghubungkan ke broker MQTT...")
    client.connect("broker.hivemq.com", 1883, 60)
    
    # 1. Jalankan kurir MQTT di BACKGROUND Thread (Tidak memblokir)
    client.loop_start() 
    
    # 2. Jalankan web server Flask di MAIN Thread
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Memulai web server di port {port}...")
    app.run(host='0.0.0.0', port=port)