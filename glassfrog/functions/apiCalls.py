from flask import json
import requests

from .messageFunctions import createMessageDict


class GlassfrogApiSettings(object):
    def __init__(self, glassfrogToken):
        self.glassfrogToken = glassfrogToken


class GlassfrogApiHandler(object):
    def __init__(self):
        pass

    def glassfrogApiCall(self, apiEndpoint, glassfrogApiSettings: GlassfrogApiSettings):
        headers = {'X-Auth-Token': glassfrogApiSettings.glassfrogToken}
        apiUrl = 'https://glassfrog.holacracy.org/api/v3/'+apiEndpoint
        apiResponse = requests.get(apiUrl, headers=headers)
        code = apiResponse.status_code
        responsebody = json.loads(apiResponse.text)
        return code, responsebody

class HipchatApiSettings(object):
    def __init__(self, hipchatToken, hipchatApiUrl, hipchatRoomId):
        self.hipchatToken = hipchatToken
        self.hipchatApiUrl = hipchatApiUrl
        self.hipchatRoomId = hipchatRoomId

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class HipchatApiHandler(object):
    def __init__(self):
        pass

    def getCapabilitiesData(self, capabilitiesUrl):
        return json.loads(requests.get(capabilitiesUrl).text)

    def getTokenData(self, tokenUrl, client_auth, post_data):
        return json.loads(requests.post(tokenUrl, auth=client_auth, data=post_data).text)

    def sendMessage(self, color, message, hipchatApiSettings: HipchatApiSettings):
        messageUrl = hipchatApiSettings.hipchatApiUrl+'/room/{}/notification'.format(hipchatApiSettings.hipchatRoomId)
        token_header = {"Authorization": "Bearer "+hipchatApiSettings.hipchatToken}
        data = createMessageDict(color, message)
        messageresponse = requests.post(messageUrl,
                                        headers=token_header,
                                        data=data)


def getCapabilitiesDict(myserver):
    capabilities_dict = \
        {
            "name": "Glassfrog Hipchat Bot",
            "description": "A Hipchat bot for accessing Glassfrog",
            "key": "glassfrog-hipchat-bot",
            "links": {
                "homepage": myserver,
                "self": myserver+"/capabilities.json"
            },
            "vendor": {
                "name": "The Hyve",
                "url": "https://www.thehyve.nl/"
            },
            "capabilities": {
                "hipchatApiConsumer": {
                    "fromName": "Glassfrog Hipchat Bot",
                    "scopes": [
                        "send_notification",
                        "view_room",
                        "view_group"
                    ]
                },
                "installable": {
                    "allowGlobal": False,
                    "allowRoom": True,
                    "callbackUrl": myserver+"/installed"
                },
                "webhook": [
                    {
                        "event": "room_message",
                        "pattern": "\\A\\/hola\\b",
                        "url": myserver+"/hola",
                        "name": "Holacracy webhook",
                        "authentication": "jwt"
                    }
                ],
                "configurable": {
                    "url": myserver+"/configure.html"
                }
            }
        }
    return capabilities_dict
