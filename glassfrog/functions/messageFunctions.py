import jwt
from glassfrog.models import Installation
from flask import escape


def createMessageDict(color, message, message_format="html"):
    message_dict = {
        "color": color,
        "message": str(message),
        "notify": False,
        "message_format": message_format
        }
    return message_dict


def getInstallationFromOauthId(oauthId):
    installation = Installation.query.filter_by(oauthId=oauthId).first()
    return installation


def getInstallationFromJWT(signed_request):
    jwt_unverified = jwt.decode(signed_request,
                                options={'verify_signature': False, 'verify_exp': False})
    oauthId = jwt_unverified['iss']
    installation = getInstallationFromOauthId(oauthId)
    secret = installation.oauthSecret
    jwt.decode(signed_request, secret, algorithms=['HS256'])
    return installation
