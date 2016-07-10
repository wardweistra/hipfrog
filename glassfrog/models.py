from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Installation(db.Model):
    __tablename__ = 'installations'
    id = db.Column(db.Integer, primary_key=True)
    oauthId = db.Column(db.String(50), unique=True)
    capabilitiesUrl = db.Column(db.String(50))
    roomId = db.Column(db.Integer)
    groupId = db.Column(db.Integer)
    oauthSecret = db.Column(db.String(50))
    glassfrogToken = db.Column(db.String(50))
    linkedCircle = db.Column(db.Integer)

    def __init__(self, oauthId, capabilitiesUrl, roomId, groupId, oauthSecret):
        self.oauthId = oauthId
        self.capabilitiesUrl = capabilitiesUrl
        self.roomId = roomId
        self.groupId = groupId
        self.oauthSecret = oauthSecret

    def __repr__(self):
        return '<Installation {}>'.format(self.id)
