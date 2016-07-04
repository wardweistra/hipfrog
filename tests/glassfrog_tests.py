import os
import glassfrog
import unittest
from unittest import mock
# import tempfile

from flask import url_for, request, json, jsonify


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
        mock_capabilitiesData = {'description': 'Group chat and IM built for teams', 'name': 'HipChat', 'capabilities': {'hipchatApiProvider': {'availableScopes': {'view_room': {'description': 'View room information and participants, but not history', 'id': 'view_room', 'name': 'View Room'}, 'import_data': {'description': 'Import users, rooms, and chat history. Only available for select add-ons.', 'id': 'import_data', 'name': 'Import Data'}, 'view_messages': {'description': 'View messages from chat rooms and private chats you have access to', 'id': 'view_messages', 'name': 'View Messages'}, 'send_notification': {'description': 'Send room notifications', 'id': 'send_notification', 'name': 'Send Notification'}, 'admin_group': {'description': "Perform group administrative tasks. Note that this scope is restricted from updating the group owner's profile.", 'id': 'admin_group', 'name': 'Administer Group'}, 'view_group': {'description': 'View users, rooms, and other group information', 'id': 'view_group', 'name': 'View Group'}, 'admin_room': {'description': 'Perform room administrative tasks', 'id': 'admin_room', 'name': 'Administer Room'}, 'manage_rooms': {'description': 'Create, update, and remove rooms', 'id': 'manage_rooms', 'name': 'Manage Rooms'}, 'send_message': {'description': 'Send private one-on-one messages', 'id': 'send_message', 'name': 'Send Message'}}, 'url': 'https://api.hipchat.com/v2/'}, 'oauth2Provider': {'authorizationUrl': 'https://www.hipchat.com/users/authorize', 'tokenUrl': 'https://api.hipchat.com/v2/oauth/token'}}, 'links': {'api': 'https://api.hipchat.com/v2', 'homepage': 'https://www.hipchat.com', 'self': 'https://api.hipchat.com/v2/capabilities', 'subdomain': 'https://www.hipchat.com'}, 'connect_server_api_version': 1, 'vendor': {'url': 'http://atlassian.com', 'name': 'Atlassian'}, 'key': 'hipchat'}
        mock_HipchatApiHandler.return_value.getCapabilitiesData.return_value = mock_capabilitiesData
        mock_HipchatApiHandler.return_value.getTokenData.return_value = {'something': 'something else'}

        installdata = {
            "oauthId": "f3100c47-9936-40e8-a8aa-798b1e8da8f0",
            "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
            "roomId": 2589171,
            "groupId": 46617,
            "oauthSecret": "Jgtf1Baj5KrSpXHZ7LbB0H3Krwr6cotrkQgkJm9C"}
        jsoninstalldata = json.dumps(installdata)
        rv = self.app.post('/installed', follow_redirects=True, data=jsoninstalldata)
        # Send install data to /install
        # Intercept call to capabilities
        # Send back capabilities
        # Intercept call to tokenUrl
        # Send back tokendata
        # Receive message back
        pass

    def test_configure(self):
        # Set right glassfrogtoken
        # Set wrong glassfrogtoken
        pass

    def test_hola(self):
        messagedata = {
            "event": "room_message",
            "item": {
                "message": {
                    "date": "2016-05-26T15:32:43.700609+00:00",
                    "from": {
                        "id": 351107,
                        "links": {
                            "self": "https://api.hipchat.com/v2/user/351107"
                            },
                        "mention_name": "WardWeistra",
                        "name": "Ward Weistra",
                        "version": "00000000"
                        },
                    "id": "715f101f-1baa-4a5c-958a-9c6c7efaaa1f",
                    "mentions": [],
                    "message": "/hola",
                    "type": "message"
                    },
                "room": {
                    "id": 2589171,
                    "is_archived": False,
                    "links": {
                        "members": "https://api.hipchat.com/v2/room/2589171/member",
                        "participants": "https://api.hipchat.com/v2/room/2589171/participant",
                        "self": "https://api.hipchat.com/v2/room/2589171",
                        "webhooks": "https://api.hipchat.com/v2/room/2589171/webhook"
                        },
                    "name": "The Hyve - Holacracy",
                    "privacy": "private",
                    "version": "0XLIKALD"
                    }
                },
            "oauth_client_id": "ed8bb9f0-02d8-426b-9226-0d50fdcd47ea",
            "webhook_id": 4965523
            }
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
