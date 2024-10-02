# Nikari Device Control Library - Nanoleaf Extension
#
# Written by Martianmellow12

# General
import json
import requests

# Local
from . import DeviceBase, make_attr, register_type


###################
# Nanoleaf Device #
###################
        
@register_type("nanoleaf")
class DeviceNanoleaf(DeviceBase):

    ##################
    # Static Methods #
    ##################

    @staticmethod
    async def add_new_device():
        device_template = {
            "type" : "nanoleaf",
            "friendly_name" : None,
            "metadata" : {
                "ip_addr" : None,
                "auth_token" : None
            },
            "attributes" : [
                {
                    "type" : "binary",
                    "name" : "state",
                    "label" : "State",
                    "property" : "state",
                    "value_on" : "ON",
                    "value_off" : "OFF",
                    "value_toggle" : "TOGGLE",
                    "access" : 7,
                    "cached" : "OFF",
                    "cached_vld" : False
                },
                {
                    "type" : "numeric",
                    "name" : "brightness",
                    "label" : "Brightness",
                    "property" : "brightness",
                    "value_min" : 0,
                    "value_max" : 100,
                    "access" : 7,
                    "cached" : 0,
                    "cached_vld" : False
                },
                {
                    "type" : "numeric",
                    "name" : "brightness_change_duration",
                    "label" : "Brightness Change Duration",
                    "property" : "brightness_change_duration",
                    "access" : 7,
                    "cached" : 0,
                    "cached_vld" : False
                },
                {
                    "type" : "numeric",
                    "name" : "hue",
                    "label" : "Hue",
                    "property" : "hue",
                    "value_min" : 0,
                    "value_max" : 360,
                    "access" : 7,
                    "cached" : 0,
                    "cached_vld" : False
                },
                {
                    "type" : "numeric",
                    "name" : "saturation",
                    "label" : "Saturation",
                    "property" : "saturation",
                    "value_min" : 0,
                    "value_max" : 100,
                    "access" : 7,
                    "cached" : 0,
                    "cached_vld" : False
                },
                {
                    "type" : "numeric",
                    "name" : "color_temperature",
                    "label" : "Color Temperature",
                    "property" : "color_temperature",
                    "value_min" : 1200,
                    "value_max" : 6500,
                    "access" : 7,
                    "cached" : 1200,
                    "cached_vld" : False
                }
            ]
        }

        # Preliminary info
        print("Add new device - Nanoleaf")
        print("Enter a friendly name for the device")
        friendly_name = str(input("> "))
        print("Enter the IP address of the device")
        ip_addr = str(input("> "))

        # Auth token retrieval
        while True:
            print("Press and hold the power button until the LEDs start flashing, then press <enter>")
            input("")
            print("Getting auth token...")
            try:
                req_url = f"http://{ip_addr}:16021/api/v1/new"
                auth_token = requests.post(req_url).json()["auth_token"]
            except Exception:
                print("Failed, retrying")
            else:
                break

        # Device data generation
        print("Generating device info...")
        device_template["friendly_name"] = friendly_name
        device_template["metadata"]["ip_addr"] = ip_addr
        device_template["metadata"]["auth_token"] = auth_token
        return device_template


    #################################
    # Nanoleaf API Helper Functions #
    #################################

    def __nanoleaf_get(self, endpoint):
        req_url = f"http://{self.__metadata__['ip_addr']}:16021/api/v1/{self.__metadata__['auth_token']}{endpoint}"
        rsp = requests.get(req_url).json()
        return rsp
    
    def __nanoleaf_put(self, endpoint, body):
        req_url = f"http://{self.__metadata__['ip_addr']}:16021/api/v1/{self.__metadata__['auth_token']}{endpoint}"
        rsp = requests.put(req_url, json.dumps(body))#.json()
        return rsp.status_code


    #######################
    # Attribute Callbacks #
    #######################

    async def __state_set_callback(self, attr_obj, value):
        if value == self.state.value_on:
            self.__nanoleaf_put("/state", {"on":{"value":True}})
        elif value == self.state.value_off:
            self.__nanoleaf_put("/state", {"on":{"value":False}})
        elif self.state.has_value_toggle and (value == self.state.value_toggle):
            light_state = self.__nanoleaf_get("/state/on")["value"]
            self.__nanoleaf_put("/state", {"on":{"value":(not light_state)}})

    async def __state_get_callback(self, attr_obj):
        light_state = self.__nanoleaf_get("/state/on")["value"]
        if light_state: return "ON"
        else: return "OFF"
    
    async def __brightness_set_callback(self, attr_obj, value):
        if self.brightness_change_duration.get_cached_vld():
            duration = self.brightness_change_duration.get_cached()
        else:
            duration = 0
        self.__nanoleaf_put("/state", {"brightness":{"value":value, "duration":duration}})

    async def __brightness_get_callback(self, attr_obj):
        value = self.__nanoleaf_get("/state/brightness")["value"]
        return value
    
    async def __brightness_change_duration_set_callback(self, attr_obj, value):
        pass

    async def __brightness_change_duration_get_callback(self, attr_obj):
        if self.brightness_change_duration.get_cached_vld():
            return self.brightness_change_duration.get_cached()
        else:
            return None
    
    async def __hue_set_callback(self, attr_obj, value):
        self.__nanoleaf_put("/state", {"hue":{"value":value}})

    async def __hue_get_callback(self, attr_obj):
        value = self.__nanoleaf_get("/state/hue")["value"]
        return value

    async def __saturation_set_callback(self, attr_obj, value):
        self.__nanoleaf_put("/state", {"sat":{"value":value}})

    async def __saturation_get_callback(self, attr_obj):
        value = self.__nanoleaf_get("/state/sat")["value"]
        return value
    
    async def __color_temperature_set_callback(self, attr_obj, value):
        self.__nanoleaf_put("/state", {"ct":{"value":value}})

    async def __color_temperature_get_callback(self, attr_obj):
        value = self.__nanoleaf_get("/state/ct")["value"]
        return value


    ################
    # Main Methods #
    ################

    def __load_attrs__(self):
        for i in self.__attributes__: self.__add_attr__(make_attr(i))
        self.state.callback_set = self.__state_set_callback
        self.state.callback_get = self.__state_get_callback
        self.brightness.callback_set = self.__brightness_set_callback
        self.brightness.callback_get = self.__brightness_get_callback
        self.brightness_change_duration.callback_set = self.__brightness_change_duration_set_callback
        self.brightness_change_duration.callback_get = self.__brightness_change_duration_get_callback
        self.hue.callback_set = self.__hue_set_callback
        self.hue.callback_get = self.__hue_get_callback
        self.saturation.callback_set = self.__saturation_set_callback
        self.saturation.callback_get = self.__saturation_get_callback
        self.color_temperature.callback_set = self.__color_temperature_set_callback
        self.color_temperature.callback_get = self.__color_temperature_get_callback

    def __init__(self, device_data):
        super().__init__(device_data=device_data)
