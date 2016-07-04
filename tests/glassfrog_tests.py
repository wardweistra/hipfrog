import os
import unittest
from unittest import mock
# import tempfile
from flask import url_for, request, json, jsonify

import glassfrog
from glassfrog.functions import apiCalls

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
        # Get capabilities.json
        pass

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
            color='green',
            message='Installed successfully. Please set Glassfrog Token in the Hipchat Integration Configure page.',
            hipchatApiSettings=mock_hipchatApiSettings)
        pass

    def test_configure(self):
        # Set right glassfrogtoken
        # Set wrong glassfrogtoken
        pass

    def test_hola(self):
        mock_messagedata = test_values.mock_messagedata
        # Send hola message
        # Assert message back
        pass

    def test_hola_circles(self):
        # Send '/hola circles' message
        # Intercept circles call to glassfrog
        # Assert circles data
        pass

    def test_uninstalled(self):
        # Send uninstall call
        # Test removed related data
        pass

if __name__ == '__main__':
    unittest.main()
