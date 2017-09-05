#!/usr/bin/env python3
from flask import Flask, json, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import re

from .functions import apiCalls
from .functions import messageFunctions as messageFunctions
from .strings import *
from .models import *
from .settings import config

app = Flask(__name__)
app.config.from_object(config)
app.config.from_envvar('HIPFROG_SETTINGS', silent=True)
db.init_app(app)


@app.route('/')
def home():
    return ('<a target="_blank" href="https://www.hipchat.com/addons/install?url=' +
            app.config['PUBLIC_URL'] + '/capabilities.json">' +
            strings.install_message + '</a>')


@app.route('/capabilities.json')
def capabilities():
    capabilities_dict = apiCalls.getCapabilitiesDict(app.config['PUBLIC_URL'])
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
                     "scope": "send_notification view_room"}
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
    # TODO why are they not uninstalled?
    return ('', 200)


def getCircles(glassfrogToken):
    apiEndpoint = 'circles'
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                              glassfrogToken)

    if code == 200:
        message = 'The following circles are in your organization:<br /><ul>'

        def getSubCircles(circleId):
            sub_circle_hierarchy = {}
            for supported_role in responsebody['linked']['supported_roles']:
                if supported_role['links']['circle'] == circleId:
                    sub_circleId = supported_role['links']['supporting_circle']
                    sub_circle_hierarchy[sub_circleId] = getSubCircles(sub_circleId)
            return sub_circle_hierarchy

        circle_hierarchy = {}

        for supported_role in responsebody['linked']['supported_roles']:
            if supported_role['links']['circle'] is None:
                sub_circleId = supported_role['links']['supporting_circle']
                circle_hierarchy[sub_circleId] = getSubCircles(sub_circleId)

        def getCircleWithId(circleId):
            for circle in responsebody['circles']:
                if circle['id'] == circleId:
                    return circle

        def getCircleMessage(circle_hierarchy):
            message = ''
            for circleId in circle_hierarchy:
                circle = getCircleWithId(circleId)
                message += ('<li><a href="https://app.glassfrog.com/circles/{0}">{1}</a>'
                            ).format(str(circle['id']), circle['name'])
                if circle_hierarchy[circleId] != {}:
                    message += '<ul>'
                    message += getCircleMessage(circle_hierarchy[circleId])
                    message += '</ul>'
                message += '</li>'
            return message

        message += '</ul>'

        message += getCircleMessage(circle_hierarchy)
        message += strings.help_hipfrog_circle
    else:
        message = responsebody['message']

    return code, message


def getIdForCircleIdentifier(glassfrogToken, circleIdentifier):
    def getCircleIdFromName(glassfrogToken, circleIdentifier):
        apiEndpoint = 'circles'
        glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
        code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                                  glassfrogToken)
        message = ''
        success = True

        if code == 200:
            circleId = messageFunctions.getMatchingCircle(
                responsebody['circles'], circleIdentifier)
            if circleId == -999:  # no match
                message = no_circle_matched.format(circleIdentifier)
                success = False
        else:
            message = responsebody['message']
            circleId = -999
            success = False
        return success, circleId, message

    message = ''
    success = True

    try:
        int(circleIdentifier)
        circleId = circleIdentifier
    except ValueError:
        success, circleId, message = getCircleIdFromName(glassfrogToken, circleIdentifier)

    return success, circleId, message


