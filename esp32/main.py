from mqtt_as import MQTTClient, config
import uasyncio as asyncio
import machine
import time
import ujson
from BME280 import BME280Sensor
TOPIC = "W000001" 
# instantierea obiectului pentru senzorul BME280
sensor = BME280Sensor()
time.sleep(2)

def format_data_to_json(serial_number, temp, press, hum):
  """
    Aceasta metoda formateaza datele intr-un format json
    si returneaza rezultatul
  """
  dictionary = {
    "duid" : serial_number,
    "temp" : temp,
    "press": press,
    "hum"  : hum
  }
  return ujson.dumps(dictionary)

async def wifi_han(state):
    """
      Handler function. Aceasta functie va verifica mereu daca wi-fi-ul sau brokerul
      este conectat
    """
    global STATUS_ERROR_CODE
    if state:
        print('We are connected to broker.')
    else:        
        print('WiFi or broker is down.')
    await asyncio.sleep(1)


def sub_cb(topic, msg, retained):
  """
    Callback function. Atunci cand un mesaj vine pe topicul la care suntem
    abonati, aceasta functie va interpreta acel mesaj
  """
  global msg_received
  print((topic, msg))    
  msg_received = msg.decode("utf-8")


async def conn_han(client):
  """
    Callback function. Dupa conectarea la broker aceasta functie va face subscribe
    la topicul specificat
  """
  await client.subscribe(TOPIC, 1)  

msg_received = ""

async def main(client):
    """
      Aceasta functie contine un while loop care asteapta o comanda prin MQTT, daca comanda este BURSTREAD
      atunci va incepe sa citeasca temperatura, presiunea si umiditatea iar mai apoi
      va trimite datele citite inapoi prin MQTT catre aplicatia WEB
      
      Citirile se pot face cu un interval de 5 secunde intre ele
    """
    global msg_received
    global outages
    global STATUS_ERROR_CODE
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        machine.reset()
        return
    while True:        
        await asyncio.sleep(5)
        if(msg_received == "BURSTREAD"):      
          temp = sensor.read_temperature_celsius_degrees()
          press = sensor.read_pressure_hpa()
          hum = sensor.read_humidity_percent()
          await client.publish(TOPIC, format_data_to_json(TOPIC, temp, press, hum), qos = 1)
          msg_received = ""

"""
  Parametrii deconfigurare pentru ESP32 MQTT
  (1) - MQTT Broker
  (2) - Numele Wi-fi-ului la care se va conecta microcontrollerul
  (3) - Parola de wi-fi
  (4) - callback function, va fi apelata cand un mesaj va fi primit
  (5) - Last Will, acest mesaj va fi tirmis in caz ca dispozitivul pierde conexiunea
  (6) - topicul care se va folosi pentru a primi si trimite mesaje prin MQTT
        Actioneaza si ca valoare pentru serial number
"""
config['server'] = "broker.hivemq.com"                           #(1)
config['ssid'] = "esp32"                                         #(2) 
config['wifi_pw'] = "esp32test"                                  #(3)
config['subs_cb'] = sub_cb                                       #(4)
config['wifi_coro'] = wifi_han
config['will'] = (TOPIC, 'Conexiunea a fost pierduta', False, 0) #(5)
config['connect_coro'] = conn_han
config['keepalive'] = 120
TOPIC = "W000001"                                                #(6)
# Instantierea obiectului de MQTT client
client = MQTTClient(config)

# pornirea aplicatiei
try:
    MQTTClient.DEBUG = True
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()

