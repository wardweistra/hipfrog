import os
import glassfrog
import unittest

from flask import url_for, request, json


class GlassfrogTestCase(unittest.TestCase):

    def setUp(self):
        glassfrog.app.config['TESTING'] = True
        self.app = glassfrog.app.test_client()

    # def tearDown(self):

    def test_home(self):
        rv = self.app.get('/', follow_redirects=True)
        assert b'Install Glassfrog HipChat Integration' in rv.data

    def test_capabilities(self):
        # Get capabilities.json
        pass

    def test_installed(self):
        installdata = {
            "oauthId": "f3100c47-9936-40e8-a8aa-798b1e8da8f0",
            "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
            "roomId": 2589171,
            "groupId": 46617,
            "oauthSecret": "Jgtf1Baj5KrSpXHZ7LbB0H3Krwr6cotrkQgkJm9C"}
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
