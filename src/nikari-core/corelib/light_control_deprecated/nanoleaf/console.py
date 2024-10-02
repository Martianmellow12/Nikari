# Huginn - Nanolead Library Console
#
# Written by Martianmellow12

# General
import os
import pathlib
import requests
import sys

# Support
sys.path.append(os.path.join("..", "..", "..", ".."))
from support import config


####################
# Global Variables #
####################

PATH = pathlib.Path(__file__).parent.resolve()
CONFIG_PATH = os.path.join(PATH, "config.json")


####################
# Console Mainloop #
####################

# Initialization
config.set_config_path(CONFIG_PATH)
config_obj = config.read_config()
print(f"Loaded config from {CONFIG_PATH}")
print(f"Loaded {len(config_obj.keys())} rooms")

# Main loop
while True:
    cmd = str(input("Nanoleaf > "))

    if cmd == "add":
        ip_addr = str(input("  IP address > "))
        input("Put the device into auth mode (hold the power button until the lights flash), then press <return>")

        url = f"http://{ip_addr}:16021/api/v1/new"
        resp = requests.post(url)
        if resp.status_code != 200:
           print("Failed to get auth token")
           continue
        auth_token = resp.json()["auth_token"]
        print(f"Received auth token: {auth_token}")

        light_name = str(input("  Light name > "))
        room_name = str(input("  Room name > "))
        if room_name not in config_obj.keys():
            config_obj[room_name] = list()
            print(f"Added room <{room_name}> to the config")
        light_obj = {
            "name" : light_name,
            "ip_addr" : ip_addr,
            "auth_token" : auth_token
        }
        config_obj[room_name].append(light_obj)
        config.write_config(config_obj)
        print("Saved light to config file")