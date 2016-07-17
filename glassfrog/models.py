from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
db = SQLAlchemy()


class Installation(db.Model):
    __tablename__ = 'installations'
    id = db.Column(db.Integer, primary_key=True)
    oauthId = db.Column(db.String(50), unique=True)
    capabilitiesUrl = db.Column(db.String(50))
    roomId = db.Column(db.Integer)
    groupId = db.Column(db.Integer)
    oauthSecret = db.Column(db.String(50))
    hipchatApiProvider_url = db.Column(db.String)
    access_token = db.Column(db.String)
    expires_in = db.Column(db.Integer)
    group_id = db.Column(db.Integer)
    group_name = db.Column(db.String)
    scope = db.Column(db.String)
    token_type = db.Column(db.String)
    glassfrogToken = db.Column(db.String(50))
    linkedCircle = db.Column(db.Integer)

    def __init__(self, oauthId, capabilitiesUrl, roomId, groupId, oauthSecret):
        self.oauthId = oauthId
        self.capabilitiesUrl = capabilitiesUrl
        self.roomId = roomId
        self.groupId = groupId
        self.oauthSecret = oauthSecret

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            for item in self.__dict__:
                if isinstance(self.__dict__[item], sqlalchemy.orm.state.InstanceState):
                    break
                if self.__dict__[item] != other.__dict__[item]:
                    return False
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Installation {} with oauthId {}>'.format(self.id, self.oauthId)
