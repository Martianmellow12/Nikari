# Nikari - Pushover API Library
#
# Written by Martianmellow12

import base64
import requests

ENDPOINT = "https://api.pushover.net/1/messages.json"

def send_message(token, user, message, allow_html=False):
    # Required fields
    params = {
        "token" : token,
        "user" : user,
        "message" : message,
        "ttl" : 5,
        "url" : "https://www.google.com"
    }

    # Optional fields
    if allow_html: params["html"] = 1

    results = requests.post(ENDPOINT, params=params)
    print(f"{results.status_code} -> {results.text}")

def get_groups(token, user):
    url = f" https://api.pushover.net/1/groups/{user}.json?token={token} "
    results = requests.get(url)
    return results.text