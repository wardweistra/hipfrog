#!/usr/bin/env python3
from flask import Flask, json
app = Flask(__name__)

myserver = "http://5.157.82.115:45277"


@app.route('/')
def hello_world():
    return 'Hello World!'


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
                        "send_notification"
                    ]
                },
                "installable": {
                    "allowGlobal": False,
                    "allowRoom": True,
                    "callbackUrl": myserver+"/installed"
                }
            }
        }
    return json.jsonify(capabilities_dict)


@app.route('/installed')
def installed():
    return ('', 200)

if __name__ == '__main__':
    app.run()
