import jwt
from glassfrog.models import Installation
from flask import escape
import Levenshtein


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


def getLevenshteinDistance(item, keyword):
    item = item.lower().replace(' ', '').replace('-', '').replace('_', '')
    keyword = keyword.lower().replace(' ', '').replace('-', '').replace('_', '')
    return Levenshtein.ratio(item.lower(), keyword.lower())


def getMatchingCircle(circles, keyword):
    closestDistance = 0
    closestMatch = -999
    for circle in circles:
        for name in ['name', 'short_name']:
            distance = getLevenshteinDistance(circle[name], keyword)
            if distance > 0.3 and distance > closestDistance:
                closestDistance = distance
                closestMatch = circle['id']
    return closestMatch

# TODO getMatchingRole
