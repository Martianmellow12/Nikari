# Nikari - Zigbee Device Management Library
#
# Written by Martianmellow12

from corelib import coredb

import paho.mqtt.client as mqtt
import time

client = mqtt.Client("dummy")
mq = list()

def on_connect(client, userdata, flags, rc):
    if rc == 0: print("CONNECTED")
    else: print("FAILED TO CONNECT")

def on_msg(client, userdata, msg):
    global mq
    mq.append(f"RCV <{msg.topic}>: {msg.payload.decode()}")

client.on_connect = on_connect
client.on_message = on_msg
client.connect("127.0.0.1")
client.loop_start()
client.subscribe("zigbee2mqtt/bridge/devices")
client.subscribe("zigbee2mqtt/test_button/#")
#client.publish("zigbee2mqtt/bridge/devices")
while True:
    try: pass
    except Exception: break
    time.sleep(5)
    print(mq)
    mq.clear()

client.loop_stop()
