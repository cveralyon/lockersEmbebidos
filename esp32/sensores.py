from machine import Pin, PWM
import time

# define pins of buzzer
BUZZER_PIN = 13

LOCKER1_SENSOR_DOOR_PIN = 12
LOCKER1_SENSOR_VACIO_PIN = 14

LOCKER2_SENSOR_DOOR_PIN = 33
LOCKER2_SENSOR_VACIO_PIN = 32

LOCKER3_SENSOR_DOOR_PIN = 35
LOCKER3_SENSOR_VACIO_PIN = 34

# initialize the pins locker 1
locker1_sensor_DOOR = Pin(LOCKER1_SENSOR_DOOR_PIN, Pin.IN)
locker1_sensor_VACIO = Pin(LOCKER1_SENSOR_VACIO_PIN, Pin.IN)
# initialize the pins locker 2
locker2_sensor_DOOR = Pin(LOCKER2_SENSOR_DOOR_PIN, Pin.IN)
locker2_sensor_VACIO = Pin(LOCKER2_SENSOR_VACIO_PIN, Pin.IN)
# initialize the pins locker 3
locker3_sensor_DOOR = Pin(LOCKER3_SENSOR_DOOR_PIN, Pin.IN)
locker3_sensor_VACIO = Pin(LOCKER3_SENSOR_VACIO_PIN, Pin.IN)

buzzer = PWM(Pin(BUZZER_PIN))

def start_buzzer():
    # Configura la frecuencia del BUZZER (por ejemplo, 440 Hz para la nota A4)
    buzzer.freq(440)
    # Configura el ciclo de trabajo para que el BUZZER suene (0-1023, donde 512 es aproximadamente el 50%)
    buzzer.duty(512)
  
def stop_buzzer():
    # Configura el ciclo de trabajo para que el BUZZER suene (0-1023, donde 512 es aproximadamente el 50%)
    buzzer.duty(0)

# Sensor y estado de vacío
door_sensors = [locker1_sensor_DOOR, locker2_sensor_DOOR, locker3_sensor_DOOR]
empty_sensors = [locker1_sensor_VACIO, locker2_sensor_VACIO, locker3_sensor_VACIO]

buzzer.duty(0)
while True:
    for sensor in door_sensors:
        if sensor.value() == 0: # Sensor de puerta: No detecta nada, la puerta está abierta
            start_buzzer()
            time.sleep(0.5) # Tiempo que suena el buzzer
            stop_buzzer()

    for sensor in empty_sensors:
        if sensor.value() == 1: # Sensor de vacío: Detecta algo, el locker no está vacío
            start_buzzer()
            time.sleep(0.5) # Tiempo que suena el buzzer
            stop_buzzer()
            
    time.sleep(0.1) # Pequeña pausa para no sobrecargar el procesador