def getIdForRoleIdentifier(glassfrogToken, roleIdentifier):
    def getRoleIdFromName(glassfrogToken, roleIdentifier, circleIdentifier=None):
        message = ''
        success = True

        if circleIdentifier:
            success, circleId, message = getIdForCircleIdentifier(glassfrogToken, circleIdentifier)
            if not success:
                return success, -999, message
            else:
                apiEndpoint = 'circles/{}/roles'.format(circleId)
        else:
            apiEndpoint = 'roles'

        glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
        code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                                  glassfrogToken)

        if code == 200:
            roleId = messageFunctions.getMatchingRole(responsebody['roles'], roleIdentifier)
            if roleId == -999:  # no match
                message = no_role_matched.format(roleIdentifier)
                success = False
        else:
            message = responsebody['message']
            roleId = -999
            success = False
        return success, roleId, message

    message = ''
    success = True

    roleIdentifier = roleIdentifier.strip(':/\\\'\"')

    try:
        int(roleIdentifier)
        roleId = roleIdentifier
    except ValueError:
        roleIdentifierParts = roleIdentifier.split(':')
        roleIdentifierRole = roleIdentifier
        roleIdentifierCircle = None

        if len(roleIdentifierParts) > 1:
            if (roleIdentifierParts[0] != '' and roleIdentifierParts[1] != ''):
                roleIdentifierCircle = roleIdentifierParts[0]
                roleIdentifierRole = roleIdentifierParts[1]

        success, roleId, message = getRoleIdFromName(
            glassfrogToken, roleIdentifierRole, roleIdentifierCircle)

    return success, roleId, message


def getCircleCircleId(glassfrogToken, circleId):
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.getCircleForCircleId(
        circleId, glassfrogToken)

    if code == 200:
        message_list = []
        # Title with circle name
        message_list += [('<strong><a href="https://app.glassfrog.com/circles/{}">Circle -'
                          ' {}</a></strong><br/>').format(
                          circleId, responsebody['circles'][0]['name'])]
        # Purpose
        if responsebody['linked']['supported_roles'][0]['purpose'] is not None:
            message_list += ['<strong>Purpose:</strong> {}'.format(
                responsebody['linked']['supported_roles'][0]['purpose'])]
        # Strategy
        if responsebody['circles'][0]['strategy'] is not None:
            message_list += ['<strong>Strategy:</strong> {}'.format(
                responsebody['circles'][0]['strategy'])]
        # Domains
        if responsebody['linked']['domains'] != []:
            if len(responsebody['linked']['domains']) > 1:
                domains = '<strong>Domains:</strong>'
            else:
                domains = '<strong>Domain:</strong>'
            domain_list = []
            for domain in responsebody['linked']['domains']:
                domain_list += ['{}'.format(domain['description'])]
            domains += ' ' + ', '.join(domain_list)
            message_list += [domains]
        # Parent circle
        # TODO add circle name
        if responsebody['linked']['supported_roles'][0]['links']['circle'] is not None:
            message_list += [('<strong><a href="https://app.glassfrog.com/circles/{}">'
                              'Parent circle</a></strong>').format(
                responsebody['linked']['supported_roles'][0]['links']['circle'])]
        # Follow up links
        message_list += [strings.help_hipfrog_circle_circleid.format(
            messageFunctions.makeMentionName(responsebody['circles'][0]['name']))]
        # Joining with new lines
        message = '<br/>'.join(message_list)
    else:
        message = responsebody['message']

    return code, message


def getCircleMembers(glassfrogToken, circleId):
    apiEndpoint = 'circles/{}/people'.format(circleId)
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                              glassfrogToken)

    if code == 200:
        message = 'The following people are in this circle:<br /><ul>'

        for person in sorted(responsebody['people'], key=lambda k: k['name']):
            message += ('<li>'
                        '<a href="https://app.glassfrog.com/people/{0}">{1}</a>'
                        '</li>').format(str(person['id']), person['name'])
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

        subcircles = []
        roles = []
        message = ""

        for role in sorted(responsebody['roles'], key=lambda k: k['name']):
            if role['links']['supporting_circle'] is not None:
                subcircles += [role]
            else:
                roles += [role]

        if subcircles != []:
            message += '<strong>Subcircles:</strong><br /><ul>'
            for subcircle in subcircles:
                message += '<li>'
                message += ('<a href="https://app.glassfrog.com/roles/{0}">{1}</a>'
                            ).format(str(subcircle['id']), subcircle['name'])
                message += '</li>'
            message += '</ul>'

        if roles != []:
            message += '<strong>Roles:</strong><br /><ul>'
            for role in roles:
                message += '<li>'
                message += ('<a href="https://app.glassfrog.com/roles/{0}">{1}</a>'
                            ).format(str(role['id']), role['name'])
                message += '</li>'
            message += '</ul>'

        message += help_hipfrog_circle_circleid_roles
    else:
        message = responsebody['message']

    return code, message


