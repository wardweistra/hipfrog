#!/usr/bin/env python3
from flask import Flask, json, request, render_template
import requests

app = Flask(__name__)

myserver = "http://5.157.82.115:45277"
app.token = ''
app.glassfrogtoken = ''


@app.route('/')
def hello_world():
    return '<a target="_blank" href="https://www.hipchat.com/addons/install?url='+myserver+"/capabilities.json"+'">Install Glassfrog HipChat Integration</a>'


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
    return json.jsonify(capabilities_dict)


@app.route('/installed', methods=['GET', 'POST'])
def installed():
    if request.method == 'POST':
        installdata = json.loads(request.get_data())
        # b'{"oauthId": "f3100c47-9936-40e8-a8aa-798b1e8da8f0", "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities", "roomId": 2589171, "groupId": 46617, "oauthSecret": "Jgtf1Baj5KrSpXHZ7LbB0H3Krwr6cotrkQgkJm9C"}'
        print(installdata)
        CLIENT_ID = installdata['oauthId']
        CLIENT_SECRET = installdata['oauthSecret']
        room_id = installdata['roomId']

        capabilitiesdata = json.loads(requests.get(installdata['capabilitiesUrl']).text)
        tokenUrl = capabilitiesdata['capabilities']['oauth2Provider']['tokenUrl']
        print(tokenUrl)

        client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        post_data = {"grant_type": "client_credentials",
                     "scope": "send_notification"}
        tokendata = json.loads(requests.post(tokenUrl,
                                             auth=client_auth,
                                             data=post_data).text)
        print(tokendata)
        # {'expires_in': 431999999, 'group_name': 'tranSMART', 'access_token': 'qjVBeM4ckCYzrc2prQMwuRZnHB3xUVsBwZISP0TF', 'group_id': 46617, 'scope': 'send_notification', 'token_type': 'bearer'}
        app.token = tokendata['access_token']
        apiUrl = capabilitiesdata['capabilities']['hipchatApiProvider']['url']
        messageUrl = apiUrl+'/room/{}/notification'.format(room_id)
        token_header = {"Authorization": "Bearer "+app.token}
        data = {
            "color": "green",
            "message": "Installed successfully. Type /hola to get started.",
            "notify": False,
            "message_format": "text"
            }
        messageresponse = requests.post(messageUrl,
                                        headers=token_header,
                                        data=data)
    return ('', 200)


@app.route('/installed/<oauthId>/', methods=['GET', 'POST'])
def uninstall(oauthId):
    return ('', 200)


def getcircles():
    headers = {'X-Auth-Token': app.glassfrogtoken}
    circlesUrl = 'https://glassfrog.holacracy.org/api/v3/circles'
    circlesresponse = requests.get(circlesUrl, headers=headers)
    print(circlesresponse)
    circles = circlesresponse.text
    print(circles)
    return circles


@app.route('/hola', methods=['GET', 'POST'])
def hola():
    print(request.get_data())
    # b'{"event": "room_message", "item": {"message": {"date": "2016-05-26T15:32:43.700609+00:00", "from": {"id": 351107, "links": {"self": "https://api.hipchat.com/v2/user/351107"}, "mention_name": "WardWeistra", "name": "Ward Weistra", "version": "00000000"}, "id": "715f101f-1baa-4a5c-958a-9c6c7efaaa1f", "mentions": [], "message": "/test", "type": "message"}, "room": {"id": 2589171, "is_archived": false, "links": {"members": "https://api.hipchat.com/v2/room/2589171/member", "participants": "https://api.hipchat.com/v2/room/2589171/participant", "self": "https://api.hipchat.com/v2/room/2589171", "webhooks": "https://api.hipchat.com/v2/room/2589171/webhook"}, "name": "The Hyve - Holacracy", "privacy": "private", "version": "0XLIKALD"}}, "oauth_client_id": "ed8bb9f0-02d8-426b-9226-0d50fdcd47ea", "webhook_id": 4965523}'
    if app.glassfrogtoken != '':
        message = getcircles()
        print(message)
        message_dict = {
            "color": "green",
            "message": message,
            "notify": False,
            "message_format": "text"
            }
    else:
        message_dict = {
            "color": "red",
            "message": "Please set the Glassfrog token first in the plugin configuration",
            "notify": False,
            "message_format": "text"
            }
    return json.jsonify(message_dict)


@app.route('/configure.html', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        app.glassfrogtoken = request.form['glassfrogtoken']
    return render_template('configure.html', glassfrogtoken=app.glassfrogtoken)

if __name__ == '__main__':
    app.run()
