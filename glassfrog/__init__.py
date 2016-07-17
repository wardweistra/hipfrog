#!/usr/bin/env python3
from flask import Flask, json, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import requests

from .functions import apiCalls
from .functions import messageFunctions as messageFunctions
from .strings import *
from .models import *
from .settings import config

app = Flask(__name__)
app.config.from_object(config)
app.config.from_envvar('GLASSFROG_HIPCHAT_SETTINGS', silent=True)
db.init_app(app)

# TODO move myserver to settings. Overwrite this and SECRET_KEY on PROD
myserver = "http://5.157.82.115:45277"


@app.route('/')
def hello_world():
    return ('<a target="_blank" href="https://www.hipchat.com/addons/install?url=' +
            myserver+"/capabilities.json"+'">Install Glassfrog HipChat Integration</a>')


@app.route('/capabilities.json')
def capabilities():
    capabilities_dict = apiCalls.getCapabilitiesDict(myserver)
    return json.jsonify(capabilities_dict)


@app.route('/installed', methods=['GET', 'POST'])
def installed():
    if request.method == 'POST':
        installdata = json.loads(request.get_data())

        installation = Installation(oauthId=installdata['oauthId'],
                                    capabilitiesUrl=installdata['capabilitiesUrl'],
                                    roomId=installdata['roomId'],
                                    groupId=installdata['groupId'],
                                    oauthSecret=installdata['oauthSecret'])

        hipchatApiHandler = apiCalls.HipchatApiHandler()

        capabilitiesdata = hipchatApiHandler.getCapabilitiesData(installdata['capabilitiesUrl'])
        tokenUrl = capabilitiesdata['capabilities']['oauth2Provider']['tokenUrl']
        client_auth = requests.auth.HTTPBasicAuth(installation.oauthId, installation.oauthSecret)
        post_data = {"grant_type": "client_credentials",
                     "scope": "send_notification"}
        tokendata = hipchatApiHandler.getTokenData(tokenUrl, client_auth, post_data)

        installation.access_token = tokendata['access_token']
        installation.expires_in = tokendata['expires_in']
        installation.group_id = tokendata['group_id']
        installation.group_name = tokendata['group_name']
        installation.scope = tokendata['scope']
        installation.token_type = tokendata['token_type']
        installation.hipchatApiProvider_url = \
            capabilitiesdata['capabilities']['hipchatApiProvider']['url']

        db.session.add(installation)
        db.session.commit()

        # Pointless query on the installation object to make sure it is still around for testing...
        installation.id

        hipchatApiHandler.sendMessage(
            color=strings.succes_color,
            message=strings.installed_successfully,
            installation=installation)
    return ('', 200)


@app.route('/installed/<oauthId>', methods=['DELETE'])
def uninstall(oauthId):
    installation = Installation.query.filter_by(oauthId=oauthId).first()
    db.session.delete(installation)
    db.session.commit()
    return ('', 200)


def getCircles(glassfrogToken):
    apiEndpoint = 'circles'
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                              glassfrogToken)

    if code == 200:
        message = 'The following circles are in your organization:<br /><ul>'
        for circle in responsebody['circles']:
            message += ('<li><code>/hola circle {}</code>'
                        ' - <a href="https://app.glassfrog.com/circles/{}">{}</a>'
                        '</li>').format(str(circle['id']), str(circle['id']), circle['name'])
        message += '</ul>'
    else:
        message = responsebody['message']

    return code, message


def getCircleMembers(glassfrogToken, circleId):
    apiEndpoint = 'circles/{}/people'.format(circleId)
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                              glassfrogToken)

    if code == 200:
        message = 'The following people are in your circle:<br /><ul>'
        for person in responsebody['people']:
            message += ('<li><code>{}</code>'
                        ' - <a href="https://app.glassfrog.com/people/{}">{}</a>'
                        '</li>').format(str(person['id']), str(person['id']), person['name'])
        message += '</ul>'
    else:
        message = responsebody['message']

    return code, message


def getCircleRoles(glassfrogToken, circleId):
    apiEndpoint = 'circles/{}/roles'.format(circleId)
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                              glassfrogToken)

    if code == 200:
        message = 'The following people are in your circle:<br /><ul>'
        for role in responsebody['roles']:
            message += ('<li><code>{}</code>'
                        ' - <a href="https://app.glassfrog.com/roles/{}">{}</a>'
                        '</li>').format(str(role['id']), str(role['id']), role['name'])
        message += '</ul>'
    else:
        message = responsebody['message']

    return code, message


@app.route('/hola', methods=['GET', 'POST'])
def hola():
    jwt_token = request.headers['Authorization'].split(' ')[1]
    installation = messageFunctions.getInstallationFromJWT(jwt_token)
    requestdata = json.loads(request.get_data())

    callingMessage = requestdata['item']['message']['message'].split()
    if installation.glassfrogToken is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    elif len(callingMessage) == 1:
        message = strings.help_information
        message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
    elif len(callingMessage) > 1:
        if callingMessage[1] == 'circles' or callingMessage[1] == 'circle':
            if len(callingMessage) > 2:
                circleId = callingMessage[2]
                if len(callingMessage) > 3:
                    if callingMessage[3] == 'people' or callingMessage[3] == 'members':
                        # /hola [circles, circle] [circleId] [people, members]
                        code, message = getCircleMembers(installation.glassfrogToken, circleId)
                        message_dict = messageFunctions.createMessageDict(strings.succes_color,
                                                                          message)
                    elif callingMessage[3] == 'roles':
                        # /hola [circles, circle] [circleId] roles
                        code, message = getCircleRoles(installation.glassfrogToken, circleId)
                        message_dict = messageFunctions.createMessageDict(strings.succes_color,
                                                                          message)
                    else:
                        # /hola [circles, circle] [circleId] something
                        message = strings.circles_missing_functionality.format(callingMessage[3],
                                                                               circleId)
                        message_dict = messageFunctions.createMessageDict(strings.error_color,
                                                                          message)
                else:
                    # /hola [circles, circle] [circleId]
                    message = strings.help_circle.format(circleId)
                    message_dict = messageFunctions.createMessageDict(strings.succes_color,
                                                                      message)
            else:
                # /hola [circles, circle]
                code, message = getCircles(installation.glassfrogToken)
                message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
        else:
            # /hola something
            message = strings.missing_functionality.format(callingMessage[1])
            message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    return json.jsonify(message_dict)


@app.route('/configure.html', methods=['GET', 'POST'])
def configure():
    installation = messageFunctions.getInstallationFromJWT(request.args['signed_request'])

    if request.method == 'POST':
        installation.glassfrogToken = request.form['glassfrogtoken']
        db.session.commit()

        code, message = getCircles(installation.glassfrogToken)
        if code == 200:
            flashmessage = strings.configured_successfully_flash
            hipchatApiHandler = apiCalls.HipchatApiHandler()
            hipchatApiHandler.sendMessage(
                        color=strings.succes_color,
                        message=strings.configured_successfully,
                        installation=installation)
        else:
            flashmessage = 'Encountered Error '+str(code)+' when testing the Glassfrog Token.'
            flashmessage = flashmessage + ' Message given: \''+message+'\'.'
        flash(flashmessage)

    glassfrogToken = ''
    if installation.glassfrogToken is not None:
        glassfrogToken = installation.glassfrogToken
    return render_template('configure.html', glassfrogtoken=glassfrogToken)

if __name__ == '__main__':
    app.run()
