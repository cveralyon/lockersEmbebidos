from machine import Pin
import network
import os
import time
import ujson
import esp32
from umqtt.simple import MQTTClient

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


mqtt = mqtt_connect(CLIENT_ID, SERVER, SSL_PARAMS)
mqtt.set_callback(mqtt_subscribe)
mqtt.subscribe(TOPIC_SUB)

WIFI_SSID = 'wifi-campus'
WIFI_PASSWORD = 'uandes2200'

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

# Initialize led
led = Pin(2, Pin.OUT)
info = os.uname()

while True:
    try:
        mqtt.check_msg()
    except:
        print('Unable to check for messages.')

    mesg = ujson.dumps({
        'state':{
            'reported': {
                'device': {
                    'client': CLIENT_ID,
                    'uptime': time.ticks_ms(),
                    'hardware': info[0],
                    'firmware': info[2]
                },
                'sensors': {
                    'hall_sensor': esp32.hall_sensor()
                },
                'led': {
                    'onboard': led.value()
                }
            }
        }
    })

    try:
        mqtt_publish(client=mqtt, message=mesg, topic=TOPIC_PUB)
    except:
        print('Unable to publish message.')

    print('Sleep for 10 second')
    time.sleep(10)
