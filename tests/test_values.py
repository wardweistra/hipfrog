mock_installdata = {
    "oauthId": "f3100c47-9936-40e8-a8aa-12314e8da8f0",
    "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
    "roomId": 2589171,
    "groupId": 46617,
    "oauthSecret": "Jgtf1Baj5KrSpXHZ7d7OkH3Krwr6cotspI7kJm9C"}

mock_capabilitiesData = {
    'description': 'Group chat and IM built for teams', 'name': 'HipChat',
    'capabilities': {
        'hipchatApiProvider': {
            'availableScopes': {
                'view_room': {
                   'description': 'View room information and participants, but not history',
                   'id': 'view_room',
                   'name': 'View Room'
                },
                'import_data': {
                    'description': ('Import users, rooms, and chat history.'
                                    ' Only available for select add-ons.'),
                    'id': 'import_data',
                    'name': 'Import Data'
                },
                'view_messages': {
                    'description': ('View messages from chat rooms and private chats'
                                    ' you have access to'),
                    'id': 'view_messages',
                    'name': 'View Messages'
                },
                'send_notification': {
                    'description': 'Send room notifications',
                    'id': 'send_notification',
                    'name': 'Send Notification'
                },
                'admin_group': {
                    'description': ("Perform group administrative tasks. Note that this scope"
                                    " is restricted from updating the group owner's profile."),
                    'id': 'admin_group',
                    'name': 'Administer Group'
                },
                'view_group': {
                    'description': 'View users, rooms, and other group information',
                    'id': 'view_group',
                    'name': 'View Group'
                },
                'admin_room': {
                    'description': 'Perform room administrative tasks',
                    'id': 'admin_room',
                    'name': 'Administer Room'
                },
                'manage_rooms': {
                    'description': 'Create, update, and remove rooms',
                    'id': 'manage_rooms',
                    'name': 'Manage Rooms'
                },
                'send_message': {
                    'description': 'Send private one-on-one messages',
                    'id': 'send_message',
                    'name': 'Send Message'
                }
            },
            'url': 'https://api.hipchat.com/v2/'
        },
        'oauth2Provider': {
            'authorizationUrl': 'https://www.hipchat.com/users/authorize',
            'tokenUrl': 'https://api.hipchat.com/v2/oauth/token'
        }
    },
    'links': {
        'api': 'https://api.hipchat.com/v2',
        'homepage': 'https://www.hipchat.com',
        'self': 'https://api.hipchat.com/v2/capabilities',
        'subdomain': 'https://www.hipchat.com'
    },
    'connect_server_api_version': 1,
    'vendor': {
        'url': 'http://atlassian.com',
        'name': 'Atlassian'
    },
    'key': 'hipchat'
}

mock_tokenData = {
    'group_id': 46617,
    'group_name': 'tranSMART',
    'expires_in': 431999999,
    'access_token': 'Ttqaf9OGREMNHIOSIYaXqM64hZ3DHSAEelxpLDeT',
    'scope': 'send_notification',
    'token_type': 'bearer'
}

mock_glassfrogToken = '172aa12c195cf90cf6bcg856523111c0ceec4eab'


def mock_authorization_headers(jwt_token='banana'):
    return {'Authorization': 'JWT ' + jwt_token}


def mock_jwt_data(signed_request):
    return {'xdmhost': 'https://transmart.hipchat.com', 'signed_request': signed_request}


def mock_jwt_decoded(time):
    return {
        'iat': 1468372150,
        'iss': 'f3100c47-9936-40e8-a8aa-12314e8da8f0',
        'exp': time,
        'prn': '351107',
        'sub': '351107',
        'jti': 'YGmIBL8ewp0Ma8NIGEgp',
        'context': {
            'room_id': 2589171,
            'roomId': 2589171,
            'user_tz': 'Europe/Amsterdam'
        }
    }


