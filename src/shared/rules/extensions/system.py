# Nikari Rule Library - System Extension
#
# Written by Martianmellow12

import asyncio
import sys
import os

from . import TriggerBase, ActionBase, register_trigger, register_action

from shared import nikari_logging

# Note: only system rules should ever access core functionality
sys.path.append(os.path.join("..", "..", "nikari-core"))
from corelib import coredb

NAME = "System Rules"
COREDB = coredb.CoreDB()


##################
# Action Classes #
##################

@register_action("system", "set_policy_active")
class ActionSetPolicyActive(ActionBase):

    INPUT_FIELDS = [
        {
            "name" : "uid",
            "type" : "number"
        },
        {
            "name" : "is_active",
            "type" : "number"
        }
    ]

    def __init__(self, fields):
        super().__init__(fields)

    async def fire(self):
        nikari_logging.log(NAME, f"Setting policy {self.fields['uid']} is_active={self.fields['is_active']}")
        await self.__rule_manager__.set_policy_active(self.fields["uid"], self.fields["is_active"])

@register_action("system", "toggle_policy_active")
class ActionTogglePolicyActive(ActionBase):

    INPUT_FIELDS = [
        {
            "name" : "uid",
            "type" : "number"
        }
    ]

    def __init__(self, fields):
        super().__init__(fields)

    async def fire(self):
        is_active = 0 if await self.__rule_manager__.get_policy_active(self.fields["uid"]) else 1
        nikari_logging.log(NAME, f"Setting policy {self.fields['uid']} is_active={is_active}")
        await self.__rule_manager__.set_policy_active(self.fields["uid"], is_active)