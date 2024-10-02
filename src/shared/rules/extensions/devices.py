# Nikari Rule Library - Devices Extension
#
# Written by Martianmellow12

import asyncio

from ... import devices
from . import TriggerBase, ActionBase, register_trigger, register_action

from shared import nikari_logging

device_manager = devices.DeviceManager()


NAME = "Device Rules"


###################
# Trigger Classes #
###################

@register_trigger("devices", "value_seen")
class TriggerValueSeen(TriggerBase):

    INPUT_FIELDS = [
        {
            "name" : "uid",
            "type" : "number"
        },
        {
            "name" : "attr_name",
            "type" : "string"
        },
        {
            "name" : "value",
            "type" : "any"
        }
    ]

    @staticmethod
    def get_field_maps():
        device_uid_map = dict()
        for i in device_manager.get_devices():
            device_uid_map[i.uid] = i.friendly_name

        maps = {
            "uid" : device_uid_map
        }
        return maps

    def __init__(self, fields):
        super().__init__(fields)

    def check(self, obj):
        if not self.__check_field__(obj, "event_type", "value_seen"): return False
        if not self.__check_input_field__(obj, "uid"): return False
        if not self.__check_input_field__(obj, "attr_name"): return False
        if not self.__check_input_field__(obj, "value"):
            if self.fields["uid"] == 7 and self.fields["attr_name"] == "contact":
                print(f"{type(self.fields['value'])} / {type(obj['value'])}")
                print("BEANS")
            return False
        return True
    
@register_trigger("devices", "value_change")
class TriggerValueChange(TriggerBase):

    INPUT_FIELDS = [
        {
            "name" : "uid",
            "type" : "number"
        },
        {
            "name" : "attr_name",
            "type" : "string"
        },
        {
            "name" : "value_old",
            "type" : "string"
        },
        {
            "name" : "value_new",
            "type" : "string"
        }
    ]
    
    def __init__(self, fields):
        super().__init__(fields)

    def check(self, obj):
        if not self.__check_field__(obj, "event_type", "value_change"): return False
        if not self.__check_input_field__(obj, "uid"): return False
        if not self.__check_input_field__(obj, "attr_name"): return False
        if not self.__check_input_field__(obj, "value_old"): return False
        if not self.__check_input_field__(obj, "value_new"): return False
        return True


##################
# Action Classes #
##################

@register_action("devices", "set")
class ActionSet(ActionBase):

    INPUT_FIELDS = [
        {
            "name" : "uid",
            "type" : "number"
        },
        {
            "name" : "attr_name",
            "type" : "string"
        },
        {
            "name" : "value",
            "type" : "string"
        }
    ]

    def __init__(self, fields):
        super().__init__(fields)

    async def fire(self):
        nikari_logging.log(NAME, f"Setting device UID={self.field['uid']} {self.fields['attr_name']} to {self.fields['value']}")
        device = device_manager.get_device_by_uid(self.fields["uid"])
        target_attr = getattr(device, self.fields["attr_name"])
        await target_attr.set(self.fields["value"])

@register_action("devices", "set_for_duration")
class ActionSetForDuration(ActionBase):

    INPUT_FIELDS = [
        {
            "name" : "uid",
            "type" : "number"
        },
        {
            "name" : "attr_name",
            "type" : "string"
        },
        {
            "name" : "value",
            "type" : "any"
        },
        {
            "name" : "duration",
            "type" : "number"
        }
    ]

    def __init__(self, fields):
        super().__init__(fields)
        self.retrigger = False

    async def fire(self):
        nikari_logging.log(NAME, f"Setting device UID={self.fields['uid']} {self.fields['attr_name']} to {self.fields['value']} for {self.fields['duration']} seconds")
        if not await self.__get_lock__():
            self.retrigger = True
            return
        device = device_manager.get_device_by_uid(self.fields["uid"])
        target_attr = getattr(device, self.fields["attr_name"])
        old_value = await target_attr.get()

        if self.fields["value"] == old_value:
            await self.__release_lock__()
            return

        await target_attr.set(self.fields["value"])
        time_remaining = self.fields["duration"]
        while time_remaining > 0:
            time_remaining -= 1
            await asyncio.sleep(1)
            if self.retrigger:
                self.retrigger = False
                time_remaining = self.fields["duration"]
        nikari_logging.log(NAME, f"Returning device UID={self.fields['uid']} {self.fields['attr_name']} to {old_value}")
        await target_attr.set(old_value)
        await self.__release_lock__()
