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
        assert b'Install Glassfrog HipChat Integration' in rv.data

    def test_capabilities(self):
        mock_myserver = 'http://localhost:45277'
        mock_capabilitiesDict = apiCalls.getCapabilitiesDict(mock_myserver)

        glassfrog.myserver = mock_myserver
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
        assert rv == (200, test_values.mock_circles_message)

        # TODO Failing call

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircleMembers(self, mock_glassfrogApiHandler):
        mock_circleId = 1000

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (
            200, test_values.mock_circle_members_response)
        rv = glassfrog.getCircleMembers(test_values.mock_glassfrogToken, mock_circleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called
        assert rv == (200, test_values.mock_circle_members_message)

        # TODO wrong circleID

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    def test_hola_no_glassfrog_token(self, mock_getInstallationFromJWT):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola'))

        mock_color = strings.error_color
        mock_message = strings.set_token_first
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_installation.glassfrogToken = None
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())
        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    def test_hola(self, mock_getInstallationFromJWT):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola'))

        mock_color = strings.succes_color
        mock_message = strings.help_information
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    @mock.patch('glassfrog.getCircles')
    def test_hola_circles(self, mock_getCircles, mock_getInstallationFromJWT):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola circles'))

        mock_color = strings.succes_color
        mock_message = test_values.mock_circles_message
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getCircles.return_value = (200, test_values.mock_circles_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    def test_hola_missing_functionality(self, mock_getInstallationFromJWT):
        mock_missing_functionality = 'something'
        mock_command = message = '/hola {}'.format(mock_missing_functionality)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.error_color
        mock_message = strings.missing_functionality.format(mock_missing_functionality)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    def test_hola_circle_circleId(self, mock_getInstallationFromJWT):
        mock_circleId = 1000
        mock_command = message = '/hola circle {}'.format(mock_circleId)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.succes_color
        mock_message = strings.help_circle.format(mock_circleId)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    @mock.patch('glassfrog.getCircleMembers')
    def test_hola_circle_members(self, mock_getCircleMembers, mock_getInstallationFromJWT):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola circle 1000 members'))

        mock_color = strings.succes_color
        mock_message = test_values.mock_circle_members_message
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_getCircleMembers.return_value = (200, test_values.mock_circle_members_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.functions.messageFunctions.getInstallationFromJWT')
    def test_hola_circle_missing_functionality(self, mock_getInstallationFromJWT):
        mock_circleId = 1000
        mock_missing_functionality = 'something'
        mock_command = message = '/hola circle {} {}'.format(mock_circleId,
                                                             mock_missing_functionality)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))

        mock_color = strings.error_color
        mock_message = strings.circles_missing_functionality.format(mock_missing_functionality,
                                                                    mock_circleId)
        mock_messageDict = messageFunctions.createMessageDict(mock_color, mock_message)

        mock_headers = test_values.mock_authorization_headers()
        mock_installation = self.defaultInstallation()
        mock_getInstallationFromJWT.return_value = mock_installation

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata,
                           headers=mock_headers)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

if __name__ == '__main__':
    unittest.main()
