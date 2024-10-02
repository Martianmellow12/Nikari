# Nikari Rule Library
#
# Written by Martianmellow12

import asyncio
import os

from . import extensions

from shared import nikari_logging

NAME = "Rule Manager"
COREDB = None
RULE_REGISTRY = dict()
POLICY_REGISTRY = dict()


##############
# Rule Class #
##############

class Rule:

    def __init__(self, ser_rule):
        self.uid = ser_rule["uid"]
        self.triggers = list()
        self.conditions = list()
        self.actions = list()

        for i in ser_rule["triggers"]: self.add_trigger(i)
        for i in ser_rule["conditions"]: self.add_condition(i)
        for i in ser_rule["actions"]: self.add_action(i)

    def add_trigger(self, ser_trigger):
        self.triggers.append(extensions.RULE_TRIGGER_REGISTRY[ser_trigger["type"]][ser_trigger["subtype"]](ser_trigger["fields"]))

    def add_condition(self, ser_condition):
        # TODO(martianmellow12): Implement this
        pass

    def add_action(self, ser_action):
        self.actions.append(extensions.RULE_ACTION_REGISTRY[ser_action["type"]][ser_action["subtype"]](ser_action["fields"]))

    async def evaluate(self, obj):
        trigger_detected = False

        # Evaluate triggers
        for i in self.triggers:
            if i.check(obj): trigger_detected = True
        if not trigger_detected: return False

        # Evaluate conditions
        # TODO(martianmellow12): Implement this

        # Fire actions
        for i in self.actions:
            nikari_logging.log(NAME, f"Firing actions for rule UID={self.uid}")
            # TODO(martianmellow12): Add support for both parallel and serial action sets
            loop = asyncio.get_running_loop()
            loop.create_task(i.fire())

    def serialize(self):
        return {
            "uid" : self.uid,
            "triggers" : [i.serialize() for i in self.triggers],
            "conditions" : [i.serialize() for i in self.conditions],
            "actions" : [i.serialize() for i in self.actions]
        }


################
# Policy Class #
################
            
class Policy:

    def __init__(self, ser_policy):
        self.uid = ser_policy["uid"]
        self.name = ser_policy["name"]
        self.rules = ser_policy["rules"]
        self.is_active = ser_policy["is_active"]

    def serialize(self):
        return {
            "uid" : self.uid,
            "name" : self.name,
            "rules" : self.rules,
            "is_active" : self.is_active
        }


################
# Rule Manager #
################

class RuleManager:

    def set_coredb(self, core_db):
        global COREDB
        COREDB = core_db

    def add_rule(self, ser_rule):
        RULE_REGISTRY[ser_rule["uid"]] = Rule(ser_rule)

    def add_policy(self, ser_policy):
        POLICY_REGISTRY[ser_policy["uid"]] = Policy(ser_policy)

    async def get_policy_active(self, uid):
        return POLICY_REGISTRY[uid].is_active

    async def set_policy_active(self, uid, active):
        POLICY_REGISTRY[uid].is_active = active
        await COREDB.ext.rules.set_policy_active(uid, active)

    def get_trigger_types(self, trigger_type=None):
        if trigger_type:
            return extensions.RULE_TRIGGER_REGISTRY[trigger_type].keys()
        else:
            return extensions.RULE_TRIGGER_REGISTRY.keys()
            
    async def evaluate(self, fields):
        nikari_logging.log(NAME, f"SAW EVENT FIELDS: {fields}", debug=True)
        for policy_uid in POLICY_REGISTRY.keys():
            if POLICY_REGISTRY[policy_uid].is_active:
                for rule_uid in POLICY_REGISTRY[policy_uid].rules:
                    if rule_uid in RULE_REGISTRY.keys():
                        await RULE_REGISTRY[rule_uid].evaluate(fields)

    def get_rules(self):
        return [RULE_REGISTRY[i] for i in RULE_REGISTRY.keys()]

#####################
# Extension Imports #
#####################

extensions.RULE_MANAGER = RuleManager()
from .extensions import *