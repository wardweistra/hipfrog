from flask import json
import requests


class HipchatApiHandler(object):
    def __init__(self):
        pass

    def getCapabilitiesData(self, capabilitiesUrl):
        return json.loads(requests.get(capabilitiesUrl).text)

    def getTokenData(self, tokenUrl, client_auth, post_data):
        return json.loads(requests.post(tokenUrl, auth=client_auth, data=post_data).text)
