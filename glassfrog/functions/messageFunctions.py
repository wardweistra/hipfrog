import jwt
from glassfrog.models import Installation
from flask import escape


def createMessageDict(color, message, card=None):
    message_dict = {
        "color": color,
        "message": str(message),
        "notify": False,
        "message_format": "html"
        }
    if card is not None:
        message_dict['card'] = card
    return message_dict


def getInstallationFromJWT(signed_request):
    jwt_unverified = jwt.decode(signed_request,
                                options={'verify_signature': False, 'verify_exp': False})
    oauthId = jwt_unverified['iss']
    installation = Installation.query.filter_by(oauthId=oauthId).first()
    secret = installation.oauthSecret
    jwt.decode(signed_request, secret, algorithms=['HS256'])
    return installation
