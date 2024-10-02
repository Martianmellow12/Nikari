# Nikari - Logging Library
#
# Written by Martianmellow12

import datetime

ENABLE_DEBUG_MESSAGES = False

def log(name, msg, timestamp=True, indent_level=0, debug=False):
    if debug and (not ENABLE_DEBUG_MESSAGES): return

    if timestamp:
        timestamp_str = f"{datetime.datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')} "
    else:
        timestamp_str = ""
    msg_formatted = f"{'  '*indent_level}{timestamp_str}[{name}] {msg}"
    print(msg_formatted)
    # TODO(martianmellow12): Save to a log file