def getRoleRoleId(glassfrogToken, roleId):
    apiEndpoint = 'roles/{}'.format(roleId)
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
    code, responsebody = glassfrogApiHandler.glassfrogApiCall(apiEndpoint,
                                                              glassfrogToken)

    if code == 200:
        message_list = []
        # Title with role name
        message_list += [('<strong><a href="https://app.glassfrog.com/roles/{}">Role -'
                          ' {}</a></strong><br/>').format(
                          roleId, responsebody['roles'][0]['name'])]
        # Purpose
        if responsebody['roles'][0]['purpose'] is not None:
            message_list += ['<strong>Purpose:</strong> {}'.format(
                responsebody['roles'][0]['purpose'])]
        # Domains
        if responsebody['linked']['domains'] != []:
            if len(responsebody['linked']['domains']) > 1:
                domains = '<strong>Domains:</strong>'
            else:
                domains = '<strong>Domain:</strong>'
            domain_list = []
            for domain in responsebody['linked']['domains']:
                domain_list += ['{}'.format(domain['description'])]
            domains += ' ' + ', '.join(domain_list)
            message_list += [domains]
        # Circle
        if responsebody['linked']['circles'] != []:
            message_list += [('<strong>Circle:</strong> '
                              '<a href="https://app.glassfrog.com/circles/{0}">{1}</a>').format(
                responsebody['linked']['circles'][0]['id'],
                responsebody['linked']['circles'][0]['name'])]
        # Accountabilities
        if responsebody['linked']['accountabilities'] != []:
            if len(responsebody['linked']['accountabilities']) > 1:
                accountabilities = '<strong>Accountabilities:</strong><ul>'
            else:
                accountabilities = '<strong>Accountability:</strong> '
            for accountability in responsebody['linked']['accountabilities']:
                if len(responsebody['linked']['accountabilities']) > 1:
                    accountabilities += '<li>'
                accountabilities += '{}'.format(accountability['description'])
                if len(responsebody['linked']['accountabilities']) > 1:
                    accountabilities += '</li>'
            if len(responsebody['linked']['accountabilities']) > 1:
                accountabilities += '</ul>'
            message_list += [accountabilities]
        # People
        if responsebody['linked']['people'] != []:
            if len(responsebody['linked']['people']) > 1:
                people = '<strong>People:</strong><ul>'
            else:
                people = '<strong>Person: </strong>'
            for person in responsebody['linked']['people']:
                if len(responsebody['linked']['people']) > 1:
                    people += '<li>'
                people += ('<a href="https://app.glassfrog.com/people/{0}">{1}</a>'
                           ).format(str(person['id']), person['name'])
                if len(responsebody['linked']['people']) > 1:
                    people += '</li>'
            if len(responsebody['linked']['people']) > 1:
                people += '</ul>'
            message_list += [people]
        message_list += [help_hipfrog_role_roleid.format(
                messageFunctions.makeMentionName(responsebody['linked']['circles'][0]['name']),
                messageFunctions.makeMentionName(responsebody['roles'][0]['name'])
            )]
        # Joining with new lines
        message = '<br/>'.join(message_list)
    else:
        message = responsebody['message']

    return code, message


@app.route('/hipfrog', methods=['GET', 'POST'])
def hipfrog():
    requestdata = json.loads(request.get_data())
    callingMessage = requestdata['item']['message']['message'].lower().split()
    oauthId = requestdata['oauth_client_id']
    installation = messageFunctions.getInstallationFromOauthId(oauthId)

    if installation.glassfrogToken is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    elif len(callingMessage) == 1:
        message = strings.help_hipfrog
        message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
    elif len(callingMessage) > 1:
        # /hipfrog something
        message = strings.missing_functionality.format(callingMessage[1])
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    # TODO Generate message_dict and color here
    return json.jsonify(message_dict)


