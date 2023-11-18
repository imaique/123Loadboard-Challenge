# python3.6
"""
host: fortuitous-welder.cloudmqtt.com
port: 1883 (non SSL)
user: CodeJamUser
password: 123CodeJam

cleanSession: true  // important
QoS: 1
clientId: "<team name>01" // see important note below
Topic: CodeJam
"""
from message_processor import MessageProcessor
from paho.mqtt import client as mqtt_client


BROKER = "fortuitous-welder.cloudmqtt.com"
PORT = 1883
TOPIC = "CodeJam"
CLIENT_ID = "kazumike01"
USERNAME = "CodeJamUser"
PASSWORD = "123CodeJam"

mess_processor = MessageProcessor()



def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(CLIENT_ID, clean_session=True)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        message = msg.payload.decode()
        mess_processor.add_raw_message(message)
        print(f"Received `{message}` from `{msg.topic}` topic")

    client.subscribe(TOPIC)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
