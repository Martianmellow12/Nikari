# Nikari Rule Library - Base Types
#
# Written by Martianmellow12

import asyncio
import os


#########################
# Rule Type Definitions #
#########################

extensions_path = os.path.dirname(__file__)
__all__ = [i[:-3] for i in os.listdir(extensions_path) if (i[-3:] == ".py") and (i != "__init__.py")]


####################
# Global Variables #
####################

RULE_MANAGER = None
RULE_TRIGGER_REGISTRY = dict()
RULE_CONDITION_REGISTRY = dict()
RULE_ACTION_REGISTRY = dict()


##############
# Exceptions #
##############

class UndefinedMethodError(Exception): pass
class MissingFieldError(Exception): pass
class FieldTypeMismatchError(Exception): pass


###########################
# Registration Decorators #
###########################

def register_trigger(trigger_type, trigger_subtype):
    def impl(cls):
        if trigger_type not in RULE_TRIGGER_REGISTRY.keys():
            RULE_TRIGGER_REGISTRY[trigger_type] = dict()
        RULE_TRIGGER_REGISTRY[trigger_type][trigger_subtype] = cls
        setattr(cls, "__rule_manager__", RULE_MANAGER)
        setattr(cls, "__trigger_type__", trigger_type)
        setattr(cls, "__trigger_subtype__", trigger_subtype)
        return cls
    return impl

def register_action(action_type, action_subtype):
    def impl(cls):
        if action_type not in RULE_ACTION_REGISTRY.keys():
            RULE_ACTION_REGISTRY[action_type] = dict()
        RULE_ACTION_REGISTRY[action_type][action_subtype] = cls
        setattr(cls, "__rule_manager__", RULE_MANAGER)
        return cls
    return impl


######################
# Trigger Base Class #
######################

class TriggerBase:

    INPUT_FIELDS = []

    @staticmethod
    def get_field_maps():
        return dict()

    def __check_field__(self, obj, field, value):
        if field not in obj.keys(): return False
        if obj[field] != value: return False
        return True
    
    def __check_input_field__(self, obj, field):
        if field not in obj.keys(): return False
        if obj[field] != self.fields[field]: return False
        return True

    def __init__(self, fields):
        for i in self.INPUT_FIELDS:
            if i["name"] not in fields.keys():
                raise MissingFieldError(f"Missing field '{i['name']}' is required")
            if (i["type"] == "number") and (type(fields[i["name"]]) not in [int, float]):
                raise FieldTypeMismatchError(f"Field '{i['name']}' should be type '{i['type']}' (got type '{type(fields[i['name']])}')")
            if i["type"] == "string":
                fields[i["name"]] = str(fields[i["name"]])
        self.fields = fields

    def serialize(self):
        serial_dict = {
            "type" : self.__class__.__trigger_type__,
            "subtype" : self.__class__.__trigger_subtype__,
            "fields" : self.fields
        }
        return serial_dict

    def check(self, obj):
        raise UndefinedMethodError("Method 'check' must be defined by children")
    
class ActionBase:

    INPUT_FIELDS = []
    RUN_LOCK = False

    @staticmethod
    def get_field_maps():
        return dict()

    def __check_field__(self, obj, field, value):
        if field not in obj.keys(): return False
        if obj[field] != value: return False
        return True
    
    def __check_input_field__(self, obj, field):
        if field not in obj.keys(): return False
        if obj[field] != self.fields[field]: return False
        return True
    
    async def __get_lock__(self):
        if not self.RUN_LOCK:
            self.RUN_LOCK = True
            return True
        else:
            return False
    
    async def __release_lock__(self):
        self.RUN_LOCK = False
    
    async def __wait_for_lock__(self):
        while self.RUN_LOCK:
            await asyncio.sleep(0.5)
        self.RUN_LOCK = True

    def __init__(self, fields):
        for i in self.INPUT_FIELDS:
            if i["name"] not in fields.keys():
                raise MissingFieldError(f"Missing field '{i['name']}' is required")
            if (i["type"] == "number") and (type(fields[i["name"]]) not in [int, float]):
                raise FieldTypeMismatchError(f"Field '{i['name']}' should be type '{i['type']}' (got type '{type(fields[i['name']])}')")
            if i["type"] == "string":
                fields[i["name"]] = str(fields[i["name"]])
        self.fields = fields

    def serialize(self):
        serial_dict = {
            "type" : self.__class__.__trigger_type__,
            "subtype" : self.__class__.__trigger_subtype__,
            "fields" : self.fields
        }
        return serial_dict

    def fire(self):
        raise UndefinedMethodError("Method 'check' must be defined by children")