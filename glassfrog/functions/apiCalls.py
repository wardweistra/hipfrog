from flask import json
import requests


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
        messageUrl = hipchatApiSettings.hipchatApiUrl+'/room/{}/notification'.format(hipchatApiSettings.roomId)
        token_header = {"Authorization": "Bearer "+hipchatApiSettings.hipchatToken}
        data = createMessageDict(color, message)
        messageresponse = requests.post(messageUrl,
                                        headers=token_header,
                                        data=data)
