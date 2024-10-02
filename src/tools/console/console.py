# Nikari - Console
#
# Written by Martianmellow12

import asyncio
import os
import sys

import consolelib

##########################
# Main Console Interface #
##########################

async def console():
    while True:
        # Parsing
        cmd_raw = str(input("> "))
        cmd_list = cmd_raw.split(" ")
        if cmd_list[0] != "":
            cmd = cmd_list[0]
        else:
            continue
        if len(cmd_list) > 1:
            cmd_args = cmd_list[1:]
        else:
            cmd_args = list()

        # Command processing
        if cmd in ["q", "quit", "exit"]:
            break

        if cmd == "device":
            await consolelib.device.console()

mainloop = asyncio.new_event_loop()
mainloop.run_until_complete(console())