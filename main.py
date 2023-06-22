from machine import Pin, PWM
import os
import time
import ujson
import esp32
import network
from umqtt.simple import MQTTClient

# Wi-Fi details
WIFI_SSID = 'wifi-campus'
WIFI_PASSWORD = 'uandes2200'

# AWS IoT Core details
SERVER = 'a1ji7xd8yopagp-ats.iot.us-east-2.amazonaws.com'
CLIENT_ID = 'cerraduras-Esp32'
TOPIC_PUB = '$aws/things/' + CLIENT_ID + '/shadow/update'
TOPIC_SUB = '$aws/things/' + CLIENT_ID + '/shadow/update/delta'

# Connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass

print('Connection successful')
print('Network config:', wlan.ifconfig())

# Load AWS certificates
with open('a6750dee-private.pem.key', 'r') as f:
    key = f.read()
with open('a6750dee-certificate.pem.crt', 'r') as f:
    cert = f.read()

SSL_PARAMS = { 'key': key, 'cert': cert, 'server_side': False }

#define pins of buzzer
BUZZER_PIN = 13

# define the pins for the relays, sensors 1
LOCKER1_RELAY_PIN = 27
LOCKER1_SENSOR_DOOR_PIN = 12
LOCKER1_SENSOR_VACIO_PIN = 14
# define the pins for the relays, sensors 2
LOCKER2_RELAY_PIN = 26
LOCKER2_SENSOR_DOOR_PIN = 33
LOCKER2_SENSOR_VACIO_PIN = 32
# define the pins for the relays, sensors 3
LOCKER3_RELAY_PIN = 25
LOCKER3_SENSOR_DOOR_PIN = 35
LOCKER3_SENSOR_VACIO_PIN = 34

# initialize the pins locker 1
locker1_relay = Pin(LOCKER1_RELAY_PIN, Pin.OUT)
locker1_sensor_DOOR = Pin(LOCKER1_SENSOR_DOOR_PIN, Pin.IN)
locker1_sensor_VACIO = Pin(LOCKER1_SENSOR_VACIO_PIN, Pin.IN)
# initialize the pins locker 2
locker2_relay = Pin(LOCKER2_RELAY_PIN, Pin.OUT)
locker2_sensor_DOOR = Pin(LOCKER2_SENSOR_DOOR_PIN, Pin.IN)
locker2_sensor_VACIO = Pin(LOCKER2_SENSOR_VACIO_PIN, Pin.IN)
# initialize the pins locker 3
locker3_relay = Pin(LOCKER3_RELAY_PIN, Pin.OUT)
locker3_sensor_DOOR = Pin(LOCKER3_SENSOR_DOOR_PIN, Pin.IN)
locker3_sensor_VACIO = Pin(LOCKER3_SENSOR_VACIO_PIN, Pin.IN)

CERRADO = 0
ABIERTO = 1000

# create a dictionary to store the lockers' states
lockers = {
    "locker1": {"relay": locker1_relay, 
                "puerta_cerrada": locker1_sensor_DOOR, 
                "locker_vacio": locker1_sensor_VACIO, 
                "ocupado": False, 
                "cerrado": True, 
                "hora_ocupacion": None,
                "hora_desocupacion": None, 
                "rut": None, 
                "disponible": True},
    
    "locker2": {"relay": locker2_relay, 
                "puerta_cerrada": locker2_sensor_DOOR, 
                "locker_vacio": locker2_sensor_VACIO, 
                "ocupado": False, 
                "cerrado": True, 
                "hora_ocupacion": None,
                "hora_desocupacion": None, 
                "rut": None, 
                "disponible": True},
    
    "locker3": {"relay": locker3_relay, 
                "puerta_cerrada": locker3_sensor_DOOR, 
                "locker_vacio": locker3_sensor_VACIO, 
                "ocupado": False, 
                "cerrado": True, 
                "hora_ocupacion": None,
                "hora_desocupacion": None, 
                "rut": None, 
                "disponible": True},
}

# Set initial relay states to CERRADO 
for locker in lockers.values():
    locker['relay'].value(CERRADO)

