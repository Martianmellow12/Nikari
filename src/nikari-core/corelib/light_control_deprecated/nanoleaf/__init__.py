# Huginn - Nanoleaf Light Integration
#
# Written by Martianmellow12

# General
import colorsys
import json
import os
import pathlib
import requests
import sys

# Support
sys.path.append("..")
from support import config
from support.huginn_logging import log


####################
# Helper Functions #
####################

def rgb_to_hsv(r, g, b):
    # Normalize r,g,b
    r = r/255.0
    g = g/255.0
    b = b/255.0

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Correct h,s,v
    h = int(h*360)
    s = int(s*100)
    v = int(v*100)

    return (h, s, v)


########################
# Nanoleaf Light Class #
########################

class NanoleafLight:

    def __init__(self, ip_addr, auth_token):
        self.ip_addr = ip_addr
        self.auth_token = auth_token
        self.url = f"http://{self.ip_addr}:16021/api/v1/{self.auth_token}"

    #########################
    # State Control Methods #
    #########################

    def get_state(self):
        req_url = f"{self.url}/state/on"
        resp_url = f"{self.url}/state"
        body = {
            "on":{
                "value":None
            }
        }

        resp_json = requests.get(req_url).json()
        return resp_json["value"]

    def set_state(self, on: bool):
        url = f"{self.url}/state"
        body = {
            "on":{
                "value":on
            }
        }
        body_json = json.dumps(body)
        resp = requests.put(url, body_json)
        return resp.status_code
    
    def toggle_state(self):
        req_url = f"{self.url}/state/on"
        resp_url = f"{self.url}/state"
        body = {
            "on":{
                "value":None
            }
        }

        resp_json = requests.get(req_url).json()
        body["on"]["value"] = not resp_json["value"]
        body_json = json.dumps(body)
        resp = requests.put(resp_url, body_json)
        return resp.status_code
    
    def set_brightness(self, value: int, duration: int=0):
        url = f"{self.url}/state"
        body = {
            "brightness":{
                "value": value
            }
        }
        if duration != 0:
            body["brightness"]["duration"] = duration
        body_json = json.dumps(body)
        resp = requests.put(url, body_json)
        return resp.status_code
        
    def set_hue(self, value: int):
        url = f"{self.url}/state"
        body = {
            "hue":{
                "value": value
            }
        }
        body_json = json.dumps(body)
        resp = requests.put(url, body_json)
        return resp.status_code
    
    def set_saturation(self, value: int):
        url = f"{self.url}/state"
        body = {
            "sat":{
                "value": value
            }
        }
        body_json = json.dumps(body)
        resp = requests.put(url, body_json)
        return resp.status_code
    
    def set_rgb(self, rgb_tuple):
        r, g, b = rgb_tuple
        h, s, v = rgb_to_hsv(r, g, b)
        url = f"{self.url}/state"
        body = {
            "hue":{
                "value":h
            },
            "sat":{
                "value":s
            },
            "brightness":{
                "value":v
            }
        }
        body_json = json.dumps(body)
        resp = requests.put(url, body_json)
        return resp.status_code
    

########################
# Nanoleaf Group Class #
########################

class NanoleafGroup:

    def __init__(self, room_name=None):
        self.room_name = room_name
        self.path = pathlib.Path(__file__).parent.resolve()
        self.config_path = os.path.join(self.path, "config.json")

        config.set_config_path(self.config_path)
        self.config = config.read_config()
        self.lights = list()

        if self.room_name == None:
            for i in self.config.keys():
                self.lights += [NanoleafLight(j["ip_addr"], j["auth_token"]) for j in self.config[i]]
        elif self.room_name not in self.config.keys():
            raise Exception(f"Room \"{self.room_name}\" doesn't exist in the config file")
        else:
            self.lights = [NanoleafLight(j["ip_addr"], j["auth_token"]) for j in self.config[self.room_name]]
    

    #########################
    # State Control Methods #
    #########################

    def get_state(self):
        return [i.get_state() for i in self.lights]
    
    def set_state(self, state):
        return [i.set_state(state) for i in self.lights]
    
    def toggle_state(self):
        if True in self.get_state():
            self.set_state(False)
        else:
            self.set_state(True)

    def set_brightness(self, value, duration=0):
        return [i.set_brightness(value, duration) for i in self.lights]
    
    def set_hue(self, value):
        return [i.set_hue(value) for i in self.lights]
    
    def set_saturation(self, value):
        return [i.set_saturation(value) for i in self.lights]
    
    def set_rgb(self, rgb_tuple):
        return [i.set_rgb(rgb_tuple) for i in self.lights]
    

####################################
# Standard Light Control Functions #
####################################

def process(command, arguments):

    # Light Control
    if command == "light_control":
        if "room_name" not in arguments.keys():
            log("nanoleaf", "Creating lighting group with all lights", indent_level=2, show_time=False)
            lights = NanoleafGroup()
        else:
            log("nanoleaf", f"Creating lighting group with <{arguments['room_name']}> lights", indent_level=2, show_time=False)
            lights = NanoleafGroup(arguments["room_name"])
        if "state" in arguments.keys():
            log("nanoleaf", f"Setting lights to state <{arguments['state']}>", indent_level=2, show_time=False)
            lights.set_state(arguments["state"])
        if ("toggle" in arguments.keys()) and (arguments["toggle"] == True):
            log("nanoleaf", "Toggling lights", indent_level=2, show_time=False)
            lights.toggle_state()
        if "brightness" in arguments.keys():
            log("nanoleaf", f"Settting lights to brightness <{arguments['brightness']}>", indent_level=2, show_time=False)
            lights.set_brightness(arguments['brightness'])
        if "hue" in arguments.keys():
            log("nanoleaf", f"Setting lights to hue <{arguments['hue']}>", indent_level=2, show_time=False)
            lights.set_hue(arguments["hue"])
        if "saturation" in arguments.keys():
            log("nanoleaf", f"Setting lights to saturation <{arguments['saturation']}>", indent_level=2, show_time=False)
            lights.set_saturation(arguments["saturation"])
        if "rgb" in arguments.keys():
            log("nanoleaf", f"Setting lights to rgb <{arguments['rgb']}>", indent_level=2, show_time=False)
            lights.set_rgb(arguments["rgb"])