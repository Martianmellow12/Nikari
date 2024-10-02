# Nikari Device Control Library
#
# Written by Martianmellow12

# General
import json

# Internal
from .device_types import *

from shared import nikari_logging


####################
# Global Variables #
####################

NAME = "Devices Module"
DEVICE_REGISTRY = dict()


##############
# Exceptions #
##############

class UnknownDeviceError(Exception): pass


#################
# Event Manager #
#################

class EventManager:

    EVENT_QUEUES = list()

    def add_event(self, event_data):
        nikari_logging.log(NAME, f"LOGGING EVENT: {event_data}", debug=True)
        for i in EventManager.EVENT_QUEUES:
            i.append(event_data)

    def get_event_queue(self):
        new_queue = list()
        EventManager.EVENT_QUEUES.append(new_queue)
        return new_queue


##################
# Device Manager #
##################

class DeviceManager:

    event_manager = EventManager()

    def add_new_device(self, device_type):
        if device_type not in device_types.DEVICE_FACTORY_REGISTRY.keys():
            raise UnknownDeviceError(f"Unknown device type '{device_type}'")
        else:
            return device_types.DEVICE_FACTORY_REGISTRY[device_type].add_new_device()
    
    def add_device(self, device_data, force=False):
        global DEVICE_REGISTRY

        if device_data["type"] not in device_types.DEVICE_FACTORY_REGISTRY.keys():
            raise UnknownDeviceError(f"Device has unrecognized type '{device_data['type']}'")
        if (device_data["uid"] in DEVICE_REGISTRY.keys()) and (force == False):
            return DEVICE_REGISTRY[device_data["uid"]]
        else:
            if device_data["uid"] in DEVICE_REGISTRY.keys():
                self.delete_devices(device_data["uid"])
            new_device = device_types.DEVICE_FACTORY_REGISTRY[device_data["type"]](device_data)
            new_device.set_event_manager(DeviceManager.event_manager)
            new_device.set_attr_device_uids()
            DEVICE_REGISTRY[new_device.uid] = new_device
            return new_device
        
    def get_devices(self):
        return [DEVICE_REGISTRY[i] for i in DEVICE_REGISTRY.keys()]
        
    def get_device_by_uid(self, uid):
        if not uid in DEVICE_REGISTRY.keys(): return None
        else: return DEVICE_REGISTRY[uid]

    def delete_devices(self, uid=None):
        if uid:
            device = DEVICE_REGISTRY.pop(uid)
            device.kill()
        else:
            for i in DEVICE_REGISTRY.keys():
                device = DEVICE_REGISTRY.pop(i)
                device.kill()
