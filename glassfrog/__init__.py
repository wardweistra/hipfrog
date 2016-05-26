#!/usr/bin/env python3
from flask import Flask, json, request
app = Flask(__name__)

myserver = "http://5.157.82.115:45277"


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/capabilities.json')
def capabilities():
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
                        "send_notification"
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
                        "pattern": "^\\/test$",
                        "url": myserver+"/test",
                        "name": "Test webhook",
                        "authentication": "jwt"
                    }
                ]
            }
        }
    return json.jsonify(capabilities_dict)


@app.route('/installed', methods=['GET', 'POST'])
def installed():
    print(request.get_data())
    # b'{"oauthId": "f3100c47-9936-40e8-a8aa-798b1e8da8f0", "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities", "roomId": 2589171, "groupId": 46617, "oauthSecret": "Jgtf1Baj5KrSpXHZ7LbB0H3Krwr6cotrkQgkJm9C"}'
    return ('', 200)


@app.route('/test', methods=['GET', 'POST'])
def test():
    print(request.get_data())
    # b'{"oauthId": "f3100c47-9936-40e8-a8aa-798b1e8da8f0", "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities", "roomId": 2589171, "groupId": 46617, "oauthSecret": "Jgtf1Baj5KrSpXHZ7LbB0H3Krwr6cotrkQgkJm9C"}'
    return ('', 200)


if __name__ == '__main__':
    app.run()
