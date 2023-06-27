from machine import Pin
from time import sleep

# Definiciones
# Recordar que los reles se activan con nivel BAJO (0)
RELAY_ON = 0
RELAY_OFF = 1

# Definir los pines como salida para los reles
relay1 = Pin(27, Pin.OUT)
relay2 = Pin(26, Pin.OUT)
relay3 = Pin(25, Pin.OUT)
relay4 = Pin(33, Pin.OUT)

# Definir los pines como entrada para los sensores infrarrojos
sensor1 = Pin(32, Pin.IN)
sensor2 = Pin(35, Pin.IN)
sensor3 = Pin(34, Pin.IN)

# Asegurar nivel ALTO en cada entrada de rele
relay1.value(RELAY_OFF)
relay2.value(RELAY_OFF)
relay3.value(RELAY_OFF)
relay4.value(RELAY_OFF)

while True:
    relay1.value(RELAY_ON)  # Activa relé 1
    sleep(2)
    relay1.value(RELAY_OFF)  # Desactiva relé 1
    sleep(2)
