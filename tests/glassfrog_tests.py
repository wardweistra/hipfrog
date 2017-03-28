#!/usr/bin/env python3
import os
import unittest
import time
import jwt
from unittest import mock
from flask import url_for, request, json, jsonify, escape

import glassfrog
from glassfrog.functions import apiCalls
from glassfrog.functions import messageFunctions as messageFunctions
from glassfrog import strings
from glassfrog.models import *
from glassfrog import db

import test_values


class GlassfrogTestCase(unittest.TestCase):

    def setUp(self):
        glassfrog.app.config['TESTING'] = True
        glassfrog.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///glassfrog_hipchat_test'

        self.app = glassfrog.app.test_client()
        db.init_app(glassfrog.app)
        with glassfrog.app.app_context():
            db.create_all()

    def tearDown(self):
        with glassfrog.app.app_context():
            db.drop_all()

    def defaultInstallation(self, set_glassfrogToken=True):
        installation = Installation(
            oauthId=test_values.mock_installdata['oauthId'],
            capabilitiesUrl=test_values.mock_installdata['capabilitiesUrl'],
            roomId=test_values.mock_installdata['roomId'],
            groupId=test_values.mock_installdata['groupId'],
            oauthSecret=test_values.mock_installdata['oauthSecret'])
        installation.access_token = test_values.mock_tokenData['access_token']
        installation.expires_in = test_values.mock_tokenData['expires_in']
        installation.group_id = test_values.mock_tokenData['group_id']
        installation.group_name = test_values.mock_tokenData['group_name']
        installation.scope = test_values.mock_tokenData['scope']
        installation.token_type = test_values.mock_tokenData['token_type']
        installation.hipchatApiProvider_url = \
            test_values.mock_capabilitiesData['capabilities']['hipchatApiProvider']['url']
        if set_glassfrogToken:
            installation.glassfrogToken = test_values.mock_glassfrogToken
        return installation

    def addInstallation(self, installation=None):
        if installation is None:
            installation = self.defaultInstallation(set_glassfrogToken=False)
        with glassfrog.app.app_context():
            db.session.add(installation)
            db.session.commit()
            db_installation = Installation.query.filter_by(oauthId=installation.oauthId).first()
        assert db_installation is not None

        return installation

    def test_home(self):
        rv = self.app.get('/', follow_redirects=True)
        assert strings.install_message in rv.data.decode('utf-8')

    def test_capabilities(self):
        mock_capabilitiesDict = apiCalls.getCapabilitiesDict(glassfrog.app.config['PUBLIC_URL'])
        rv = self.app.get('/capabilities.json', follow_redirects=True)
        return_capabilitiesDict = json.loads(rv.get_data())
        assert return_capabilitiesDict == mock_capabilitiesDict

    @mock.patch('glassfrog.apiCalls.HipchatApiHandler')
    def test_installed(self, mock_HipchatApiHandler):
        mock_HipchatApiHandler.return_value.getCapabilitiesData.return_value = \
            test_values.mock_capabilitiesData
        mock_HipchatApiHandler.return_value.getTokenData.return_value = test_values.mock_tokenData
        mock_jsoninstalldata = json.dumps(test_values.mock_installdata)

        mock_installation = self.defaultInstallation(set_glassfrogToken=False)

        with glassfrog.app.app_context():
            db_installation = Installation.query.filter_by(
                oauthId=mock_installation.oauthId).first()
        assert db_installation is None

        rv = self.app.post('/installed', follow_redirects=True, data=mock_jsoninstalldata)

        with glassfrog.app.app_context():
            db_installation = Installation.query.filter_by(
                oauthId=mock_installation.oauthId).first()
        assert db_installation is not None

        mock_HipchatApiHandler.return_value.sendMessage.assert_called_with(
            color=strings.succes_color,
            message=strings.installed_successfully,
            installation=db_installation)

    def test_uninstalled(self):
        installation = self.addInstallation()

        rv = self.app.delete('/installed/{}'.format(installation.oauthId), follow_redirects=True)

        with glassfrog.app.app_context():
            db_installation = Installation.query.filter_by(oauthId=installation.oauthId).first()
        assert db_installation is None
        assert rv.status_code == 200

    @mock.patch('glassfrog.apiCalls.requests.get')
    def test_getRoomMembers(self, mock_requests_get):
        mock_installation = self.defaultInstallation()
        mock_color = strings.succes_color

        hipchatApiHandler = apiCalls.HipchatApiHandler()

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(test_values.mock_room_members_response)
        mock_requests_get.return_value = mock_response

        rv = hipchatApiHandler.getRoomMembers(installation=mock_installation)
        mock_requestUrl = '{}/room/{}/member'.format(mock_installation.hipchatApiProvider_url,
                                                     mock_installation.roomId)
        mock_token_header = {"Authorization": "Bearer "+mock_installation.access_token}

        mock_requests_get.assert_called_with(mock_requestUrl,
                                             headers=mock_token_header)

        assert rv == (mock_response.status_code, test_values.mock_room_members_response)

    @mock.patch('glassfrog.apiCalls.requests')
    def test_sendMessage(self, mock_requests):
        mock_installation = self.defaultInstallation()
        mock_color = strings.succes_color
        mock_message = 'Test!'

        hipchatApiHandler = apiCalls.HipchatApiHandler()
        hipchatApiHandler.sendMessage(
            color=mock_color,
            message=mock_message,
            installation=mock_installation)
        mock_messageUrl = '{}/room/{}/notification'.format(
            mock_installation.hipchatApiProvider_url, mock_installation.roomId)
        mock_token_header = {"Authorization": "Bearer "+mock_installation.access_token}
        mock_data = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_requests.post.assert_called_with(mock_messageUrl,
                                              headers=mock_token_header,
                                              data=mock_data)

    @mock.patch('glassfrog.apiCalls.requests.get')
    def test_glassfrogApiCall(self, mock_requests_get):
        glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
        mock_apiEndpoint = 'circles'

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(test_values.mock_circles_response)
        mock_requests_get.return_value = mock_response

        code, responsebody = glassfrogApiHandler.glassfrogApiCall(mock_apiEndpoint,
                                                                  test_values.mock_glassfrogToken)

        mock_headers = {'X-Auth-Token': test_values.mock_glassfrogToken}
        mock_apiUrl = 'https://glassfrog.holacracy.org/api/v3/'+mock_apiEndpoint
        mock_requests_get.assert_called_with(mock_apiUrl, headers=mock_headers)

    def test_getInstallationFromJWT(self):
        oauthId = test_values.mock_installdata['oauthId']
        oauthSecret = test_values.mock_installdata['oauthSecret']
        installation = Installation(oauthId=oauthId,
                                    capabilitiesUrl=test_values.mock_installdata
                                    ['capabilitiesUrl'],
                                    roomId=test_values.mock_installdata['roomId'],
                                    groupId=test_values.mock_installdata['groupId'],
                                    oauthSecret=oauthSecret)
        self.addInstallation(installation)
        mock_jwt_decoded_data = test_values.mock_jwt_decoded(int(time.time())+1000)
        mock_jwt_encoded = jwt.encode(mock_jwt_decoded_data, oauthSecret, algorithm='HS256')
        with glassfrog.app.app_context():
            installation = messageFunctions.getInstallationFromJWT(mock_jwt_encoded)
        assert installation is not None

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    @mock.patch('glassfrog.apiCalls.HipchatApiHandler')
    @mock.patch('glassfrog.getCircles')
    def test_configure(self, mock_getCircles, mock_HipchatApiHandler, mock_getInstallationFromJWT):
        mock_installation = self.defaultInstallation(set_glassfrogToken=False)
        assert mock_installation.glassfrogToken is None
        mock_getInstallationFromJWT.return_value = mock_installation

        # Loading of page
        rv = self.app.get('/configure.html', follow_redirects=True,
                          query_string=test_values.mock_jwt_data('bogus'))
        assert b'Glassfrog Token' in rv.data

        # Wrong token
        mock_getCircles.return_value = [401, test_values.mock_401_responsebody['message']]
        rv = self.app.post('/configure.html', follow_redirects=True,
                           data=dict(glassfrogtoken=test_values.mock_glassfrogToken),
                           query_string=test_values.mock_jwt_data('bogus'))
        assert mock_getCircles.called
        assert escape(test_values.mock_401_flash_message) in rv.data.decode('utf-8')

        # Right token
        mock_getCircles.return_value = (200, test_values.mock_circles_message)
        rv = self.app.post('/configure.html', follow_redirects=True,
                           data=dict(glassfrogtoken=test_values.mock_glassfrogToken),
                           query_string=test_values.mock_jwt_data('bogus'))
        assert mock_getCircles.called
        assert escape(strings.configured_successfully_flash) in rv.data.decode('utf-8')
        mock_HipchatApiHandler.return_value.sendMessage.assert_called_with(
            color=strings.succes_color,
            message=strings.configured_successfully,
            installation=mock_installation)

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircles(self, mock_glassfrogApiHandler):
        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circles_response)
        rv = glassfrog.getCircles(test_values.mock_glassfrogToken)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called
        for circle in test_values.mock_circles_response['circles']:
            assert circle['name'] in rv[1]
            assert '{}'.format(circle['id']) in rv[1]

        # TODO Failing call

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getIdForCircleIdentifier(self, mock_glassfrogApiHandler):
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circles_response)

        # Test succesful match
        mock_circleIdentifier = "business-development"
        mock_circleId = test_values.mock_circles_response['circles'][2]['id']
        rv = glassfrog.getIdForCircleIdentifier(test_values.mock_glassfrogToken, mock_circleIdentifier)
        assert rv == (True, mock_circleId, '')

        # Test bad match
        mock_circleIdentifier = "banana"
        rv = glassfrog.getIdForCircleIdentifier(test_values.mock_glassfrogToken, mock_circleIdentifier)
        assert rv == (False, -999, strings.no_circle_matched.format(mock_circleIdentifier))

        # Test error
        mock_code = 401
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            mock_code, test_values.mock_401_responsebody)

        mock_circleIdentifier = "banana"
        rv = glassfrog.getIdForCircleIdentifier(test_values.mock_glassfrogToken, mock_circleIdentifier)
        assert rv == (False, -999, test_values.mock_401_responsebody['message'])

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircleCircleId(self, mock_glassfrogApiHandler):
        mock_circleId = test_values.mock_circle_circleId_response['circles'][0]['id']

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circle_circleId_response)
        rv = glassfrog.getCircleCircleId(test_values.mock_glassfrogToken, mock_circleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called

        for circle in test_values.mock_circle_circleId_response['circles']:
            assert circle['name'] in rv[1]
            assert strings.help_hipfrog_circle_circleid.format(circle['id']) in rv[1]
        for supported_role in \
                test_values.mock_circle_circleId_response['linked']['supported_roles']:
            assert supported_role['purpose'] in rv[1]
        for domain in test_values.mock_circle_circleId_response['linked']['domains']:
            assert domain['description'] in rv[1]

        # TODO wrong circleID

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircleMembers(self, mock_glassfrogApiHandler):
        mock_circleId = 1000

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circle_members_response)
        rv = glassfrog.getCircleMembers(test_values.mock_glassfrogToken, mock_circleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called
        for person in test_values.mock_circle_members_response['people']:
            assert person['name'] in rv[1]
            assert '{}'.format(person['id']) in rv[1]

        # TODO wrong circleID

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircleRoles(self, mock_glassfrogApiHandler):
        mock_circleId = 1000

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circle_roles_response)
        rv = glassfrog.getCircleRoles(test_values.mock_glassfrogToken, mock_circleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called
        for role in test_values.mock_circle_roles_response['roles']:
            assert role['name'] in rv[1]
            assert '{}'.format(role['id']) in rv[1]

        # TODO wrong circleID

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getIdForRoleIdentifier(self, mock_glassfrogApiHandler):
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_roles_response)

        # Test succesful match
        mock_roleIdentifier = "fullfil"
        mock_roleId = test_values.mock_roles_response['roles'][0]['id']
        rv = glassfrog.getIdForRoleIdentifier(test_values.mock_glassfrogToken, mock_roleIdentifier)
        assert rv == (True, mock_roleId, '')

        # Test bad match
        mock_roleIdentifier = "banana"
        rv = glassfrog.getIdForRoleIdentifier(test_values.mock_glassfrogToken, mock_roleIdentifier)
        assert rv == (False, -999, strings.no_role_matched.format(mock_roleIdentifier))

        # Test error
        mock_code = 401
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            mock_code, test_values.mock_401_responsebody)

        mock_roleIdentifier = "banana"
        rv = glassfrog.getIdForRoleIdentifier(test_values.mock_glassfrogToken, mock_roleIdentifier)
        assert rv == (False, -999, test_values.mock_401_responsebody['message'])

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getRoleRoleId(self, mock_glassfrogApiHandler):
        mock_roleId = test_values.mock_role_roleid_response['roles'][0]['id']

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_role_roleid_response)
        rv = glassfrog.getRoleRoleId(test_values.mock_glassfrogToken, mock_roleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called

        for role in test_values.mock_role_roleid_response['roles']:
            assert role['name'] in rv[1]
            assert role['purpose'] in rv[1]
        for circle in test_values.mock_role_roleid_response['linked']['circles']:
            assert circle['name'] in rv[1]
        for accountability in test_values.mock_role_roleid_response['linked']['accountabilities']:
            assert accountability['description'] in rv[1]
        for person in test_values.mock_role_roleid_response['linked']['people']:
            assert person['name'] in rv[1]
        for domain in test_values.mock_role_roleid_response['linked']['domains']:
            assert domain['description'] in rv[1]

        # TODO wrong circleID

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    def test_hipfrog_no_glassfrog_token(self, mock_getInstallationFromOauthId):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hipfrog'))

        mock_color = strings.error_color
        mock_message = strings.set_token_first
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_installation.glassfrogToken = None
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())
        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    def test_hipfrog(self, mock_getInstallationFromOauthId):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hipfrog'))

        mock_color = strings.succes_color
        mock_message = strings.help_hipfrog
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getCircles')
    def test_hipfrog_circles(self, mock_getCircles, mock_getInstallationFromOauthId):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hipfrog circles'))

        mock_color = strings.succes_color
        mock_message = test_values.mock_circles_message
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getCircles.return_value = (200, test_values.mock_circles_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    def test_hipfrog_missing_functionality(self, mock_getInstallationFromOauthId):
        mock_missing_functionality = 'something'
        mock_command = message = '/hipfrog {}'.format(mock_missing_functionality)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.error_color
        mock_message = strings.missing_functionality.format(mock_missing_functionality)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getCircleCircleId')
    def test_hipfrog_circle_circleId(self, mock_getCircleCircleId,
                                     mock_getInstallationFromOauthId):
        mock_circleId = 1000
        mock_command = '/hipfrog circle {}'.format(mock_circleId)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.succes_color
        mock_message = test_values.mock_circle_circleId_message.format(mock_circleId)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getCircleCircleId.return_value = (
            200, test_values.mock_circle_circleId_message.format(mock_circleId))

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getCircleCircleId')
    @mock.patch('glassfrog.getIdForCircleIdentifier')
    def test_hipfrog_circle_circleId_string(self, mock_getIdForCircleIdentifier,
                                            mock_getCircleCircleId,
                                            mock_getInstallationFromOauthId):
        mock_circleId = 1000
        mock_circleIdentier = 'sales'
        mock_command = '/hipfrog circle {}'.format(mock_circleIdentier)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        # Error code in retrieving circleId
        mock_code = 401
        mock_message = test_values.mock_401_responsebody['message']
        mock_messageDict = messageFunctions.createMessageDict(
            strings.error_color, mock_message)

        mock_getCircleCircleId.return_value = (
            200, test_values.mock_circle_circleId_message.format(mock_circleId))
        mock_getIdForCircleIdentifier.return_value = (False, -999, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getCircleMembers')
    def test_hipfrog_circle_members(self, mock_getCircleMembers, mock_getInstallationFromOauthId):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hipfrog circle 1000 members'))

        mock_color = strings.succes_color
        mock_message = test_values.mock_circle_members_message
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getCircleMembers.return_value = (200, test_values.mock_circle_members_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getCircleRoles')
    def test_hipfrog_circle_roles(self, mock_getCircleRoles, mock_getInstallationFromOauthId):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hipfrog circle 1000 roles'))

        mock_color = strings.succes_color
        mock_message = test_values.mock_circle_roles_message
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getCircleRoles.return_value = (200, test_values.mock_circle_roles_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    def test_hipfrog_circle_missing_functionality(self, mock_getInstallationFromOauthId):
        mock_circleId = test_values.mock_circle_circleId_response['circles'][0]['id']
        mock_missing_functionality = 'something'
        mock_command = message = '/hipfrog circle {} {}'.format(mock_circleId,
                                                                mock_missing_functionality)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.error_color
        mock_message = strings.circles_missing_functionality.format(mock_missing_functionality,
                                                                    mock_circleId)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getRoleRoleId')
    def test_hipfrog_role_roleId(self, mock_getRoleRoleId,
                                 mock_getInstallationFromOauthId):
        mock_roleId = 1000
        mock_command = message = '/hipfrog role {}'.format(mock_roleId)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.succes_color
        mock_message = test_values.mock_role_roleId_message.format(mock_roleId)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getRoleRoleId.return_value = (
            200, test_values.mock_role_roleId_message.format(mock_roleId))

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getRoleRoleId')
    @mock.patch('glassfrog.getIdForRoleIdentifier')
    def test_hipfrog_role_roleId_string(self, mock_getIdForRoleIdentifier,
                                        mock_getRoleRoleId,
                                        mock_getInstallationFromOauthId):
            mock_roleId = 1000
            mock_roleIdentier = 'secretary'
            mock_command = '/hipfrog role {}'.format(mock_roleIdentier)
            mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

            # Error code in retrieving roleId
            mock_code = 401
            mock_message = test_values.mock_401_responsebody['message']
            mock_messageDict = messageFunctions.createMessageDict(
                strings.error_color, mock_message)

            mock_getRoleRoleId.return_value = (
                200, test_values.mock_role_roleId_message.format(mock_roleId))
            mock_getIdForRoleIdentifier.return_value = (False, -999, mock_message)

            mock_headers = test_values.mock_authorization_headers()
            mock_installation = self.defaultInstallation()
            mock_getInstallationFromOauthId.return_value = mock_installation

            rv = self.app.post('/hipfrog', follow_redirects=True, data=mock_messagedata,
                               headers=mock_headers)
            return_messageDict = json.loads(rv.get_data())

            assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    @mock.patch('glassfrog.apiCalls.HipchatApiHandler')
    def test_getMentionsForRole(self, mock_HipchatApiHandler, mock_glassfrogApiHandler):
        mock_roleId = test_values.mock_role_roleid_response['roles'][0]['id']
        mock_installation = self.defaultInstallation()
        mock_HipchatApiHandler.return_value.getRoomMembers.return_value = \
            200, test_values.mock_room_members_response

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_role_roleid_response)
        rv = glassfrog.getMentionsForRole(mock_installation, mock_roleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called

        for person in test_values.mock_role_roleid_response['linked']['people']:
            for room_member in test_values.mock_room_members_response['items']:
                if person['name'] == room_member['name']:
                    assert room_member['mention_name'] in rv[1]

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    @mock.patch('glassfrog.apiCalls.HipchatApiHandler')
    def test_getMentionsForCircle(self, mock_HipchatApiHandler, mock_glassfrogApiHandler):
        mock_circleId = 1000
        mock_installation = self.defaultInstallation()
        mock_HipchatApiHandler.return_value.getRoomMembers.return_value = \
            200, test_values.mock_room_members_response

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circle_members_response)
        rv = glassfrog.getMentionsForCircle(mock_installation, mock_circleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called

        for person in test_values.mock_circle_members_response['people']:
            for room_member in test_values.mock_room_members_response['items']:
                if person['name'] == room_member['name']:
                    assert room_member['mention_name'] in rv[1]

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getMentionsForRole')
    def test_atRole(self, mock_getMentionsForRole, mock_getInstallationFromOauthId):
        mock_roleId = test_values.mock_role_roleid_response['roles'][0]['id']
        mock_command = 'Beste @Role {}: Hoi!'.format(mock_roleId)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.succes_color
        mock_message = test_values.mock_atrole_message.format(mock_roleId)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message,
                                                              message_format="text")

        mock_getMentionsForRole.return_value = (
            200, test_values.mock_atrole_mentions.format(mock_roleId))

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/atrole', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getMentionsForCircle')
    def test_atCircle(self, mock_getMentionsForCircle, mock_getInstallationFromOauthId):
        mock_circleId = 1000
        mock_command = 'Beste @Circle {}: Hoi!'.format(mock_circleId)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_message = test_values.mock_atcircle_message.format(
            mock_circleId, mock_circleId)
        mock_messageDict = messageFunctions.createMessageDict(
            strings.succes_color, mock_message, message_format="text")

        mock_getMentionsForCircle.return_value = (
            200, test_values.mock_atcircle_mentions.format(mock_circleId))

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/atcircle', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromOauthId')
    @mock.patch('glassfrog.getMentionsForCircle')
    @mock.patch('glassfrog.getIdForCircleIdentifier')
    def test_atCircle_string(self, mock_getIdForCircleIdentifier,
                             mock_getMentionsForCircle,
                             mock_getInstallationFromOauthId):

        mock_circleId = 1000
        mock_circleIdentier = 'sales'
        mock_command = 'Beste @Circle {}: Hoi!'.format(mock_circleIdentier)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        # Succesful match
        mock_message = test_values.mock_atcircle_message.format(
            mock_circleIdentier, mock_circleId)
        mock_messageDict = messageFunctions.createMessageDict(
            strings.succes_color, mock_message, message_format="text")

        mock_getMentionsForCircle.return_value = (
            200, test_values.mock_atcircle_mentions.format(mock_circleId))
        mock_getIdForCircleIdentifier.return_value = (True, mock_circleId, '')

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/atcircle', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

        # Unsuccesful match
        mock_message = strings.no_circle_matched.format(mock_circleIdentier)
        mock_messageDict = messageFunctions.createMessageDict(
            strings.error_color, mock_message)

        mock_getMentionsForCircle.return_value = (
            200, test_values.mock_atcircle_mentions.format(mock_circleId))
        mock_getIdForCircleIdentifier.return_value = (False, -999, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/atcircle', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

        # Error code in retrieving circleId
        mock_code = 401
        mock_message = test_values.mock_401_responsebody['message']
        mock_messageDict = messageFunctions.createMessageDict(
            strings.error_color, mock_message)

        mock_getMentionsForCircle.return_value = (
            401, test_values.mock_401_responsebody)
        mock_getIdForCircleIdentifier.return_value = (False, -999, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromOauthId.return_value = mock_installation

        rv = self.app.post('/atcircle', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

# TODO test_hipfrog_role_roleId_string
# TODO test_atCircle_string
# TODO test_atRole_string

if __name__ == '__main__':
    unittest.main()
