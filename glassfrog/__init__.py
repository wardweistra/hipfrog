#!/usr/bin/env python3
from flask import Flask, json, request, render_template, flash
import requests

from .functions import apiCalls
from .functions import messageFunctions as messageFunctions
from .strings import *

app = Flask(__name__)
app.secret_key = 'not_so_secret'

myserver = "http://5.157.82.115:45277"
app.hipchatApiSettings = None
app.glassfrogApiSettings = None


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
            color=strings.succes_color,
            message=strings.installed_successfully,
            hipchatApiSettings=app.hipchatApiSettings)
    return ('', 200)


@app.route('/installed/<oauthId>', methods=['GET', 'POST', 'DELETE'])
def uninstall(oauthId):
    # TODO Delete entries related to this installation (oauthID) from database.
    return ('', 200)


def getCircles():
    apiEndpoint = 'circles'
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint, app.glassfrogApiSettings)

    if code == 200:
        message = 'The following circles are in your organization:'
        for circle in responsebody['circles']:
            message = message + '\n- ' + circle['name'] + ' (/hola circle ' + str(circle['id']) + ')'
    else:
        message = responsebody['message']

    return code, message


def getCircleMembers(circleId):
    apiEndpoint = 'circles/{}/people'.format(circleId)
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint, app.glassfrogApiSettings)

    if code == 200:
        message = 'The following people are in your circle:'
        for person in responsebody['people']:
            message = message + '\n- ' + person['name'] + ' (' + str(person['id']) + ')'
    else:
        message = responsebody['message']

    return code, message


def helpInformation():
    message = help_information
    return message


def helpInformationCircle(circleId):
    message = strings.help_circle.format(circleId)
    return message


@app.route('/hola', methods=['GET', 'POST'])
def hola():
    requestdata = json.loads(request.get_data())

    callingMessage = requestdata['item']['message']['message'].split()
    if app.glassfrogApiSettings is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    elif len(callingMessage) == 1:
        message = helpInformation()
        message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
    elif len(callingMessage) > 1:
        if callingMessage[1] == 'circles' or callingMessage[1] == 'circle':
            if len(callingMessage) > 2:
                circleId = callingMessage[2]
                if len(callingMessage) > 3:
                    if callingMessage[3] == 'people' or callingMessage[3] == 'members':
                        # /hola [circles, circle] [circleId] [people, members]
                        code, message = getCircleMembers(circleId)
                        message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
                    else:
                        # /hola [circles, circle] [circleId] something
                        message = "Sorry, the feature \'"+callingMessage[3]+"\' does not exist (yet). Type /hola circle "+circleId+" to get a list of the available commands."
                        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
                else:
                    # /hola [circles, circle] [circleId]
                    message = helpInformationCircle(circleId)
                    message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
            else:
                # /hola [circles, circle]
                code, message = getCircles()
                message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
        else:
            # /hola something
            message = "Sorry, the feature \'"+callingMessage[1]+"\' does not exist (yet). Type /hola to get a list of the available commands."
            message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    return json.jsonify(message_dict)


@app.route('/configure.html', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(
                                    glassfrogToken=request.form['glassfrogtoken'])
        code, message = getCircles()
        if code == 200:
            flashmessage = 'Valid Glassfrog Token stored'
            hipchatApiHandler = apiCalls.HipchatApiHandler()
            hipchatApiHandler.sendMessage(
                        color=strings.succes_color,
                        message="Configured successfully. Type /hola to get started!",
                        hipchatApiSettings=app.hipchatApiSettings)
        else:
            flashmessage = 'Encountered Error '+str(code)+' when testing the Glassfrog Token.'
            flashmessage = flashmessage + ' Message given: \''+message+'\'.'
        flash(flashmessage)

    glassfrogToken = ''
    if app.glassfrogApiSettings is not None:
        glassfrogToken = app.glassfrogApiSettings.glassfrogToken
    return render_template('configure.html', glassfrogtoken=glassfrogToken)

if __name__ == '__main__':
    app.run()
