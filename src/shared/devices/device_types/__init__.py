# Nikari Device Control Library - Base Types
#
# Written by Martianmellow12

import json
import os

###########################
# Device Type Definitions #
###########################

device_type_path = os.path.dirname(__file__)
__all__ = [i[:-3] for i in os.listdir(device_type_path) if (i[-3:] == ".py") and (i != "__init__.py")]


####################
# Global Variables #
####################

DEVICE_FACTORY_REGISTRY = dict()


##############
# Exceptions #
##############

class AttrAccessError(Exception): pass
class AttrAssignmentError(Exception): pass
class AttrCreationError(Exception): pass
class UndefinedMethodError(Exception): pass
class UnknownDeviceError(Exception): pass


###########################
# Registration Decorators #
###########################

def register_type(type_name):
    def impl(cls):
        DEVICE_FACTORY_REGISTRY[type_name] = cls
        return cls
    return impl


#############################
# Registry Access Functions #
#############################

async def add_new_device(device_type):
    if device_type in DEVICE_FACTORY_REGISTRY.keys():
        return await DEVICE_FACTORY_REGISTRY[device_type].add_new_device()
    else:
        raise UnknownDeviceError(f"Unknown device type '{device_type}'")


###################
# Attribute Types #
###################

def make_attr(attr_data):
    if attr_data["type"] == "binary": return __AttrBinary__(attr_data)
    if attr_data["type"] == "numeric": return __AttrNumeric__(attr_data)
    if attr_data["type"] == "enum": return __AttrEnum__(attr_data)
    raise AttrCreationError(f"Attribute factory can't make attr of unknown type '{attr_data['type']}'")

class __AttrBase__:

    def __valid__(self, value):
        raise UndefinedMethodError("All children must define __valid__")
    
    def __init__(self, attr_data):
        self.__device_uid__ = None
        self.__event_manager__ = None

        # Cached value management
        self.type = "base"
        self.name = attr_data["name"]
        self.cached = attr_data["cached"]
        self.cached_vld = attr_data["cached_vld"]

    def set_cached(self, value):
        if self.__valid__(value):
            event_set = {
                "event_type" : "value_seen",
                "uid" : self.__device_uid__,
                "attr_name" : self.name,
                "value" : value
            }
            self.__event_manager__.add_event(event_set)
            if self.cached != value:
                event_change = {
                    "event_type" : "value_change",
                    "uid" : self.__device_uid__,
                    "attr_name" : self.name,
                    "value_old" : self.cached,
                    "value_new" : value
                }
                self.__event_manager__.add_event(event_change)
            self.cached = value
            self.cached_vld = True
        else:
            raise ValueError(f"'{value}' is not valid for {self.type} attribute '{self.name}'")

    def get_cached(self):
        if self.cached_vld: return self.cached
        else: raise AttrAccessError("The cached value isn't valid for this attribute")

    def get_cached_vld(self):
        # Intentionally hiding the value of cached_vld
        if self.cached_vld: return True
        else: return False


    ##############################
    # Externally Defined Methods #
    ##############################

    async def callback_get(self):
        raise UndefinedMethodError("The 'get' callback hasn't been defined for this attribute")
    
    async def callback_set(self, value):
        raise UndefinedMethodError("The 'set' callback hasn't been defined for this attribute")

class __AttrBinary__(__AttrBase__):

    def __valid__(self, value):
        valid_values = [self.value_on, self.value_off]
        if self.has_value_toggle: valid_values.append(self.value_toggle)
        return value in valid_values
    
    def __init__(self, attr_data):
        super().__init__(attr_data=attr_data)

        # Validation
        if attr_data["type"] != "binary":
            raise AttrCreationError(f"Attempted to create a binary attribute from json with type '{attr_data['type']}'")

        # Required values
        self.type = attr_data["type"]
        self.label = attr_data["label"]
        self.property = attr_data["property"]
        self.value_on = attr_data["value_on"]
        self.value_off = attr_data["value_off"]
        self.access = attr_data["access"]

        # Optional values
        if "value_toggle" in attr_data.keys():
            self.has_value_toggle = True
            self.value_toggle = attr_data["value_toggle"]
        else:
            self.has_value_toggle = False

        # Internal variables
        self.__valid_values__ = [self.value_on, self.value_off]
        if self.has_value_toggle: self.__valid_values__.append(self.value_toggle)

    async def get(self):
        # TODO(martianmellow12): Allow devices to define their own 'get' behaviors
        #if not (self.access & 4): raise AttrAccessError("Cannot 'get' attribute with access bit 2 set to 0")
        result = await self.callback_get(self)
        self.set_cached(result)
        return result
    
    async def set(self, value):
        if not (self.access & 2): raise AttrAccessError("Cannot 'set' attribute with access bit 1 set to 0")
        if not value in self.__valid_values__: raise ValueError(f"'{value}' is not valid for this attribute; valid values are {', '.join(self.__valid_values__)}")
        result = await self.callback_set(self, value)
        self.set_cached(value)
        return result
    
