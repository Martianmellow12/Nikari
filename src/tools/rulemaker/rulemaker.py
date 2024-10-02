# Nikari - Rule Maker GUI
#
# Written by Martianmellow12

import asyncio
import os
import sys
from tkinter import *

sys.path.append(os.path.join("..", ".."))
sys.path.append(os.path.join("..", "..", "nikari-core"))

# Nikari imports
from shared import devices
from shared import rules
from corelib import coredb


####################
# Global Functions #
####################

STATE_REGISTRY = {
    "canvas" : None,
    "active_element" : 0,
    "elements" : dict()
}

def on_lclick(event):
    global STATE_REGISTRY

    active_elements = STATE_REGISTRY["canvas"].find_withtag(CURRENT)
    if len(active_elements) == 0:
        STATE_REGISTRY["active_element"] = 0
    else:
        STATE_REGISTRY["active_element"] = active_elements[0]

    STATE_REGISTRY["elements"][STATE_REGISTRY["active_element"]].on_lclick(event)

def on_rclick(event):
    global STATE_REGISTRY

    active_elements = STATE_REGISTRY["canvas"].find_withtag(CURRENT)
    if len(active_elements) == 0:
        STATE_REGISTRY["active_element"] = 0
    else:
        STATE_REGISTRY["active_element"] = active_elements[0]

    STATE_REGISTRY["elements"][STATE_REGISTRY["active_element"]].on_rclick(event)

#########################
# General Block Classes #
#########################

class FieldBase:

    TEXT_WPAD = 20
    TEXT_HPAD = 5

class FieldMap(FieldBase):

    def __init__(self, canvas, x, y, opt_map=dict(), pretext="TEST: "):
        global STATE_REGISTRY
        self.canvas = canvas
        self.x = x
        self.y = y
        self.opt_map = opt_map
        self.pretext = pretext

        self.id = -1
        self.selection = -1
        self.text_id = -1
        self.text = f"{self.pretext}<none>"
        self.text_color = "#FF0000"

        self.__draw__()
        STATE_REGISTRY["elements"][self.id] = self
        STATE_REGISTRY["elements"][self.text_id] = self

    def __draw__(self):
        # Draw and adjust text
        self.text_id = self.canvas.create_text(self.x, self.y, text=self.text, fill=self.text_color, font="Arial 12", anchor=NW)
        text_bbox = list(self.canvas.bbox(self.text_id))
        text_w = text_bbox[2] - text_bbox[0] + (2*FieldMap.TEXT_WPAD)
        text_h = text_bbox[3] - text_bbox[1] + (2*FieldMap.TEXT_HPAD)
        self.canvas.move(self.text_id, FieldMap.TEXT_WPAD, FieldMap.TEXT_HPAD)

        # Draw the bounding rectangle
        self.id = self.canvas.create_rectangle(self.x, self.y, self.x+text_w, self.y+text_h, outline="#FFFFFF", fill="#000000", activefill="#111111")
        self.canvas.tag_raise(self.text_id)

    def __redraw__(self):
        self.canvas.itemconfig(self.text_id, text=self.text, fill=self.text_color)
        text_bbox = list(self.canvas.bbox(self.text_id))
        text_w = text_bbox[2] - text_bbox[0] + (2*FieldMap.TEXT_WPAD)
        text_h = text_bbox[3] - text_bbox[1] + (2*FieldMap.TEXT_HPAD)
        self.canvas.coords(self.id, self.x, self.y, self.x+text_w, self.y+text_h)
        self.canvas.tag_raise(self.text_id)

    def __delete__(self):
        pass

    def __menu_select__(self, value):
        return lambda: self.set_selection(value)

    def set_selection(self, value):
        self.selection = value
        if self.selection == -1:
            selection_text = "<none>"
            self.text_color = "#FF0000"
        else:
            selection_text = self.opt_map[value]
            self.text_color = "#FFFFFF"
        self.text = f"{self.pretext}{selection_text}"
        self.__redraw__()

    def on_lclick(self, event):
        print("FIELD_CLICK")
        m = Menu(self.canvas, tearoff=0)
        for i in self.opt_map.keys():
            m.add_command(label=self.opt_map[i], command=self.__menu_select__(i))

        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    def on_rclick(self, event):
        print(f"SELECTION: {self.selection}")

    def get_width(self):
        coords = self.canvas.coords(self.id)
        return coords[2] - coords[0]



#######################
# Trigger Block Class #
#######################

class TriggerBlock:

    def __draw_section__(self, idx):
        section_w = 100
        section_h = 25
        section_x = self.x
        section_y = self.y + (idx * section_h)

        new_section = self.canvas.create_rectangle(section_x, section_y, section_x+section_w, section_y+section_h, outline="#FFFFFF", fill="#000000", activefill="#111111")
    
    def __draw__(self):
        for i, idx in enumerate(range(0, 5)):#enumerate(self.cls.INPUT_FIELDS):
            self.__draw_section__(idx)


    def __init__(self, canvas, trigger_class, x, y):
        self.canvas = canvas
        self.cls = trigger_class

        self.x = x
        self.y = y
        self.sections = list()
        self.node = None
        
        self.__draw__()


#############
# Main Loop #
#############

async def mainloop_task(loop):
    core_db = coredb.CoreDB()
    await core_db.db_init()
    device_manager = devices.DeviceManager()
    await core_db.ext.devices.reload_devices(device_manager)
    rule_manager = rules.RuleManager()
    await core_db.ext.rules.reload(rule_manager)
    print(rules.extensions.RULE_TRIGGER_REGISTRY["devices"]["value_seen"].get_field_maps())

    #
    # Test code, delete later
    #
    top = Tk()
    c = Canvas(top, bg="#000000", height=800, width=800)
    c.pack(fill="both", expand=True)

    STATE_REGISTRY["canvas"] = c
    c.bind("<ButtonPress-1>", on_lclick)
    c.bind("<ButtonPress-3>", on_rclick)
    t_field = FieldMap(c, 200, 200, {1:"Alpha",2:"Beta Gamma Delta"})

    top.mainloop()

mainloop = asyncio.new_event_loop()
mainloop.run_until_complete(mainloop_task(mainloop))