def getMentionsForRole(installation, roleId):
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()

    # get role details
    apiEndpoint = 'roles/{}'.format(roleId)
    code, role_responsebody = glassfrogApiHandler.glassfrogApiCall(
        apiEndpoint, installation.glassfrogToken)
    if code != 200:
        message = role_responsebody['message']
        return code, message

    role_names = []

    message = "{} in {}: ".format(
        role_responsebody['roles'][0]['name'], role_responsebody['linked']['circles'][0]['name'])

    if role_responsebody['linked']['people'] != []:
        # Get names of people in role
        for person in role_responsebody['linked']['people']:
            role_names += [person['name']]
        # Get names of people in room
        hipchatApiHandler = apiCalls.HipchatApiHandler()
        room_code, room_members = hipchatApiHandler.getRoomMembers(installation=installation)

        mention_list = []

        for role_name in role_names:
            inroom = False
            for room_member in room_members['items']:
                if room_member['name'] == role_name:
                    mention_list += ['@'+room_member['mention_name']]
                    inroom = True
                    break
            if not inroom:
                mention_list += [role_name]

        message += ", ".join(mention_list)
    else:
        message += "(not fullfilled)"

    return code, message


def getMentionsForCircle(installation, circleId):
    glassfrogApiHandler = apiCalls.GlassfrogApiHandler()

    # Get circle details
    code, circle_responsebody = glassfrogApiHandler.getCircleForCircleId(
        circleId, installation.glassfrogToken)
    if code != 200:
        message = circle_responsebody['message']
        return code, message

    # Get circle members
    apiEndpoint = 'circles/{}/people'.format(circleId)
    code, members_responsebody = glassfrogApiHandler.glassfrogApiCall(
        apiEndpoint, installation.glassfrogToken)
    if code != 200:
        message = members_responsebody['message']
        return code, message

    circle_names = []

    message = "{}: ".format(circle_responsebody['circles'][0]['name'])

    if members_responsebody['people'] != []:
        # Get names of people in circle
        for person in members_responsebody['people']:
            circle_names += [person['name']]
        # Get names of people in room
        hipchatApiHandler = apiCalls.HipchatApiHandler()
        room_code, room_members = hipchatApiHandler.getRoomMembers(installation=installation)

        mention_list = []

        for circle_name in circle_names:
            inroom = False
            for room_member in room_members['items']:
                if room_member['name'] == circle_name:
                    mention_list += ['@'+room_member['mention_name']]
                    inroom = True
                    break
            if not inroom:
                mention_list += [circle_name]

        message += ", ".join(mention_list)
    else:
        message += "(not fullfilled)"

    return code, message


@app.route('/atrole', methods=['GET', 'POST'])
def atRole():
    requestdata = json.loads(request.get_data())
    callingMessage = requestdata['item']['message']['message']
    oauthId = requestdata['oauth_client_id']
    installation = messageFunctions.getInstallationFromOauthId(oauthId)

    message_format = 'html'

    if installation.glassfrogToken is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    else:
        try:
            roleIdentifier = re.search(strings.regex_at_role_roleId, callingMessage).group(1)
            # Convert roleIdentifier to roleId if needed
            success, roleId, message = getIdForRoleIdentifier(
                installation.glassfrogToken, roleIdentifier)
            if not success:
                code = 404
            else:
                code, mentions = getMentionsForRole(installation, roleId)
                from_mention = requestdata['item']['message']['from']['mention_name']
                message = '@'+from_mention+' said: '+callingMessage+' /cc '+mentions
                message_format = "text"
        except AttributeError:
            code = 404
            message = ("Please specify a role name after @role.")

        color = strings.succes_color if code == 200 else strings.error_color
        message_dict = messageFunctions.createMessageDict(color, message, message_format)
    return json.jsonify(message_dict)