def mock_messagedata(message):
    return {
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
                "message": message,
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


mock_401_flash_message = ('Encountered Error 401 when testing the Glassfrog Token.'
                          ' Message given: \'api key not specified or not valid\'.')

mock_401_responsebody = {'message': 'api key not specified or not valid'}

mock_circles_response = {
    'circles': [
        {
            'id': 8495,
            'links': {},
            'short_name': 'The Hyve',
            'strategy': None,
            'name': 'The Hyve Company Circle'
        },
        {
            'id': 9032,
            'links': {},
            'short_name': 'Delivery',
            'strategy': None,
            'name': 'Delivery'
        },
        {
            'id': 15512,
            'links': {},
            'short_name': 'Business Development & Sales',
            'strategy': None,
            'name': 'Business Development & Sales'
        }
    ],
    'linked': {
        'roles': [],
        'domains': [],
        'policies': [],
        'supported_roles': [
            {
                'links': {
                    'supporting_circle': 8495,
                    'people': [],
                    'accountabilities':[],
                    'domains':[],
                    'circle':None
                },
                'purpose':'Party',
                'name':'The Hyve Company Circle',
                'id':7763372
            },
            {
                'links': {
                    'supporting_circle': 9032,
                    'people': [],
                    'accountabilities':[],
                    'domains':[],
                    'circle': 8495
                },
                'purpose':'Deliver stuff',
                'name':'Service Delivery',
                'id': 7745623
            },
            {
                'links': {
                    'supporting_circle': 15512,
                    'people': [],
                    'accountabilities':[],
                    'domains':[],
                    'circle': 8495
                },
                'purpose':'Sell stuff',
                'name':'Business Development & Sales',
                'id': 7298371
            }
        ]

    }
}

mock_circles_message = '''The following circles are in your organization:<br />
<ul>
<li><code>/hipfrog circle 8495</code> -
 <a href="https://app.glassfrog.com/circles/8495">The Hyve Company Circle</a></li>
<li><code>/hipfrog circle 9032</code> -
 <a href="https://app.glassfrog.com/circles/9032">Delivery</a></li>
<li><code>/hipfrog circle 15512</code> -
 <a href="https://app.glassfrog.com/circles/15512">Business Development & Sales</a></li>
</ul>'''

mock_circle_circleId_response = {
    'linked': {
        'policies': [

        ],
        'domains': [
            {
                'description': 'cBioPortal Architecture roadmap',
                'id': 8467822
            },
            {
                'description': 'cBioPortal Community engagement',
                'id': 8467823
            }
        ],
        'supported_roles': [
            {
                'links': {
                    'accountabilities': [
                        8914197,
                        8914198,
                        8914199
                    ],
                    'circle':8996,
                    'domains':[
                        8467822,
                        8467823
                    ],
                    'people':[
                        28608
                    ],
                    'supporting_circle':13665
                },
                'purpose':('Create and sustain cBioPortal as a great product and a thriving'
                           ' open source community, by making it the default  for translational'
                           ' oncology data visualization portal'),
                'name':'cBioPortal',
                'id':8283892
            }
        ],
        'roles': []
    },
    'circles': [
        {
            'links': {
                'policies': [

                ],
                'domain':[
                    8467822,
                    8467823
                ],
                'supported_role':8283892,
                'roles':[
                    8284164,
                    8284162,
                    8284166,
                    8284163
                ]
            },
            'strategy':None,
            'short_name':'cBioPortal',
            'name':'cBioPortal',
            'id':13665
        }
    ]
}

mock_circle_circleId_message = '''
<strong><a href="https://app.glassfrog.com/circles/{0}">Circle - cBioPortal</a></strong><br/>
<br/>
<strong>Purpose:</strong>
 Create and sustain cBioPortal as a great product and a thriving open source community, by making
 it the default for translational oncology data visualization portal<br/>
<strong>Domains:</strong> cBioPortal Architecture roadmap, cBioPortal Community engagement<br/>
<strong>Parent circle:</strong> <code>/hipfrog circle 8996</code><br/>
<strong>More:</strong>
<ul><li><code>/hipfrog circle {0} members</code> - List the members of this circle</li>
<li><code>/hipfrog circle {0} roles</code> - List the roles in this circle</li>
</ul>'''

mock_circle_members_response = {
    'people': [
        {
            'id': 1234,
            'email': 'someone@thehyve.nl',
            'external_id': None,
            'name': 'Someone van Something',
            'links': {
                'circles': [
                    1,
                    2
                ]
            }
        },
        {
            'id': 22309,
            'email': 'ward@thehyve.nl',
            'external_id': None,
            'name': 'Ward Weistra',
            'links': {
                'circles': [
                    1,
                    2,
                    23
                ]
            }
        }
    ]
}

mock_circle_members_message = '''The following people are in your circle:<br />
<ul>
<li><code>1234</code> -
 <a href="https://app.glassfrog.com/people/1234">Someone van Something</a></li>
<li><code>22309</code> -
 <a href="https://app.glassfrog.com/people/22309">Ward Weistra</a></li>
 </ul>'''

mock_circle_roles_response = {
    'linked': {
        'domains': [
            {
                'description': 'cBioPortal Architecture roadmap',
                'id': 8467822
            },
            {
                'description': 'cBioPortal Community engagement',
                'id': 8467823
            },
            {
                'description': 'Role assignments within the Circle',
                'id': 7884527
            }
        ],
        'circles': [],
        'people': [],
        'accountabilities': [
            {
                'description': 'Engaging in the product X community meetings',
                'id': 8914197
            },
            {
                'description': ('Maintaining a vision on product X as a product and its relation '
                                'to other open source initiatives'),
                'id': 8914198
            },
            {
                'description': 'Promoting The Hyve as go-to company for product X services',
                'id': 8914199
            },
            {
                'description': ('Providing everyone at @The_Hyve_Company_Circle with offices and'
                                ' equipment\nFacilitating company mandated travels for'
                                ' @The_Hyve_Company_Circle members'),
                'id': 8912563
            }
        ]
    },
    'roles': [
        {
            'id': 8282582,
            'links': {
                'domains': [

                ],
                'circle':8996,
                'people':[
                    28477,
                    28611
                ],
                'supporting_circle':None,
                'accountabilities':[

                ]
            },
            'name':'Finance',
            'purpose':'Providing The Hyve with finance and accounting functions'
        },
        {
            'id': 8283892,
            'links': {
                'domains': [
                    8467822,
                    8467823
                ],
                'circle':8996,
                'people':[
                    28608
                ],
                'supporting_circle':13665,
                'accountabilities':[
                    8914197,
                    8914198,
                    8914199
                ]
            },
            'name':'product X',
            'purpose':('Create and sustain product X as a great product and a thriving open source'
                       ' community, by making it the default for function Y')
        },
        {
            'id': 8282557,
            'links': {
                'domains': [

                ],
                'circle':8996,
                'people':[
                    32696
                ],
                'supporting_circle':None,
                'accountabilities':[
                    8912563
                ]
            },
            'name':'Facilities',
            'purpose':'Facilitating the company with all necessary office support'
        },
        {
            'id': 7763373,
            'links': {
                'domains': [
                    7884527
                ],
                'circle':8996,
                'people':[
                    28604
                ],
                'supporting_circle':None,
                'accountabilities':[]
            },
            'name':'Lead Link',
            'purpose':('Advance biology and medical science by creating and serving thriving'
                       ' open source communities')
        },
        {
            'id': 7937421,
            'links': {
                'domains': [

                ],
                'circle':8996,
                'people':[
                ],
                'supporting_circle':10625,
                'accountabilities':[
                ]
            },
            'name':'Business Development & Sales',
            'purpose':('Doing the marketing, Business Development & Sales of'
                       ' @The_Hyve_Company_Circle')
        }
    ]
}

mock_circle_roles_message = '''The following people are in your circle:<br />
<ul>
<li><code>8282582</code> - <a href="https://app.glassfrog.com/roles/8282582">Finance</a></li>
<li><code>8283892</code> - <a href="https://app.glassfrog.com/roles/8283892">product X</a></li>
<li><code>8282557</code> - <a href="https://app.glassfrog.com/roles/8282557">Facilities</a></li>
<li><code>7763373</code> - <a href="https://app.glassfrog.com/roles/7763373">Lead Link</a></li>
<li><code>7937421</code> - <a href="https://app.glassfrog.com/roles/7937421">
Business Development & Sales</a></li>
</ul>
'''

mock_roles_response = {
    "linked": {
        "circles": [],
        'accountabilities': [],
        "people": [],
        'domains': []
    },
    "roles": [
        {
            "id": 83866836,
            "name": "Fulfillment Role",
            "purpose": 'Exist',
            "links": {
                'supporting_circle': None
            }
        },
        {
            "id": 83866837,
            "name": "Entertainment Role",
            "purpose": 'Dancing',
            "links": {
                'supporting_circle': None
            }
        },
        {
            "id": 83866838,
            "name": "Delivery secretary",
            "purpose": 'Making sure everything gets noted down',
            "links": {
                'supporting_circle': None
            }
        }
    ]
}

mock_role_roleid_response = {
    "linked": {
        "circles": [
            {
                "id": 582240928,
                "name": "Operations",
                "short_name": "Ops",
                "strategy": ("Emphasize \"Documenting & Aligning to Standards\", "
                             "even over \"Developing & Co-Creating Novelty\""),
                "links": {
                }
            }
        ],
        'accountabilities': [
            {
                'description': ('Assigning Partners to the Circle\xe2\x80\x99s Roles; monitoring '
                                'the fit; offering feedback to enhance fit; and re-assigning '
                                'Roles to other Partners when useful for enhancing fit'),
                'id': 8234494
            },
            {
                'description': ('Allocating the Circle\xe2\x80\x99s resources across its '
                                'various Projects and/or Roles'),
                'id': 8234495
            }
        ],
        "people": [
            {
                "id": 811765527,
                "name": "Henk de Vries",
                "email": "henk@devries.com",
                "external_id": None
            }
        ],
        'domains': [
            {
                'description': 'Role assignments within the Circle',
                'id': 8424325
            }
        ]
    },
    "roles": [
        {
            "id": 83866836,
            "name": "Fulfillment Role",
            "purpose": 'Exist',
            "links": {
                "circle": 582240928,
                "people": [
                    811765527
                ],
                'accountabilities': [
                    8234494,
                    8234495
                ],
                'domains':[
                    8424325
                ]
            }
        }
    ]
}

mock_role_roleId_message = '''
<strong><a href="https://app.glassfrog.com/roles/83866836">Role - Fulfillment Role</a></strong>
<br/><br/>
<strong>Purpose:</strong> Exist<br/>
<strong>Domain:</strong> Role assignments within the Circle<br/>
<strong>Circle:</strong> <code>/hipfrog circle 582240928</code> -
 <a href="https://app.glassfrog.com/circles/582240928">Operations</a><br/>
<strong>Accountabilities:</strong><ul>
<li>Assigning Partners to the Circleâs Roles; monitoring the fit; offering feedback to enhance
 fit; and re-assigning Roles to other Partners when useful for enhancing fit</li>
<li>Allocating the Circleâs resources across its various Projects and/or Roles</li>
</ul>
<br/>
<strong>Person: </strong><code>811765527</code> -
 <a href="https://app.glassfrog.com/people/811765527">Carlos Aldrich</a>'''

mock_room_members_response = {
    "items": [
        {
            "id": 1325375,
            "mention_name": "HenkdeVries",
            "name": "Henk de Vries",
            "room_roles": [
                "room_member"
            ],
            "version":"QMWTDSXQ"
        },
        {
            "id": 32797,
            "mention_name": "WardWeistra",
            "name": "Ward Weistra",
            "room_roles": [
                "room_member",
                "room_admin"
            ],
            "version":"00000000"
        }
    ],
    "links": {
        "self": "https://api.hipchat.com/v2/room/1000/member"
    },
    "maxResults": 100,
    "startIndex": 0
}

mock_atrole_mentions = '''Fulfillment Role (/hipfrog role {0}) - @HenkdeVries'''
mock_atrole_message = ('@WardWeistra said: Beste @Role {0}: Hoi! /cc '
                       'Fulfillment Role (/hipfrog role {0}) - @HenkdeVries')
mock_atcircle_mentions = ('Circle {0} (/hipfrog circle {0}) - Someone van Something,'
                          ' @WardWeistra')
mock_atcircle_message = ('@WardWeistra said: Beste @Circle {0}: Hoi! /cc '
                         'Circle {1} (/hipfrog circle {1}) - Someone van Something, @WardWeistra')
