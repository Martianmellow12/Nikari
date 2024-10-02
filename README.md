# Nikari
 An expandable home assistant designed to run on a Raspberry Pi. The goal is to create a system where, from the core's perspective, all actions appear identical (ex. interfacing with a Zigbee button is no different than interfacing with a Nanoleaf light is no different from interfacing with a calendar). This is done to a) make adding expansions as easy as dragging-and-dropping a folder to the right place with no additional configuration, and b) to facilitate creating a powerful GUI that can chain devices and their attributes together into rules.

 Current features include:
 - Support for Nanoleaf lights
 - Support for Zigbee devices (requires additional hardware)
 - Support for trigger/action rules (ex. using a zigbee sensor to turn on a light for 5 minutes)

To be implemented:
- Support for voice control using PicoVoice
- A GUI for adding/removing devices and rules
- Misc. actions (push notifications, timers, etc.)
