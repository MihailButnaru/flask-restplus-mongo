# encoding: utf-8
"""
OAuth2 provider models.

It is based on the code from the example:
https://github.com/lepture/example-oauth2-server

More details are available here:
* http://flask-oauthlib.readthedocs.org/en/latest/oauth2.html
* http://lepture.com/en/2013/create-oauth-server
"""
import enum

#from sqlalchemy_utils.types import ScalarListType

from app.extensions import db
from flask_mongoengine import Document
from app.modules.users.models import User
from mongoengine import EmailField, StringField, DateTimeField, IntField, ListField, ReferenceField
from app.modules.api.mongo_helpers import EnumField, StringEnumField


class OAuth2Client(Document):
#class OAuth2Client(db.Model):
    """
    Model that binds OAuth2 Client ID and Secret to a specific User.
    """

    meta = {'allow_inheritance': True, 'abstract': False, 'collection': 'oauth2_client'}

    #__tablename__ = 'oauth2_client'

    client_id = StringField(max_length=40)
    #client_id = db.Column(db.String(length=40), primary_key=True)
    client_secret = StringField(max_length=55)
    #client_secret = db.Column(db.String(length=55), nullable=False)

    user = ReferenceField("User")
    @property
    def user_id(self):
        return self.user.id

    #user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), index=True, nullable=False)
    #user = db.relationship('User')

    #class ClientTypes(str, enum.Enum):
    #    public = 'public'
    #    confidential = 'confidential'

    client_type = StringEnumField(['public','confidential'], default='public')

    #client_type = db.Column(db.Enum(ClientTypes), default=ClientTypes.public, nullable=False)
    #redirect_uris = db.Column(ScalarListType(separator=' '), default=[], nullable=False)
    #default_scopes = db.Column(ScalarListType(separator=' '), nullable=False)

    redirect_uris = ListField(StringField(max_length=30), default=[])
    default_scopes = ListField(StringField(max_length=30), default=[])


    @property
    def default_redirect_uri(self):
        redirect_uris = self.redirect_uris
        if redirect_uris:
            return redirect_uris[0]
        return None

    @classmethod
    def find(cls, client_id):
        if not client_id:
            return
        return cls.objects(client_id=client_id).first()

        #return cls.query.get(client_id)


#class OAuth2Grant(db.Model):
class OAuth2Grant(Document):

    """
    Intermediate temporary helper for OAuth2 Grants.
    """

    meta = {'allow_inheritance': True, 'abstract': False, 'collection': 'oauth2_grant'}
    #__tablename__ = 'oauth2_grant'

    #id = db.Column(db.Integer, primary_key=True)  # pylint: disable=invalid-name
    id = IntField()

    user = ReferenceField("User")
    @property
    def user_id(self):
        return self.user.id

    #user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), index=True, nullable=False)
    #user = db.relationship('User')

    client = ReferenceField("OAuth2Client")
    @property
    def client_id(self):
        return self.client.client_id

    #client_id = db.Column(
    #    db.String(length=40),
    #    db.ForeignKey('oauth2_client.client_id'),
    #    index=True,
    #    nullable=False,
    #)
    #client = db.relationship('OAuth2Client')

    code = StringField(max_length=255)

    #code = db.Column(db.String(length=255), index=True, nullable=False)

    #redirect_uri = db.Column(db.String(length=255), nullable=False)
    #expires = db.Column(db.DateTime, nullable=False)
    redirect_uri = StringField(max_length=255)
    expires = DateTimeField()

    #scopes = db.Column(ScalarListType(separator=' '), nullable=False)
    scopes = ListField(StringField(max_length=30), default=[])

    " mongoengine provides delete of same name, does not return self "
    #def delete(self):
    #    db.session.delete(self)
    #    db.session.commit()
    #    return self

    @classmethod
    def find(cls, client_id, code):
        return cls.objects(client_id=client_id, code=code).first()
        #return cls.query.filter_by(client_id=client_id, code=code).first()


#class OAuth2Token(db.Model):
class OAuth2Token(Document):
    """
    OAuth2 Access Tokens storage model.
    """

    meta = {'allow_inheritance': True, 'abstract': False, 'collection': 'oauth2_token'}
    #__tablename__ = 'oauth2_token'

    id = IntField()
    #id = db.Column(db.Integer, primary_key=True)  # pylint: disable=invalid-name

    client = ReferenceField("OAuth2Client")
    @property
    def client_id(self):
        return self.client.client_id

    #client_id = db.Column(
    #    db.String(length=40),
    #    db.ForeignKey('oauth2_client.client_id'),
    #    index=True,
    #    nullable=False,
    #)
    #client = db.relationship('OAuth2Client')

    user = ReferenceField("User")
    @property
    def user_id(self):
        return self.user.id

    #user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), index=True, nullable=False)
    #user = db.relationship('User')

    token_type = StringEnumField(['Bearer'], default='Bearer')

    #class TokenTypes(str, enum.Enum):
    #    # currently only bearer is supported
    #    Bearer = 'Bearer'
    #token_type = db.Column(db.Enum(TokenTypes), nullable=False)

    access_token = StringField(max_length=255, unique=True)
    refresh_token = StringField(max_length=255, unique=True)
    expires = DateTimeField()
    scopes = ListField(StringField(max_length=30), default=[])

    #access_token = db.Column(db.String(length=255), unique=True, nullable=False)
    #refresh_token = db.Column(db.String(length=255), unique=True, nullable=True)
    #expires = db.Column(db.DateTime, nullable=False)
    #scopes = db.Column(ScalarListType(separator=' '), nullable=False)

    @classmethod
    def find(cls, access_token=None, refresh_token=None):
        if access_token:
            return cls.objects(access_token=access_token).first()
            #return cls.query.filter_by(access_token=access_token).first()
        elif refresh_token:
            return cls.objects(refresh_token=refresh_token).first()
            #return cls.query.filter_by(refresh_token=refresh_token).first()
