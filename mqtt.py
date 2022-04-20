import random
import time
from paho.mqtt import client as mqtt_client


broker = 'broker.mqttdashboard.com'
port = 1883
subscribe_topic = "/eyetracking/image"
publishing_topic = "/movement/instructions"
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'user'
# password = 'pass'
PATH = None


def connect_mqtt() -> mqtt_client:
  def on_connect(client, userdata, flags, rc):
    if rc != 0:
      print("Failed to connect, return code %d\n", rc)

  client = mqtt_client.Client(client_id)
  #client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

def publish(client, message):
  result = client.publish(publishing_topic, message)
  status = result[0]
  if status == 0:
    print(f"Send `{message}` to topic `{publishing_topic}`")
  else:
    print(f"Failed to send message to topic {publishing_topic}")

def subscribe(client: mqtt_client):
  def on_message(client, userdata, msg):
    global PATH
    PATH = str(msg.payload.decode())
    client.disconnect()

  client.subscribe(subscribe_topic)
  client.on_message = on_message

def run():
  client = connect_mqtt()
  subscribe(client)
  client.loop_forever()

def get_image_path():
  print('Awaiting for image path...')
  run()
  return PATH