@app.route('/atcircle', methods=['GET', 'POST'])
def atCircle():
    requestdata = json.loads(request.get_data())
    callingMessage = requestdata['item']['message']['message']
    oauthId = requestdata['oauth_client_id']
    installation = messageFunctions.getInstallationFromOauthId(oauthId)

    message_format = 'html'

    if installation.glassfrogToken is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    else:
        try:
            circleIdentifier = re.search(strings.regex_at_circle_circleId, callingMessage).group(1)
            # Convert circleIdentifier to circleId if needed
            success, circleId, message = getIdForCircleIdentifier(
                installation.glassfrogToken, circleIdentifier)
            if not success:
                code = 404
            else:
                code, mentions = getMentionsForCircle(installation, circleId)
                from_mention = requestdata['item']['message']['from']['mention_name']
                message = '@'+from_mention+' said: '+callingMessage+' /cc '+mentions
                message_format = "text"
        except AttributeError:
            code = 404
            message = ("Please specify a circle name after @circle.")

        color = strings.succes_color if code == 200 else strings.error_color
        message_dict = messageFunctions.createMessageDict(color, message, message_format)
    return json.jsonify(message_dict)


@app.route('/slashcircle', methods=['GET', 'POST'])
def slashCircle():
    requestdata = json.loads(request.get_data())
    callingMessage = requestdata['item']['message']['message'].lower().split()
    oauthId = requestdata['oauth_client_id']
    installation = messageFunctions.getInstallationFromOauthId(oauthId)

    if installation.glassfrogToken is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    elif len(callingMessage) > 1:
        circleIdentifier = callingMessage[1]
        # Convert circleIdentifier to circleId if needed
        success, circleId, message = getIdForCircleIdentifier(
            installation.glassfrogToken, circleIdentifier)
        if not success:
            message_dict = messageFunctions.createMessageDict(strings.error_color, message)
        else:
            if len(callingMessage) > 2:
                if callingMessage[2] == 'people' or callingMessage[2] == 'members':
                    # /[circles, circle] [circleId] [people, members]
                    code, message = getCircleMembers(installation.glassfrogToken, circleId)
                    color = strings.succes_color if code == 200 else strings.error_color
                    message_dict = messageFunctions.createMessageDict(color,
                                                                      message)
                elif callingMessage[2] == 'roles':
                    # /[circles, circle] [circleId] roles
                    code, message = getCircleRoles(installation.glassfrogToken, circleId)
                    color = strings.succes_color if code == 200 else strings.error_color
                    message_dict = messageFunctions.createMessageDict(color,
                                                                      message)
                else:
                    # /[circles, circle] [circleId] something
                    message = strings.circles_missing_functionality.format(
                        callingMessage[2], circleId)
                    message_dict = messageFunctions.createMessageDict(strings.error_color,
                                                                      message)
            else:
                # /[circles, circle] [circleId]
                code, message = getCircleCircleId(installation.glassfrogToken, circleId)
                color = strings.succes_color if code == 200 else strings.error_color
                message_dict = messageFunctions.createMessageDict(color, message)
    else:
        # /[circles, circle]
        code, message = getCircles(installation.glassfrogToken)
        message_dict = messageFunctions.createMessageDict(strings.succes_color, message)

    return json.jsonify(message_dict)


@app.route('/slashrole', methods=['GET', 'POST'])
def slashRole():
    requestdata = json.loads(request.get_data())
    callingMessage = requestdata['item']['message']['message'].lower().split()
    oauthId = requestdata['oauth_client_id']
    installation = messageFunctions.getInstallationFromOauthId(oauthId)

    if installation.glassfrogToken is None:
        message = strings.set_token_first
        message_dict = messageFunctions.createMessageDict(strings.error_color, message)
    elif len(callingMessage) > 1:
        roleIdentifier = callingMessage[1]
        # Convert roleIdentifier to roleId if needed
        success, roleId, message = getIdForRoleIdentifier(
            installation.glassfrogToken, roleIdentifier)
        if not success:
            message_dict = messageFunctions.createMessageDict(strings.error_color, message)
        else:
            # /[roles, role] [roleId]
            code, message = getRoleRoleId(installation.glassfrogToken, roleId)
            color = strings.succes_color if code == 200 else strings.error_color
            message_dict = messageFunctions.createMessageDict(color, message)
    else:
        # TODO give help message for /role
        # /[roles, role]
        # code, message = getRoles(installation.glassfrogToken)
        # message_dict = messageFunctions.createMessageDict(strings.succes_color, message)
        pass

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
