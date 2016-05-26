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
                        "pattern": "\\A\\/test\\b",
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
    # b'{"event": "room_message", "item": {"message": {"date": "2016-05-26T15:32:43.700609+00:00", "from": {"id": 351107, "links": {"self": "https://api.hipchat.com/v2/user/351107"}, "mention_name": "WardWeistra", "name": "Ward Weistra", "version": "00000000"}, "id": "715f101f-1baa-4a5c-958a-9c6c7efaaa1f", "mentions": [], "message": "/test", "type": "message"}, "room": {"id": 2589171, "is_archived": false, "links": {"members": "https://api.hipchat.com/v2/room/2589171/member", "participants": "https://api.hipchat.com/v2/room/2589171/participant", "self": "https://api.hipchat.com/v2/room/2589171", "webhooks": "https://api.hipchat.com/v2/room/2589171/webhook"}, "name": "The Hyve - Holacracy", "privacy": "private", "version": "0XLIKALD"}}, "oauth_client_id": "ed8bb9f0-02d8-426b-9226-0d50fdcd47ea", "webhook_id": 4965523}'
    return ('', 200)


if __name__ == '__main__':
    app.run()
