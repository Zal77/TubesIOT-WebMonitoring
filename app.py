from flask import Flask, jsonify, render_template
from flask_mqtt import Mqtt
import pymysql as mysql

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'Kelompok 1'  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
topic = 'TubesIOT/kelompok1/sensor'
topic2 = 'TubesIOT/kelompok1/aktuator'

mqtt_client = Mqtt(app)
dataSensor = [0, 0, 0, 0]

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    global dataSensor
    data = dict(
       topic=message.topic,
       payload=message.payload.decode("utf-8").split("#")
    )
    cleaned_payload = ['0' if element.strip() == 'nan' else element.strip() for element in data['payload']]
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    conn = mysql.connect(
        host='localhost',
        user='root',
        password='',
        db='iot',
        charset='utf8mb4',
        cursorclass=mysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            # Create a new record for each element in the payload
            sql = "INSERT INTO `mqtt` (ultra, suhu, humi, ldr) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (float(cleaned_payload[0]), float(cleaned_payload[1]), float(cleaned_payload[2]), float(cleaned_payload[3])))
        # Commit changes
        conn.commit()
        print("Records inserted successfully")

        dataSensor = [float(value) for value in cleaned_payload]
        aktuator(cleaned_payload)
    finally:
        conn.close()

def aktuator(nilaisensor):
    sensor = [float(value) if value.replace('.', '', 1).isdigit() or value == 'nan' else 0.0 for value in nilaisensor]
    print("Nilai sensor setelah konversi:", sensor)

    if not sensor:
        print("Data sensor tidak berisi angka. Skipping...")
        return

    pompa = "PUMPON" if sensor[0] > 30 else "PUMPOFF"
    fan = "FANON" if sensor[1] > 24 else "FANOFF"
    led = "LEDON" if sensor[3] < 700 else "LEDOFF"

    control_message = f"{pompa}#{fan}#{led}"
    print(f"Data Aktuator:\t" + control_message)
    mqtt_client.publish(topic2, control_message)
    
@app.route("/")
def index():
    return render_template("index.html", dataSensor=dataSensor)

if __name__ == '__main__':
    app.run(debug=True)

