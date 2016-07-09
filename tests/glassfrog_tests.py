#!/usr/bin/env python3
import os
import unittest
from unittest import mock
# import tempfile
from flask import url_for, request, json, jsonify, escape

import glassfrog
from glassfrog.functions import apiCalls
from glassfrog.functions.messageFunctions import createMessageDict
from glassfrog import strings

import test_values


class GlassfrogTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, glassfrog.app.config['DATABASE'] = tempfile.mkstemp()
        glassfrog.app.config['TESTING'] = True
        self.app = glassfrog.app.test_client()
        # with glassfrog.app.app_context():
        #     glassfrog.init_db()

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(glassfrog.app.config['DATABASE'])
        pass

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
        mock_HipchatApiHandler.return_value.getCapabilitiesData.return_value = test_values.mock_capabilitiesData
        mock_HipchatApiHandler.return_value.getTokenData.return_value = test_values.mock_tokenData
        mock_jsoninstalldata = json.dumps(test_values.mock_installdata)

        rv = self.app.post('/installed', follow_redirects=True, data=mock_jsoninstalldata)

        mock_hipchatApiSettings = apiCalls.HipchatApiSettings(
                                    hipchatToken=test_values.mock_tokenData['access_token'],
                                    hipchatApiUrl=test_values.mock_capabilitiesData['capabilities']['hipchatApiProvider']['url'],
                                    hipchatRoomId=test_values.mock_installdata['roomId'])
        mock_HipchatApiHandler.return_value.sendMessage.assert_called_with(
            color=strings.succes_color,
            message=strings.installed_successfully,
            hipchatApiSettings=mock_hipchatApiSettings)

    @mock.patch('glassfrog.apiCalls.requests')
    def test_sendMessage(self, mock_requests):
        mock_hipchatToken = 'TtqnpP9GREMNHIOSIYaXqM64hZ3YfQjEelxpLDeT'
        mock_hipchatApiUrl = 'https://api.hipchat.com/v2/'
        mock_hipchatRoomId = 2589171
        mock_color = strings.succes_color
        mock_message = 'Test!'

        hipchatApiHandler = apiCalls.HipchatApiHandler()
        mock_hipchatApiSettings = apiCalls.HipchatApiSettings(
                                    hipchatToken=mock_hipchatToken,
                                    hipchatApiUrl=mock_hipchatApiUrl,
                                    hipchatRoomId=mock_hipchatRoomId)
        hipchatApiHandler.sendMessage(
            color=mock_color,
            message=mock_message,
            hipchatApiSettings=mock_hipchatApiSettings)
        mock_messageUrl = '{}/room/{}/notification'.format(mock_hipchatApiUrl, mock_hipchatRoomId)
        mock_token_header = {"Authorization": "Bearer "+mock_hipchatToken}
        mock_data = createMessageDict(mock_color, mock_message)

        mock_requests.post.assert_called_with(mock_messageUrl,
                                              headers=mock_token_header,
                                              data=mock_data)

    @mock.patch('glassfrog.apiCalls.requests.get')
    def test_glassfrogApiCall(self, mock_requests_get):
        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrogApiHandler = apiCalls.GlassfrogApiHandler()
        mock_glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)
        mock_apiEndpoint = 'circles'

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(test_values.mock_circles_response)
        mock_requests_get.return_value = mock_response

        code, responsebody = glassfrogApiHandler.glassfrogApiCall(mock_apiEndpoint,
                                                                  mock_glassfrogApiSettings)

        mock_headers = {'X-Auth-Token': mock_glassfrogToken}
        mock_apiUrl = 'https://glassfrog.holacracy.org/api/v3/'+mock_apiEndpoint
        mock_requests_get.assert_called_with(mock_apiUrl, headers=mock_headers)

    @mock.patch('glassfrog.apiCalls.HipchatApiHandler')
    @mock.patch('glassfrog.getCircles')
    def test_configure(self, mock_getCircles, mock_HipchatApiHandler):
        mock_hipchatToken = 'TtqnpP9GREMNHIOSIYaXqM64hZ3YfQjEelxpLDeT'
        mock_hipchatApiUrl = 'https://api.hipchat.com/v2/'
        mock_hipchatRoomId = 2589171
        mock_token = 'banana'
        mock_hipchatApiSettings = apiCalls.HipchatApiSettings(
                                    hipchatToken=mock_hipchatToken,
                                    hipchatApiUrl=mock_hipchatApiUrl,
                                    hipchatRoomId=mock_hipchatRoomId)
        glassfrog.app.hipchatApiSettings = mock_hipchatApiSettings

        # Loading of page
        rv = self.app.get('/configure.html', follow_redirects=True)
        assert b'Glassfrog Token' in rv.data

        # Wrong token
        mock_getCircles.return_value = [401, test_values.mock_401_responsebody['message']]
        rv = self.app.post('/configure.html', follow_redirects=True, data=dict(
            glassfrogtoken=mock_token
        ))
        assert mock_getCircles.called
        assert escape(test_values.mock_401_flash_message) in rv.data.decode('utf-8')

        # Right token
        mock_getCircles.return_value = (200, test_values.mock_circles_message)
        rv = self.app.post('/configure.html', follow_redirects=True, data=dict(
            glassfrogtoken=mock_token
        ))
        assert mock_getCircles.called
        assert escape(strings.configured_successfully_flash) in rv.data.decode('utf-8')
        mock_HipchatApiHandler.return_value.sendMessage.assert_called_with(
            color=strings.succes_color,
            message=strings.configured_successfully,
            hipchatApiSettings=mock_hipchatApiSettings)

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircles(self, mock_glassfrogApiHandler):
        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (200, test_values.mock_circles_response)
        rv = glassfrog.getCircles()
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called
        assert rv == (200, test_values.mock_circles_message)

        # TODO Failing call

    @mock.patch('glassfrog.apiCalls.GlassfrogApiHandler')
    def test_getCircleMembers(self, mock_glassfrogApiHandler):
        mock_glassfrogToken = 'myglassfrogtoken'
        mock_circleId = 1000
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        # Succesfull call
        mock_glassfrogApiHandler.return_value.glassfrogApiCall.return_value = (200, test_values.mock_circle_members_response)
        rv = glassfrog.getCircleMembers(mock_circleId)
        assert mock_glassfrogApiHandler.return_value.glassfrogApiCall.called
        assert rv == (200, test_values.mock_circle_members_message)

        # TODO wrong circleID

    def test_hola_no_glassfrog_token(self):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola'))
        mock_color = strings.error_color
        mock_message = strings.set_token_first
        mock_messageDict = createMessageDict(mock_color, mock_message)

        glassfrog.app.glassfrogApiSettings = None

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())
        assert return_messageDict == mock_messageDict

    def test_hola(self):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola'))
        mock_color = strings.succes_color
        mock_message = strings.help_information
        mock_messageDict = createMessageDict(mock_color, mock_message)

        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.getCircles')
    def test_hola_circles(self, mock_getCircles):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola circles'))
        mock_color = strings.succes_color
        mock_message = test_values.mock_circles_message
        mock_messageDict = createMessageDict(mock_color, mock_message)
        mock_getCircles.return_value = (200, test_values.mock_circles_message)

        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    def test_hola_missing_functionality(self):
        mock_missing_functionality = 'something'
        mock_command = message = '/hola {}'.format(mock_missing_functionality)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))
        mock_color = strings.error_color
        mock_message = strings.missing_functionality.format(mock_missing_functionality)
        mock_messageDict = createMessageDict(mock_color, mock_message)

        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    def test_hola_circle_circleId(self):
        mock_circleId = 1000
        mock_command = message = '/hola circle {}'.format(mock_circleId)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))
        mock_color = strings.succes_color
        mock_message = strings.help_circle.format(mock_circleId)
        mock_messageDict = createMessageDict(mock_color, mock_message)

        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    @mock.patch('glassfrog.getCircleMembers')
    def test_hola_circle_members(self, mock_getCircleMembers):
        mock_messagedata = json.dumps(test_values.mock_messagedata('/hola circle 1000 members'))
        mock_color = strings.succes_color
        mock_message = test_values.mock_circle_members_message
        mock_messageDict = createMessageDict(mock_color, mock_message)
        mock_getCircleMembers.return_value = (200, test_values.mock_circle_members_message)

        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    def test_hola_circle_missing_functionality(self):
        mock_circleId = 1000
        mock_missing_functionality = 'something'
        mock_command = message = '/hola circle {} {}'.format(mock_circleId, mock_missing_functionality)
        mock_messagedata = json.dumps(test_values.mock_messagedata(mock_command))
        mock_color = strings.error_color
        mock_message = strings.circles_missing_functionality.format(mock_missing_functionality, mock_circleId)
        mock_messageDict = createMessageDict(mock_color, mock_message)

        mock_glassfrogToken = 'myglassfrogtoken'
        glassfrog.app.glassfrogApiSettings = apiCalls.GlassfrogApiSettings(mock_glassfrogToken)

        rv = self.app.post('/hola', follow_redirects=True, data=mock_messagedata)
        return_messageDict = json.loads(rv.get_data())

        assert return_messageDict == mock_messageDict

    def test_uninstalled(self):
        mock_oauthId = test_values.mock_installdata['oauthId']
        rv = self.app.delete('/installed/{}'.format(mock_oauthId), follow_redirects=True)
        assert rv.status_code == 200

if __name__ == '__main__':
    unittest.main()
