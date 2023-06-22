import os
import time
import ujson
import esp32
from umqtt.simple import MQTTClient
from machine import Pin, PWM

# Configura el ciclo de trabajo a 0 para silenciar el BUZZER
CLIENT_ID = "your_client_id"
SERVER = "your_server"
SSL_PARAMS = {"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": "/etc/ca.crt", "keyfile": "/etc/client.key", "certfile": "/etc/client.crt"}
TOPIC_SUB = "your_topic_sub"
TOPIC_PUB = "your_topic_pub"

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

def mqtt_connect(client_id, endpoint, ssl_params):
    mqtt = MQTTClient(
        client_id=client_id,
        server=endpoint,
        ssl_params=ssl_params,
        port=8883,
        keepalive=4000,
        ssl=True
    )
    print('Connecting to AWS IoT...')
    mqtt.connect()
    print('Done')
    return mqtt

def mqtt_publish(client, topic, message=''):
    print('Publishing message...')
    print('TOp', topic)
    client.publish(topic, message)
    print(message)

def mqtt_subscribe(topic, msg):
    print('Message received...')
    print('TOP', topic)
    message = ujson.loads(msg)
    print(topic, message)
    if message['state']['led']:
        led_state(message)
    print('Done')

def led_state(message):
    led.value(message['state']['led']['onboard'])

def mqtt_callback(topic, message):
    print((topic, message))

mqtt = mqtt_connect(CLIENT_ID, SERVER, SSL_PARAMS)
mqtt.set_callback(mqtt_subscribe)
mqtt.subscribe(TOPIC_SUB)


def open_locker(locker, retirar=False):
    locker['relay'].value(ABIERTO)
    locker['cerrado'] = False
    # Actualizar el estado de disponibilidad en caso de que se esté retirando un documento
    if retirar:
        locker['disponible'] = False
    check_locker(locker)

def close_locker(locker, ingresar=False):
    # El locker solo se cierra si está vacío o si se está ingresando un documento
    if locker['locker_vacio'].value() or ingresar:
        locker['relay'].value(CERRADO)
        locker['cerrado'] = True
        # Actualizar el estado de disponibilidad en caso de que se esté ingresando un documento
        if ingresar:
            locker['disponible'] = False
    else:
        # Emitir sonido si se intenta cerrar el locker con documentos dentro
        start_buzzer()
    check_locker(locker)
    
def check_locker(locker):
    # check if the locker is ocupado by reading the sensor
    lockers[locker]["ocupado"] = lockers[locker]["puerta_cerrada"].value()

def start_buzzer():
		# Configura la frecuencia del BUZZER (por ejemplo, 440 Hz para la nota A4)
		buzzer.freq(440)
		# Configura el ciclo de trabajo para que el BUZZER suene (0-1023, donde 512 es aproximadamente el 50%)
		buzzer.duty(512)
  
def stop_buzzer():
		# Configura el ciclo de trabajo para que el BUZZER suene (0-1023, donde 512 es aproximadamente el 50%)
		buzzer.duty(0)

def update_shadow(mqtt_client, locker_id):
    # fetch the state of the locker
    locker = lockers[locker_id]

    # create the payload for the shadow update
    payload = {
        "state": {
            "reported": {
                "rut": locker['rut'],
                "hora_ocupacion": locker['hora_ocupacion'],
                "hora_desocupacion": locker['hora_desocupacion'],
                "cerrado": locker['cerrado'],
                "ocupado": locker['ocupado'],
                "disponible": locker['disponible']
            }
        }
    }

    # publish the shadow update
    topic = "$aws/things/{}/shadow/update".format(locker_id)
    mqtt_publish(mqtt_client, topic, ujson.dumps(payload))

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
    # and so on for other possible actions

mqtt.set_callback(process_message)

while True:
    # periodically check for messages
    mqtt.check_msg()
    
    all_lockers_closed = True
    
    # check the state of each locker
    for locker in lockers:
        check_locker(locker)
        update_shadow(mqtt, locker)
        if lockers[locker]["ocupado"] and not lockers[locker]["cerrado"]:
            # if the locker is ocupado and not closed, beep the buzzer
            start_buzzer()
            all_lockers_closed = False

    if all_lockers_closed:
        stop_buzzer()

    # publish the current state of the lockers
    mqtt_publish(mqtt, TOPIC_PUB, ujson.dumps(lockers))
    
    # sleep for a bit before the next iteration
    time.sleep(0.1)
    


