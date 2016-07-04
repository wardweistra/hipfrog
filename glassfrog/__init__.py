#!/usr/bin/env python3
from flask import Flask, json, request, render_template, flash
import requests

from .functions import apiCalls
from .functions.messageFunctions import createMessageDict

app = Flask(__name__)
app.secret_key = 'not_so_secret'

myserver = "http://5.157.82.115:45277"
app.hipchatApiSettings = None
app.glassfrogToken = ''


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

        hipchatApiHandler = apiCalls.HipchatApiHandler()

        capabilitiesdata = hipchatApiHandler.getCapabilitiesData(installdata['capabilitiesUrl'])
        tokenUrl = capabilitiesdata['capabilities']['oauth2Provider']['tokenUrl']

        client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        post_data = {"grant_type": "client_credentials",
                     "scope": "send_notification"}
        tokendata = hipchatApiHandler.getTokenData(tokenUrl, client_auth, post_data)

        app.hipchatApiSettings = apiCalls.HipchatApiSettings(
                                    hipchatToken=tokendata['access_token'],
                                    hipchatApiUrl=capabilitiesdata['capabilities']['hipchatApiProvider']['url'],
                                    hipchatRoomId=installdata['roomId'])

        hipchatApiHandler.sendMessage(
            color='green',
            message="Installed successfully. Please set Glassfrog Token in the Hipchat Integration Configure page.",
            hipchatApiSettings=app.hipchatApiSettings)
    return ('', 200)


@app.route('/installed/<oauthId>', methods=['GET', 'POST', 'DELETE'])
def uninstall(oauthId):
    # TODO Delete entries related to this installation (oauthID) from database.
    return ('', 200)


def glassfrogApiCall(apiEndpoint):
    headers = {'X-Auth-Token': app.glassfrogToken}
    apiUrl = 'https://glassfrog.holacracy.org/api/v3/'+apiEndpoint
    apiResponse = requests.get(apiUrl, headers=headers)
    code = apiResponse.status_code
    responsebody = json.loads(apiResponse.text)
    return code, responsebody


def getCircles():
    apiEndpoint = 'circles'
    code, responsebody = glassfrogApiCall(apiEndpoint)

    if code == 200:
        message = 'The following circles are in your organization:'
        for circle in responsebody['circles']:
            message = message + '\n- ' + circle['name'] + ' (/hola circle ' + str(circle['id']) + ')'
    else:
        message = responsebody['message']

    return code, message


def getCircleMembers(circleId):
    apiEndpoint = 'circles/{}/people'.format(circleId)
    code, responsebody = glassfrogApiCall(apiEndpoint)

    if code == 200:
        message = 'The following people are in your circle:'
        for person in responsebody['people']:
            message = message + '\n- ' + person['name'] + ' (' + str(person['id']) + ')'
    else:
        message = responsebody['message']

    return code, message


def helpInformation():
    message = "Hola to you too!  Thanks for using the Glassfrog Hipchat Bot.\nPlease use one of the following commands to find out more:\n- /hola circles -- List the circles in your organization"
    return message


def helpInformationCircle(circleId):
    message = "Please use one of the following commands on your circle to find out more:\n- /hola circle "+circleId+" members -- List the members of this circle"
    return message


@app.route('/hola', methods=['GET', 'POST'])
def hola():
    requestdata = json.loads(request.get_data())
    callingMessage = requestdata['item']['message']['message'].split()
    if app.glassfrogToken == '':
        message = "Please set the Glassfrog Token first in the plugin configuration"
        message_dict = createMessageDict('red', message)
    elif len(callingMessage) == 1:
        message = helpInformation()
        message_dict = createMessageDict('green', message)
    elif len(callingMessage) > 1:
        if callingMessage[1] == 'circles' or callingMessage[1] == 'circle':
            if len(callingMessage) > 2:
                circleId = callingMessage[2]
                if len(callingMessage) > 3:
                    if callingMessage[3] == 'people' or callingMessage[3] == 'members':
                        # /hola [circles, circle] [circleId] [people, members]
                        code, message = getCircleMembers(circleId)
                        message_dict = createMessageDict('green', message)
                    else:
                        # /hola [circles, circle] [circleId] something
                        message = "Sorry, the feature \'"+callingMessage[3]+"\' does not exist (yet). Type /hola circle "+circleId+" to get a list of the available commands."
                        message_dict = createMessageDict('red', message)
                else:
                    # /hola [circles, circle] [circleId]
                    message = helpInformationCircle(circleId)
                    message_dict = createMessageDict('green', message)
            else:
                # /hola [circles, circle]
                code, message = getCircles()
                message_dict = createMessageDict('green', message)
        else:
            # /hola something
            message = "Sorry, the feature \'"+callingMessage[1]+"\' does not exist (yet). Type /hola to get a list of the available commands."
            message_dict = createMessageDict('red', message)
    return json.jsonify(message_dict)


@app.route('/configure.html', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        app.glassfrogToken = request.form['glassfrogtoken']
        code, message = getCircles()
        if code == 200:
            flashmessage = 'Valid Glassfrog Token stored'
            hipchatApiHandler = apiCalls.HipchatApiHandler()
            hipchatApiHandler.sendMessage(
                        color='green',
                        message="Configured successfully. Type /hola to get started!",
                        hipchatApiSettings=app.hipchatApiSettings)
        else:
            flashmessage = 'Encountered Error '+str(code)+' when testing the Glassfrog Token.'
            flashmessage = flashmessage + ' Message given: \''+message+'\'.'
        flash(flashmessage)
    return render_template('configure.html', glassfrogtoken=app.glassfrogToken)

if __name__ == '__main__':
    app.run()
