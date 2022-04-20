import random

from paho.mqtt import client as mqtt_client


broker = 'broker.mqttdashboard.com'
port = 1883
topic = "/eyetracking/image"
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'user'
# password = 'pass'
PATH = None


def connect_mqtt() -> mqtt_client:
  print('Awaiting for image path...')
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print(".")
    else:
      print("Failed to connect, return code %d\n", rc)

  client = mqtt_client.Client(client_id)
  #client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client


def subscribe(client: mqtt_client):
  def on_message(client, userdata, msg):
    global PATH
    PATH = str(msg.payload.decode())
    client.disconnect()

  client.subscribe(topic)
  client.on_message = on_message

def run():
  client = connect_mqtt()
  subscribe(client)
  client.loop_forever()

def get_image_path():
  run()
  return PATH