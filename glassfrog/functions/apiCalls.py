from flask import json, url_for
import requests

from .messageFunctions import createMessageDict
import glassfrog.strings as strings


class GlassfrogApiHandler(object):
    def __init__(self):
        pass

    def glassfrogApiCall(self, apiEndpoint, glassfrogToken):
        headers = {'X-Auth-Token': glassfrogToken}
        apiUrl = 'https://glassfrog.holacracy.org/api/v3/'+apiEndpoint
        apiResponse = requests.get(apiUrl, headers=headers)
        code = apiResponse.status_code
        responsebody = json.loads(apiResponse.text)
        return code, responsebody

    def getCircleForCircleId(self, circleId, glassfrogToken):
        apiEndpoint = 'circles/{}'.format(circleId)
        code, responsebody = self.glassfrogApiCall(apiEndpoint, glassfrogToken)
        return code, responsebody


class HipchatApiHandler(object):
    def __init__(self):
        pass

    def getCapabilitiesData(self, capabilitiesUrl):
        return json.loads(requests.get(capabilitiesUrl).text)

    def getTokenData(self, tokenUrl, client_auth, post_data):
        return json.loads(requests.post(tokenUrl, auth=client_auth, data=post_data).text)

    def sendMessage(self, color, message, installation):
        messageUrl = '{}/room/{}/notification'.format(installation.hipchatApiProvider_url,
                                                      installation.roomId)
        token_header = {"Authorization": "Bearer "+installation.access_token}
        data = createMessageDict(color, message)
        messageresponse = requests.post(messageUrl,
                                        headers=token_header,
                                        data=data)

    def getRoomMembers(self, installation):
        token_header = {"Authorization": "Bearer "+installation.access_token}

        requestUrl = '{}/room/{}'.format(installation.hipchatApiProvider_url,
                                         installation.roomId)
        messageresponse = requests.get(requestUrl, headers=token_header)

        if messageresponse.status_code != 200:
            return messageresponse.status_code, json.loads(messageresponse.text)

        privacy = json.loads(messageresponse.text)['privacy']

        if privacy == 'public':
            requestUrl = '{}/room/{}/participant'.format(installation.hipchatApiProvider_url,
                                                         installation.roomId)
        elif privacy == 'private':
            requestUrl = '{}/room/{}/members'.format(installation.hipchatApiProvider_url,
                                                     installation.roomId)
        messageresponse = requests.get(requestUrl, headers=token_header)

        return messageresponse.status_code, json.loads(messageresponse.text)


def getCapabilitiesDict(publicUrl):
    capabilities_dict = \
        {
            "name": "HipFrog",
            "description": "A Hipchat bot for accessing Glassfrog",
            "key": "hipfrog",
            "links": {
                "homepage": publicUrl,
                "self": publicUrl+"/capabilities.json"
            },
            "vendor": {
                "name": "The Hyve",
                "url": "https://www.thehyve.nl/"
            },
            "capabilities": {
                "hipchatApiConsumer": {
                    "fromName": "HipFrog",
                    "scopes": [
                        "send_notification",
                        "view_room"
                    ],
                    "avatar": {
                        "url": publicUrl+'/static/hipfrog.png',
                        "url@2x": publicUrl+'/static/hipfrog.png'
                    }
                },
                "installable": {
                    "allowGlobal": False,
                    "allowRoom": True,
                    "callbackUrl": publicUrl+"/installed"
                },
                "webhook": [
                    {
                        "event": "room_message",
                        "pattern": strings.regex_hipfrog,
                        "url": publicUrl+"/hipfrog",
                        "name": "Hipfrog webhook",
                        "authentication": "jwt"
                    },
                    {
                        "event": "room_message",
                        "pattern": strings.regex_at_role,
                        "url": publicUrl+"/atrole",
                        "name": "At Role webhook",
                        "authentication": "jwt"
                    },
                    {
                        "event": "room_message",
                        "pattern": strings.regex_at_circle,
                        "url": publicUrl+"/atcircle",
                        "name": "At Circle webhook",
                        "authentication": "jwt"
                    },
                    {
                        "event": "room_message",
                        "pattern": strings.regex_slash_role,
                        "url": publicUrl+"/slashrole",
                        "name": "Slash Role webhook",
                        "authentication": "jwt"
                    },
                    {
                        "event": "room_message",
                        "pattern": strings.regex_slash_circle,
                        "url": publicUrl+"/slashcircle",
                        "name": "Slash Circle webhook",
                        "authentication": "jwt"
                    }
                ],
                "configurable": {
                    "url": publicUrl+"/configure.html"
                }
            }
        }
    return capabilities_dict
