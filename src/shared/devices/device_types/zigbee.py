# Nikari Device Control Library - Zigbee Extension
#
# Written by Martianmellow12

# General
import aiomqtt
import asyncio
import json
import paho.mqtt.client as mqtt

# Local
from . import DeviceBase, make_attr, register_type, AttrAccessError


#################
# Zigbee Device #
#################

@register_type("zigbee")
class DeviceZigbee(DeviceBase):

    ##################
    # Static Methods #
    ##################

    @staticmethod
    async def add_new_device():      
        print("Add new device - Zigbee")
        print("Enter the MQTT server info")
        mqtt_ip = str(input("IP Address > "))
        mqtt_port = int(input("Port (usually 1883) > "))
        print("Enter a friendly name for the device")
        friendly_name = str(input("> "))
        device_addr = None
        device_data = None

        # Connect the client
        async with aiomqtt.Client(mqtt_ip, mqtt_port) as client:
            async with client.messages() as messages:
                await client.publish("zigbee2mqtt/bridge/request/permit_join", "true")
                await client.subscribe("zigbee2mqtt/bridge/event")
                async for message in messages:
                    payload = json.loads(message.payload.decode())
                    if (payload["type"] == "device_joined"):
                        device_addr = payload["data"]["ieee_address"]
                        print(f"Joining device with address {device_addr}")
                    if (payload["type"] == "device_interview") and (payload["data"]["status"] == "successful") and (payload["data"]["ieee_address"] == device_addr):
                        print(f"Got device data for {friendly_name}")
                        device_data = payload["data"]
                        break
                await client.publish("zigbee2mqtt/bridge/request/permit_join", "false")

        print("Generating device info...")
        device = dict()
        device["type"] = "zigbee"
        device["friendly_name"] = friendly_name
        device["metadata"] = {
            "mqtt_ip" : mqtt_ip,
            "mqtt_port" : mqtt_port,
            "ieee_addr" : device_addr
        }
        device["attributes"] = DeviceZigbee.__exposes_to_attrs__(device_data["definition"]["exposes"])
        return device

    @staticmethod
    def __exposes_to_attrs__(device_data):
        attrs = list()
        for i in device_data:
            if i["type"] in ["binary", "numeric", "enum"]:
                i["cached"] = None
                i["cached_vld"] = False
                attrs.append(i)
            if i["type"] == "switch":
                attrs += DeviceZigbee.__exposes_to_attrs__(i["features"])
        return attrs


    ####################
    # Helper Functions #
    ####################

    def __get_topic(self):
        return f"zigbee2mqtt/{self.__metadata__['ieee_addr']}"


    #######################
    # Attribute Callbacks #
    #######################

    async def __zigbee_set(self, attr_obj, value):
        async with aiomqtt.Client(self.__metadata__["mqtt_ip"], self.__metadata__["mqtt_port"]) as client:
            await client.publish(f"{self.__get_topic()}/set/{attr_obj.property}", payload=value)

    async def __zigbee_get(self, attr_obj):
        if attr_obj.access & 4:
            async with aiomqtt.Client(self.__metadata__["mqtt_ip"], self.__metadata__["mqtt_port"]) as client:
                await client.publish(f"{self.__get_topic()}/get/{attr_obj.property}")
            while not attr_obj.get_cached_vld():
                # TODO(martianmellow12): Implement stall prevention
                await asyncio.sleep(0.1)
        if not attr_obj.get_cached_vld():
            raise AttrAccessError(f"Zigbee: Couldn't get cached value for {attr_obj.property}")
        return attr_obj.get_cached()


    ################
    # Main Methods #
    ################

    def __load_attrs__(self):
        for i in self.__attributes__: self.__add_attr__(make_attr(i))
        for i in self.__attr_registry__:
            attr = getattr(self, i)
            attr.callback_set = self.__zigbee_set
            attr.callback_get = self.__zigbee_get

    def __init__(self, device_data):
        super().__init__(device_data=device_data)
        asyncio.get_event_loop().create_task(self.task())

    async def task(self):
        while not self.__kill__:
            async with aiomqtt.Client(self.__metadata__["mqtt_ip"], self.__metadata__["mqtt_port"]) as client:
                async with client.messages() as messages:
                    await client.subscribe(self.__get_topic())
                    async for message in messages:
                        payload = json.loads(message.payload.decode())
                        for i in self.__attr_registry__:
                            if i in payload.keys():
                                attr = getattr(self, i)
                                attr.set_cached(payload[i])
