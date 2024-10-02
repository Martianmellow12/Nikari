import aiosqlite
import json
from . import DbExtensionBase, db_extension

devices_table_sql = """
CREATE TABLE IF NOT EXISTS devices (
    uid integer PRIMARY KEY,
    type text,
    friendly_name text,
    metadata text,
    attributes text
);
"""

add_device_sql = "INSERT INTO devices(type, friendly_name, metadata, attributes) VALUES(?, ?, ?, ?);"
delete_device_sql = "DELETE FROM devices WHERE uid=?;"

@db_extension("devices")
class Devices(DbExtensionBase):

    def __init__(self):
        super().__init__()
        print("Initialized CoreDB extension \"devices\"")

    async def create_tables(self, db_obj):
        await db_obj.execute(devices_table_sql)

    async def add_device(self, device_type, friendly_name, metadata, attributes):
        metadata_json = json.dumps(metadata)
        attributes_json = json.dumps(attributes)
        
        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(add_device_sql, (device_type, friendly_name, metadata_json, attributes_json))
            await db.commit()

    async def delete_device(self, device_uid):
        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(delete_device_sql, (device_uid,))
            await db.commit()

    async def get_devices(self, device_type=None):
        async with aiosqlite.connect(self.__db_path__) as db:
            c = await db.cursor()
            if device_type: await c.execute("SELECT * FROM devices where type=?;", (device_type, ))
            else: await c.execute("SELECT * FROM devices;")
            results = await c.fetchall()
            
        device_list = list()
        for i in results:
            device_dict = {
                "uid" : i[0],
                "type" : i[1],
                "friendly_name" : i[2],
                "metadata" : json.loads(i[3]),
                "attributes" : json.loads(i[4])
            }
            device_list.append(device_dict)
            
        return device_list
    
    async def reload_devices(self, device_manager):
        device_list = await self.get_devices()
        for i in device_list:
            device_manager.add_device(i)