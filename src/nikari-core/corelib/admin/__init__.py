# Nikari - Admin Command Processing
#
# Written by Martianmellow12

# General
import sys

# Shared
sys.path.append("..")
from shared.nikari_logging import log

# Nikari
from corelib import coredb

# Global variables
NAME = "Nikari Core / Admin"
COREDB = coredb.CoreDB()


######################
# Command Processing #
######################

async def process_command(command_obj):
    if command_obj["type"] != "admin":
        log(NAME, f"Erroneously received command with type '{command_obj['type']}' > {command_obj}")
        return None
    
    if command_obj["command"] == "kill_core":
        quit()
    
    log(NAME, f"Received unrecognized command '{command_obj['command']}'")
    return None
