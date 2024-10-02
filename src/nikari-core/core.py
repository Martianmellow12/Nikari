# Nikari Core
#
# Written by Martianmellow12

# General
import asyncio
import sys

# Corelib
from corelib import coredb
import corelib.tasks

# Shared
sys.path.append("..")
from shared import nikari_logging
from shared import devices
from shared import rules
#from shared import voice_cmd


####################
# Global Variables #
####################

NAME = "Nikari Core"
COREDB = None
DEVICE_MANAGER = None
RULE_MANAGER = None
VC_SERVER = None


#################
# Core Mainloop #
#################

async def mainloop_task(loop):

    # CoreDB setup
    nikari_logging.log(NAME, "Initializing CoreDB")
    COREDB = coredb.CoreDB()
    await COREDB.db_init()

    # Device manager
    nikari_logging.log(NAME, "Initializing device manager")
    DEVICE_MANAGER = devices.DeviceManager()
    await COREDB.ext.devices.reload_devices(DEVICE_MANAGER)

    # Rule manager
    nikari_logging.log(NAME, "Initializing rule manager")
    RULE_MANAGER = rules.RuleManager()
    RULE_MANAGER.set_coredb(COREDB)
    await COREDB.ext.rules.reload(RULE_MANAGER)
    corelib.tasks.rules.set_rule_manager(RULE_MANAGER)
    corelib.tasks.rules.add_event_queue(DEVICE_MANAGER.event_manager.get_event_queue())
    loop.create_task(corelib.tasks.rules.rule_manager_task())

    # Voice commands
    '''
    nikari_logging.log(NAME, "Initializing voice command server")
    VC_SERVER = voice_cmd.VoiceCmdServer()
    loop.create_task(VC_SERVER.voice_server_task())
    '''

    while True:
        nikari_logging.log(NAME, "Tick")
        await asyncio.sleep(300)

mainloop = asyncio.new_event_loop()
mainloop.run_until_complete(mainloop_task(mainloop))