# Crea un objeto PWM para controlar el BUZZER
buzzer = PWM(Pin(BUZZER_PIN))


## CODIGO DE CONECTION CON AWS IoT Core MQTT Client

# Function to initialize the AWS IoT Core MQTT Client
def connect_to_mqtt():
    client = MQTTClient(client_id=CLIENT_ID, server=SERVER, port=8883, ssl=True, ssl_params=SSL_PARAMS)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(TOPIC_SUB)
    print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC_SUB))
    return client

# Function to publish a message to the AWS IoT Core MQTT Client
def mqtt_publish(client, topic, message):
    client.publish(topic, message)

def mqtt_callback(topic, message):
    print((topic, message))
    process_message(topic, message)  # Agregado para procesar los mensajes recibidos

# Function to handle the locker data
def locker_data(locker):
    locker_data = {
        "ocupado": locker["ocupado"],
        "cerrado": locker["cerrado"],
        "hora_ocupacion": locker["hora_ocupacion"],
        "hora_desocupacion": locker["hora_desocupacion"],
        "rut": locker["rut"],
        "disponible": locker["disponible"]
    }
    return locker_data

# Function to update the shadow of a locker
def update_locker_shadow(client, locker_name):
    shadow_message = {
        "state": {
            "reported": {
                locker_name: locker_data(lockers[locker_name])
            }
        }
    }
    shadow_message_str = ujson.dumps(shadow_message)
    mqtt_publish(client, TOPIC_PUB, shadow_message_str)

def process_message(topic, msg):
    message = ujson.loads(msg)
    if "action" in message:
        if message["action"] == "open":
            # Identificar si se está retirando un documento
            retirar = message.get("retirar", False)
            open_locker(message["locker"], retirar=retirar)
        elif message["action"] == "close":
            # Identificar si se está ingresando un documento
            ingresar = message.get("ingresar", False)
            close_locker(message["locker"], ingresar=ingresar)



## CODIGO DE LOGICA 
def open_locker(locker_name, retirar=False):
    print("Entre a Open_Locker")
    locker = lockers[locker_name]
    locker['relay'].value(ABIERTO)
    locker['cerrado'] = False
    if retirar:
        locker['disponible'] = False
        locker['hora_desocupacion'] = time.time()  # Actualiza la hora de desocupación
    check_locker(locker_name)

def close_locker(locker_name, ingresar=False):
    print("Entre a close_locker")
    locker = lockers[locker_name]
    if locker['locker_vacio'].value() or ingresar:
        locker['relay'].value(CERRADO)
        locker['cerrado'] = True
        if ingresar:
            locker['disponible'] = False
            locker['hora_ocupacion'] = time.time()  # Actualiza la hora de ocupación
    else:
        start_buzzer()
        time.sleep(1)  # Espera un segundo antes de verificar el locker
        check_locker(locker_name)
        stop_buzzer()  # Detiene el buzzer después de la verificación

def check_locker(locker_name):
    print("Entre a check_locker")
    locker = lockers[locker_name]
    locker["ocupado"] = locker["puerta_cerrada"].value()

def start_buzzer():
		# Configura la frecuencia del BUZZER (por ejemplo, 440 Hz para la nota A4)
		buzzer.freq(440)
		# Configura el ciclo de trabajo para que el BUZZER suene (0-1023, donde 512 es aproximadamente el 50%)
		buzzer.duty(512)
  
def stop_buzzer():
		# Configura el ciclo de trabajo para que el BUZZER suene (0-1023, donde 512 es aproximadamente el 50%)
		buzzer.duty(0)

def main():
    # Connect to MQTT
    client = connect_to_mqtt()
    
    while True:
        # Check and update the state of each locker
        for locker_name, locker in lockers.items():
            if locker["relay"].value() == 1000:
                locker["cerrado"] = False
            else:
                locker["cerrado"] = True
            
            if locker["locker_vacio"].value() == 1:
                locker["ocupado"] = False
            else:
                locker["ocupado"] = True
                
            # Update the shadow of the locker
            update_locker_shadow(client, locker_name)

        # Non-blocking wait for message
        client.check_msg()
        time.sleep(1)
        
if __name__ == "__main__":
    main()

