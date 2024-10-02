# Huginn - Light Control Module
#
# Written by Martianmellow12

# General
import sys

# Support
sys.path.append("..")
from shared.nikari_logging import log

from corelib import coredb

# Light Control Extensions
#from . import nanoleaf

# Global variables
NAME = "Nikari Core / Light Control"
EXTENSIONS = {
    #"nanoleaf" : nanoleaf
}
COREDB = coredb.CoreDB()


###########################
# Light Control Functions #
###########################

def set_state(light_list, state):
    for light in light_list:
        # TODO(martianmellow12): Implement this
        pass
        #EXTENSIONS[light["type"]].set_state(light, state)
    log(NAME, f"Turned {len(light_list)} light(s) '{'on' if state else 'off'}'")

def get_state(light_list):
    for light in light_list:
        light["state"] = True
        # TODO(martianmellow12): Implement this
        #EXTENSIONS[light["type"]].set_state(light, state)
    log(NAME, f"Read state for {len(light_list)} light(s)")
    return light_list


######################
# Command Processing #
######################

async def process_command(command_obj):
    if command_obj["type"] != "light_control":
        log(NAME, f"Erroneously received command with type '{command_obj['type']}' > {command_obj}")
        return None
    
    if command_obj["command"] == "add_light":
        result = await COREDB.add_light(command_obj["light_type"],
                                        command_obj["room"],
                                        command_obj["ip_addr"],
                                        command_obj["port"],
                                        command_obj["meta"])
        return {"success" : result}
    
    if command_obj["command"] == "remove_light":
        result =  await COREDB.remove_light(command_obj["light_id"])
        return {"success" : result}
    
    if command_obj["command"] == "get_lights":
        room = None
        light_type = None
        light_id = None
        if "room" in command_obj.keys(): room = command_obj["room"]
        if "light_type" in command_obj.keys(): light_type = command_obj["light_type"]
        if "light_id" in command_obj.keys(): light_id = command_obj["light_id"]
        results = await COREDB.get_lights(light_id, light_type, room)
        return {"lights" : results}

    if command_obj["command"] == "set_state":
        light_id = None
        light_type = None
        room = None
        if "light_id" in command_obj.keys(): light_id = command_obj["light_id"]
        if "light_type" in command_obj.keys(): light_type = command_obj["light_type"]
        if "room" in command_obj.keys(): room = command_obj["room"]

        lights = await COREDB.get_lights(light_id, light_type, room)
        set_state(lights, command_obj["state"])
        return {"result" : True}
    
    if command_obj["command"] == "get_state":
        light_id = None
        light_type = None
        room = None
        if "id" in command_obj.keys(): light_id = command_obj["light_id"]
        if "light_type" in command_obj.keys(): light_type = command_obj["light_type"]
        if "room" in command_obj.keys(): room = command_obj["room"]

        lights = await COREDB.get_lights(light_id, light_type, room)
        results = get_state(lights)
        return {"lights" : results}
    
    if command_obj["command"] == "toggle_state":
        light_id = None
        light_type = None
        room = None
        if "id" in command_obj.keys(): light_id = command_obj["light_id"]
        if "light_type" in command_obj.keys(): light_type = command_obj["light_type"]
        if "room" in command_obj.keys(): room = command_obj["room"]
        lights = await COREDB.get_lights(light_id, light_type, room)

        states = get_state(lights)
        if command_obj["force"] == True:
            if not all(i["state"] == True for i in states):
                set_state(lights, True)
            else:
                set_state(lights, False)
        else:
            if not all(i["state"] == False for i in states):
                set_state(lights, False)
            else:
                set_state(lights, True)

        return {"result" : True}

    log(NAME, f"Received unrecognized command '{command_obj['command']}'")
    return None
