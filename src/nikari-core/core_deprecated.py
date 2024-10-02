# Nikari - Core
#
# Written by Martianmellow12

# General
import asyncio
import sys

# Shared
sys.path.append("..")
from shared.nikari_logging import log
from shared import comm

# Extensions
from corelib import admin
from corelib import light_control
from corelib import devices

# Config DB
from corelib import coredb

# Global variables
NAME = "Nikari Core"


######################
# Command Processing #
######################

async def command_callback(command, addr):
    print("AAAA")
    try:
        log(NAME, f"Command received from {addr} > {command}")
        if command["type"] == "light_control":
            result = await light_control.process_command(command)
            if result == None:
                return {"error" : "command_failed"}
            return result
        if command["type"] == "admin":
            result = await admin.process_command(command)
            if result == None:
                return {"error" : "command_failed"}
            return result
        print("DSFDSG")
        return {"error" : "command_unknown"}
    except Exception as e:
        print(e)


#################
# Core Mainloop #
#################

mainloop = asyncio.new_event_loop()

# CoreDB setup
COREDB = coredb.CoreDB()
asyncio.run(COREDB.db_init())
log(NAME ,"Initialized config DB")

# Servers
server = comm.Server()
server.set_callback(command_callback)
mainloop.create_task(server.server_task())
mainloop.create_task(server.discovery_task())
device_manager = devices.DeviceManager()
device_manager.start()

log(NAME, "Starting the command and discovery servers")
log(NAME, f"Command server started at {server.ip_addr}:{server.port}", timestamp=False, indent_level=1)
log(NAME, f"Discovery server started at {server.ip_addr}:{server.discovery_port}", timestamp=False, indent_level=1)

try:
    mainloop.run_forever()
except Exception:
    print("Exiting...")
device_manager.stop()