# encoding: utf-8
"""
Team database models
--------------------
"""

#from sqlalchemy_utils import Timestamp

from app.extensions import db
from mongoengine import EmailField, StringField, DateTimeField, IntField, ListField, ReferenceField, BooleanField
from app.modules.api.mongo_helpers import EnumField, StringEnumField, Timestamp
from flask_mongoengine import Document


#class TeamMember(db.Model):
class TeamMember(Document):

    """
    Team-member database model.
    """
    #__tablename__ = 'team_member'
    meta = {'allow_inheritance': True, 'abstract': False, 'collection': 'team_member'}


    team = ReferenceField("Team")
    @property
    def team_id(self):
        return self.team.id
    user = ReferenceField("User", unique_with='team')
    @property
    def user_id(self):
        return self.user.id


    #team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    #team = db.relationship('Team')
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    #user = db.relationship(
    #    'User',
    #    backref=db.backref('teams_membership', cascade='delete, delete-orphan')
    #)

    is_leader = BooleanField(default=False)
    #is_leader = db.Column(db.Boolean, default=False, nullable=False)

    #__table_args__ = (
    #    db.UniqueConstraint('team_id', 'user_id', name='_team_user_uc'),
    #)

    def __repr__(self):
        return (
            "<{class_name}("
            "team_id={self.team_id}, "
            "user_id=\"{self.user_id}\", "
            "is_leader=\"{self.is_leader}\""
            ")>".format(
                class_name=self.__class__.__name__,
                self=self
            )
        )

    def check_owner(self, user):
        return self.user == user

    def check_supervisor(self, user):
        return self.team.check_owner(user)


#class Team(db.Model, Timestamp):
class Team(Document, Timestamp):

    """
    Team database model.
    """

    id = IntField()
    title = StringField(max_length=50)

    #id = db.Column(db.Integer, primary_key=True) # pylint: disable=invalid-name
    #title = db.Column(db.String(length=50), nullable=False)

    members = ListField(ReferenceField('TeamMember'))

    #members = db.relationship('TeamMember', cascade='delete, delete-orphan')

    def __repr__(self):
        return (
            "<{class_name}("
            "id={self.id}, "
            "title=\"{self.title}\""
            ")>".format(
                class_name=self.__class__.__name__,
                self=self
            )
        )

    #FIXME: find mongoengine equivalent
    #@db.validates('title')
    def validate_title(self, key, title): # pylint: disable=unused-argument,no-self-use
        if len(title) < 3:
            raise ValueError("Title has to be at least 3 characters long.")
        return title

    def check_owner(self, user):
        """
        This is a helper method for OwnerRolePermission integration.
        """

        if self.objects(team=self, is_leader=True, user=user).first():
            return True
        return False

        #if db.session.query(
        #        TeamMember.query.filter_by(team=self, is_leader=True, user=user).exists()
        #).scalar():
        #    return True
        #return False
