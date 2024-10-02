# Nikari - Core DB Library
#
# Written by Martianmellow12

import aiosqlite
import datetime
import json
import os
import pathlib

from .extensions import *


#################
# Core DB Class #
#################

class CoreDB:

    ####################
    # Internal Methods #
    ####################


    ########################
    # General User Methods #
    ########################

    def __init__(self):
        self.__path__ = pathlib.Path(__file__).parent.resolve()
        self.__filename__ = "core.db"
        self.__filepath__ = os.path.join(self.__path__, self.__filename__)
        self.ext = extensions.EXTENSIONS

    async def db_init(self):
        if not os.path.exists(self.__path__):
            os.mkdir(self.__path__)

        async with aiosqlite.connect(self.__filepath__) as db:
            for i in self.ext.list:
                i.__db_path__ = self.__filepath__
                await i.create_tables(db)


    ############################
    # Light Management Methods #
    ############################

    async def add_light(self, light_type, room, ip_addr, port, meta={}):
        async with aiosqlite.connect(self.__filepath__) as db:
            await db.execute("INSERT INTO lights(type, room, ip_addr, port, meta) VALUES(?, ?, ?, ?, ?);", (light_type, room, ip_addr, port, json.dumps(meta)))
            await db.commit()
        return True
    
    async def remove_light(self, light_id):
        async with aiosqlite.connect(self.__filepath__) as db:
            await db.execute("DELETE FROM lights WHERE id = ?;", (light_id,))
            await db.commit()
        return True

    async def get_lights(self, light_id=None, light_type=None, room=None):
        selection_str, selection_tuple = self.__selection_list__(("id", "type", "room"), (light_id, light_type, room))

        async with aiosqlite.connect(self.__filepath__) as db:
            c = await db.cursor()
            await c.execute("PRAGMA table_info(lights);")
            col_names = [i[1] for i in await c.fetchall()]
            await c.execute(f"SELECT * FROM lights{selection_str};", selection_tuple)
            lights = await c.fetchall()
        
        results = list()
        for light in lights:
            light_dict = dict()
            for idx, i in enumerate(col_names):
                light_dict[i] = light[idx]
            results.append(light_dict)
        for light in results:
            light["meta"] = json.loads(light["meta"])
        return results


    ############################
    # Event Management Methods #
    ############################

    async def add_event(self, title, start_time, duration):
        pass


    #
    # TODO(martianmellow12): DEPRECATED, REMOVE LATER
    #

    async def add_event(self, time, type_str, body, title="Nikari", url=None, url_title=None, allow_html=False, priority=0, device=None):
        time_str = str(time)

        async with aiosqlite.connect(self.__filepath__) as db:
            await db.execute("""INSERT INTO events(time_str,
                                                   type,
                                                   title,
                                                   body,
                                                   url,
                                                   url_title,
                                                   allow_html,
                                                   priority,
                                                   device)
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, )""",
                                (time_str, type_str, title, body, url, url_title, allow_html, priority, device))
            await db.commit()
        return True
    
    async def get_events(self, start_time=datetime.datetime.now()):
        datetime_fstr = "%Y-%m-%d %H:%M:%S.%f"

        async with aiosqlite.connect(self.__filepath__) as db:
            c = await db.cursor()
            await c.execute("PRAGMA table_info(events);")
            col_names = [i[1] for i in await c.fetchall()]
            await c.execute(f"SELECT * FROM events;")
            events = await c.fetchall()

        event_list = list()
        for event in events:
            event_dict = dict()
            for idx, i in enumerate(col_names):
                event_dict[i] = event[idx]
            event_dict["time"] = datetime.datetime.strptime(event_dict["time_str"], datetime_fstr)
            if event_dict["time"] >= start_time:
                event_list.append(event_dict)
        return event_list