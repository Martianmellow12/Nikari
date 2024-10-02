import aiosqlite
import json
from . import DbExtensionBase, db_extension

rules_table_sql = """
CREATE TABLE IF NOT EXISTS rules (
    uid integer PRIMARY KEY,
    triggers text,
    conditions text,
    actions text
);
"""
policies_table_sql = """
CREATE TABLE IF NOT EXISTS policies (
    uid integer PRIMARY KEY,
    name text,
    rules text,
    is_active integer
);
"""

add_rule_sql = "INSERT INTO rules(triggers, conditions, actions) VALUES(?, ?, ?);"
delete_rule_sql = "DELETE FROM rules WHERE uid=?;"
add_policy_sql = "INSERT INTO policies(name, rules, is_active) VALUES(?, ?, ?);"
delete_policy_sql = "DELETE FROM policies WHERE uid=?;"
set_policy_sql = "UPDATE policies SET is_active=? WHERE uid=?;"

@db_extension("rules")
class Rules(DbExtensionBase):

    def __init__(self):
        super().__init__()
        print("Initialized CoreDB extension \"rules\"")

    async def create_tables(self, db_obj):
        await db_obj.execute(rules_table_sql)
        await db_obj.execute(policies_table_sql)

    async def add_rule(self, ser_rule):
        triggers_json = json.dumps(ser_rule["triggers"])
        conditions_json = json.dumps(ser_rule["conditions"])
        actions_json = json.dumps(ser_rule["actions"])

        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(add_rule_sql, (triggers_json, conditions_json, actions_json))
            await db.commit()

    async def delete_rule(self, uid):
        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(delete_rule_sql, (uid, ))
            await db.commit()

    async def get_rules(self):
        async with aiosqlite.connect(self.__db_path__) as db:
            c = await db.cursor()
            await c.execute("SELECT * FROM rules;")
            results = await c.fetchall()

        rules_list = list()
        for i in results:
            ser_rule = {
                "uid" : i[0],
                "triggers" : json.loads(i[1]),
                "conditions" : json.loads(i[2]),
                "actions" : json.loads(i[3])
            }
            rules_list.append(ser_rule)
        return rules_list
    
    async def add_policy(self, ser_policy):
        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(add_policy_sql, (ser_policy["name"], json.dumps(ser_policy["rules"]), ser_policy["is_active"]))
            await db.commit()

    async def delete_policy(self, uid):
        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(delete_policy_sql, (uid, ))
            await db.commit()

    async def get_policies(self):
        async with aiosqlite.connect(self.__db_path__) as db:
            c = await db.cursor()
            await c.execute("SELECT * FROM policies;")
            results = await c.fetchall()

        policy_list = list()
        for i in results:
            ser_policy = {
                "uid" : i[0],
                "name" : i[1],
                "rules" : json.loads(i[2]),
                "is_active" : i[3]
            }
            policy_list.append(ser_policy)
        return policy_list
    
    async def get_policy_active(self, uid):
        policies = await self.get_policies()
        for i in policies:
            if i["uid"] == uid:
                return i["is_active"]
        return None
    
    async def set_policy_active(self, uid, is_active):
        if is_active: is_active = 1
        else: is_active = 0
        async with aiosqlite.connect(self.__db_path__) as db:
            await db.execute(set_policy_sql, (is_active, uid))
            await db.commit()

    async def reload(self, rule_manager):
        rules = await self.get_rules()
        policies = await self.get_policies()

        for i in rules: rule_manager.add_rule(i)
        for i in policies: rule_manager.add_policy(i)

