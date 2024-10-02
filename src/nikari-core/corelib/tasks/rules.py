# Nikari Core - Rule Tasks
#
# Written by Martianmellow12

import asyncio


STEP_DELAY = 0.01
RULE_MANAGER = None
EVENT_QUEUES = list()


########################
# Management Functions #
########################

def set_rule_manager(rule_manager):
    global RULE_MANAGER
    RULE_MANAGER = rule_manager

def add_event_queue(event_queue):
    global EVENT_QUEUES
    EVENT_QUEUES.append(event_queue)


#########
# Tasks #
#########

async def rule_manager_task():
    global RULE_MANAGER
    global EVENT_QUEUES

    while True:
        await asyncio.sleep(STEP_DELAY)
        for i in EVENT_QUEUES:
            while len(i) > 0:
                event = i.pop(0)
                await RULE_MANAGER.evaluate(event)
