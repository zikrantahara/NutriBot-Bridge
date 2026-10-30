import paho.mqtt.client as mqtt
import requests
import os
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
FIREBASE_URL = "https://nutribot-18e6e-default-rtdb.firebaseio.com/NutriBot_Node1/sensor_aktual"
mqtt_client = None

# --- FUNGSI MQTT ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[STATUS] Berhasil Terhubung ke MQTT Broker!")
        client.subscribe("nutribot/sensor/#")
    else:
        print(f"[ERROR] Koneksi MQTT Gagal. Kode: {rc}")

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
            print(f"[UPDATE BERHASIL] {topic} -> {payload} (Status Firebase: {response.status_code})")
        except Exception as e:
            print(f"[ERROR FIREBASE] Gagal memperbarui {topic}: {e}")

def init_mqtt():
    global mqtt_client
    print("▶ Memulai inisialisasi Paho MQTT...")
    try:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        mqtt_client = mqtt.Client()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect("broker.hivemq.com", 1883, 60)
        # Menggunakan loop_start() agar berjalan di background thread Paho bawaan
        mqtt_client.loop_start() 
        print("✅ MQTT Listener (loop_start) aktif!")
    except Exception as e:
        print(f"[ERROR MQTT INIT] Terjadi kesalahan: {e}")

# --- RUTINITAS FLASK & SCHEDULER ---
@app.route('/')
def home():
    return "✅ NutriBot Bridge is Running 24/7 with APScheduler!"

if __name__ == "__main__":
    # Menjalankan inisialisasi MQTT sebelum Flask start
    init_mqtt()
    
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Memulai web server Flask di port {port}...")
    
    # use_reloader=False SANGAT PENTING agar MQTT tidak di-start 2 kali oleh Flask
    app.run(host='0.0.0.0', port=port, use_reloader=False)