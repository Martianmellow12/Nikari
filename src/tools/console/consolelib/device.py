# Nikari - Device Console
#
# Written by Martianmellow12

import asyncio
import os
import sys

sys.path.append(os.path.join("..", ".."))
sys.path.append(os.path.join("..", "..", "nikari-core"))

from corelib import coredb
from shared import devices


####################
# Helper Functions #
####################

def print_attrs(device):
    for i in device.__attr_registry__:
        info_str = str()
        attr = getattr(device, i)

        if attr.type == "binary":
            info_str += f"[binary] {attr.name} -> {attr.value_on} / {attr.value_off}"
            if attr.has_value_toggle: info_str += f" / {attr.value_toggle}"

        elif attr.type == "numeric":
            info_str += f"[numeric] {attr.name}"
            if attr.has_unit: info_str += f" ({attr.unit})"
            if attr.has_value_min or attr.has_value_max:
                info_str += " -> "
                if attr.has_value_min: info_str += f"min={attr.value_min}   "
                if attr.has_value_max: info_str += f"min={attr.value_max}   "

        elif attr.type == "enum":
            info_str += f"[enum] {attr.name} -> {attr.values}"

        else:
            info_str += f"[unknown] {attr.name}"

        print(info_str)


################
# Main Console #
################

async def console():
    device_manager = devices.DeviceManager()
    database = coredb.CoreDB()

    print("Loading devices...")
    await database.db_init()
    for i in await database.ext.devices.get_devices():
        device_manager.add_device(i)

    selected_device = None

    while True:
        # Parsing
        if selected_device: prompt = f"{selected_device.uid} - {selected_device.friendly_name}"
        else: prompt = "None"
        cmd_raw = str(input(f"[{prompt}] > "))
        cmd_list = cmd_raw.split(" ")
        if cmd_list[0] != "":
            cmd = cmd_list[0]
        else:
            continue
        if len(cmd_list) > 1:
            cmd_args = cmd_list[1:]
        else:
            cmd_args = list()

        # Allow async events to be processed before proceeding
        await asyncio.sleep(0.1)

        # Command processing
        if cmd in ["q", "quit", "exit"]:
            break

        if cmd in ["ls", "list"]:
            if not cmd_args:
                cmd_args.append("devices")
            if cmd_args[0] == "devices":
                for i in device_manager.get_devices():
                    print(f"[{i.uid}] ({i.type}) {i.friendly_name}")
            if cmd_args[0] == "attrs":
                if not selected_device:
                    print("ERROR: no device selected")
                    continue
                else:
                    print_attrs(selected_device)
            continue

        if cmd in ["select", "sel"]:
            if not cmd_args:
                print("ERROR: expected a device UID as an argument")
                continue
            if not cmd_args[0].isnumeric():
                print("ERROR: UID must be a number")
                continue
            selected_device = device_manager.get_device_by_uid(int(cmd_args[0]))
            if not selected_device:
                print("ERROR: invalid UID")
                continue

        if cmd == "set":
            if len(cmd_args) < 2:
                print("ERROR: no attribute or value provided")
                continue
            if cmd_args[0] not in selected_device.__attr_registry__:
                print(f"ERROR: device has no attribute '{cmd_args[0]}'")
                continue
            attr = getattr(selected_device, cmd_args[0])
            if attr.type == "numeric": cmd_args[1] = int(cmd_args[1])
            await attr.set(cmd_args[1])

        if cmd == "get":
            if len(cmd_args) < 1:
                print("ERROR: no attribute provided")
                continue
            if cmd_args[0] not in selected_device.__attr_registry__:
                print(f"ERROR: device has no attribute '{cmd_args[0]}'")
                continue
            attr = getattr(selected_device, cmd_args[0])
            try:
                value = await attr.get()
                print(f"{cmd_args[0]} -> {value}")
            except Exception as e:
                print(f"Failed to get value: {e}")

        if cmd == "add":
            if len(cmd_args) < 1:
                print("ERROR: no device type provided")
                continue
            try: device_data = await devices.device_types.add_new_device(cmd_args[0])
            except devices.device_types.UnknownDeviceError:
                print(f"Unknown device type '{cmd_args[0]}'")
                continue
            print("Saving to database...")
            await database.ext.devices.add_device(device_data["type"], device_data["friendly_name"], device_data["metadata"], device_data["attributes"])
            print("")

        if cmd == "rm":
            if not selected_device:
                print("ERROR: No device selected")
                continue
            await database.ext.devices.delete_device(selected_device.uid)
            print(f"Deleted device with UID {selected_device.uid}")