class __AttrNumeric__(__AttrBase__):

    def __valid__(self, value):
        if not str(value).replace(".", "", 1).isnumeric(): return False
        if self.has_value_max and (value > self.value_max): return False
        if self.has_value_min and (value < self.value_min): return False
        return True

    def __value_is_valid__(self, value):
        if self.has_value_max and (value > self.value_max): return False
        if self.has_value_min and (value < self.value_min): return False
        return True

    def __init__(self, attr_data):
        super().__init__(attr_data=attr_data)

        # Validation
        if attr_data["type"] != "numeric":
            raise AttrCreationError(f"Attempted to create a numeric attribute from json with type '{attr_data['type']}'")
        
        # Required values
        self.type = attr_data["type"]
        self.label = attr_data["label"]
        self.property = attr_data["property"]
        self.access = attr_data["access"]

        # Optional values
        self.has_value_max = "value_max" in attr_data.keys()
        if self.has_value_max: self.value_max = attr_data["value_max"]
        
        self.has_value_min = "value_min" in attr_data.keys()
        if self.has_value_min: self.value_min = attr_data["value_min"]

        self.has_value_step = "value_step" in attr_data.keys()
        if self.has_value_step: self.value_step = attr_data["value_step"]

        self.has_unit = "unit" in attr_data.keys()
        if self.has_unit: self.unit = attr_data["unit"]

        self.has_presets = "presets" in attr_data.keys()
        if self.has_presets: self.presets = attr_data["presets"]

    async def get(self):
        if not (self.access & 4): raise AttrAccessError("Cannot 'get' attribute with access bit 2 set to 0")
        result = await self.callback_get(self)
        self.set_cached(result)
        return result
    
    async def set(self, value):
        if not (self.access & 2): raise AttrAccessError("Cannot 'set' attribute with access bit 1 set to 0")
        result = await self.callback_set(self, value)
        self.set_cached(value)
        return result
    
class __AttrEnum__(__AttrBase__):

    def __valid__(self, value):
        return value in self.values

    def __init__(self, attr_data):
        super().__init__(attr_data=attr_data)

        # Validation
        if attr_data["type"] != "enum":
            raise AttrCreationError(f"Attempted to create an enum attribute from json with type '{attr_data['type']}'")
        
        # Required values
        self.type = attr_data["type"]
        self.label = attr_data["label"]
        self.property = attr_data["property"]
        self.access = attr_data["access"]
        self.values = attr_data["values"]

    async def get(self):
        if not (self.access & 4): raise AttrAccessError("Cannot 'get' attribute with access bit 4 set to 0")
        result = await self.callback_get(self)
        self.set_cached(result)
        return result
    
    async def set(self, value):
        if not (self.access & 2): raise AttrAccessError("Cannot 'get' attribute with access bit 2 set to 0")
        result = await self.callback_set(self, value)
        self.set_cached(value)
        return result
    

#####################
# Device Base Class #
#####################

class DeviceBase:

    ###################
    # Virtual Methods #
    ###################

    @staticmethod
    def add_new_device():
        raise UndefinedMethodError("Children must define the add_new_device method")

    def __load_attrs__(self):
        raise UndefinedMethodError("Children must define the __load_attrs__ method")


    ####################
    # Internal Methods #
    ####################

    def __serialize__(self):
        serialized_device = {
            "uid" : self.uid,
            "type" : self.type,
            "metadata" : self.__metadata__,
            "attributes" : list()
        }
        for i in self.__attr_registry__:
            serialized_device["attributes"].append(getattr(self, i).__serialize__())
        return serialized_device

    def __add_attr__(self, attr_obj):
        name = attr_obj.name
        if name in self.__attr_registry__:
            raise AttrAssignmentError(f"Object already has an attribute named '{name}'")
        attr_obj.__event_manager__ = self.__event_manager__
        self.__attr_registry__.append(name)
        setattr(self, name, attr_obj)


    ################
    # User Methods #
    ################

    def __init__(self, device_data):
        self.uid = device_data["uid"]
        self.friendly_name = device_data["friendly_name"]
        self.type = device_data["type"]
        self.__metadata__ = device_data["metadata"]
        self.__attributes__ = device_data["attributes"]

        self.__attr_registry__ = list()
        self.__event_manager__ = None
        self.__kill__ = False

        self.__load_attrs__()

    def set_event_manager(self, event_manager):
        self.__event_manager__ = event_manager
        for i in self.__attr_registry__:
            attr = getattr(self, i)
            attr.__event_manager__ = event_manager

    def set_attr_device_uids(self):
        for i in self.__attr_registry__:
            attr = getattr(self, i)
            attr.__device_uid__ = self.uid

    async def task(self):
        # Implemented by children if needed
        pass

    async def kill(self):
        self.__kill__ = True
