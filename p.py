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
    #process_message(topic, message)  # Agregado para procesar los mensajes recibidos
