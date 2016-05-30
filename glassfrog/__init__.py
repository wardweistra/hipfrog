#!/usr/bin/env python3
from flask import Flask, json, request, render_template, flash
import requests

app = Flask(__name__)
app.secret_key = 'not_so_secret'

myserver = "http://5.157.82.115:45277"
app.hipchatToken = ''
app.glassfrogToken = ''
app.hipchatApiUrl = ''
app.roomId = ''


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
    return json.jsonify(capabilities_dict)


@app.route('/installed', methods=['GET', 'POST'])
def installed():
    if request.method == 'POST':
        installdata = json.loads(request.get_data())

        CLIENT_ID = installdata['oauthId']
        CLIENT_SECRET = installdata['oauthSecret']
        app.roomId = installdata['roomId']

        capabilitiesdata = json.loads(requests.get(installdata['capabilitiesUrl']).text)
        tokenUrl = capabilitiesdata['capabilities']['oauth2Provider']['tokenUrl']

        client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        post_data = {"grant_type": "client_credentials",
                     "scope": "send_notification"}
        tokendata = json.loads(requests.post(tokenUrl,
                                             auth=client_auth,
                                             data=post_data).text)

        app.hipchatToken = tokendata['access_token']
        app.hipchatApiUrl = capabilitiesdata['capabilities']['hipchatApiProvider']['url']

        sendMessage('green', "Installed successfully. Please set Glassfrog Token in the Hipchat Integration Configure page.")
    return ('', 200)


@app.route('/installed/<oauthId>', methods=['GET', 'POST', 'DELETE'])
def uninstall(oauthId):
    # TODO Delete entries related to this installation (oauthID) from database.
    return ('', 200)


def getCircles():
    headers = {'X-Auth-Token': app.glassfrogToken}
    circlesUrl = 'https://glassfrog.holacracy.org/api/v3/circles'
    circlesresponse = requests.get(circlesUrl, headers=headers)
    print(circlesresponse)
    code = circlesresponse.status_code
    print(code)

    responsebody = json.loads(circlesresponse.text)
    if code == 200:
        message = 'The following circles are in your organization:'
        for circle in circles['circles']:
            message = message + '\n- ' + circle['name'] + '(' + circle['id'] + ')'
    else:
        message = responsebody['message']

    print(circles)
    return code, message


def createMessageDict(color, message):
    message_dict = {
        "color": color,
        "message": str(message),
        "notify": False,
        "message_format": "text"
        }
    return message_dict


def sendMessage(color, message):
    messageUrl = app.hipchatApiUrl+'/room/{}/notification'.format(app.roomId)
    token_header = {"Authorization": "Bearer "+app.hipchatToken}
    data = createMessageDict(color, message)
    messageresponse = requests.post(messageUrl,
                                    headers=token_header,
                                    data=data)


def helpInformation():
    message = "Hola to you too!  Thanks for using the Glassfrog Hipchat Bot.\nPlease use one of the following commands to find out more:\n- /hola circles -- List the circles in your organization"
    return message


@app.route('/hola', methods=['GET', 'POST'])
def hola():
    requestdata = json.loads(request.get_data())
    print(requestdata)
    callingMessage = requestdata['item']['message']['message'].split()
    if app.glassfrogToken == '':
        message = "Please set the Glassfrog Token first in the plugin configuration"
        message_dict = createMessageDict('red', message)
    elif len(callingMessage) == 1:
        message = helpInformation()
        message_dict = createMessageDict('green', message)
    elif len(callingMessage) > 1:
        if callingMessage[1] == 'circles' or callingMessage[1] == 'circle':
            code, message = getCircles()
            message_dict = createMessageDict('green', message)
        else:
            message = "Sorry, the feature \'"+callingMessage[1]+"\' does not exist (yet). Type /hola to get help information."
            message_dict = createMessageDict('red', message)
    return json.jsonify(message_dict)


@app.route('/configure.html', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        app.glassfrogToken = request.form['glassfrogtoken']
        code, message = getCircles()
        if code == 200:
            flashmessage = 'Valid Glassfrog Token stored'
            sendMessage('green', "Configured successfully. Type /hola to get started!")
        else:
            flashmessage = 'Encountered Error '+str(code)+' when testing the Glassfrog Token.'
            flashmessage = flashmessage + ' Message given: \''+message+'\'.'
        flash(flashmessage)
    return render_template('configure.html', glassfrogtoken=app.glassfrogToken)

if __name__ == '__main__':
    app.run()
