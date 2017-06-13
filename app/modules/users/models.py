# encoding: utf-8
"""
User database models
--------------------
"""
import enum

from mongoengine import Document, EmailField, StringField, DateTimeField, IntField
from datetime import datetime
from app.extensions import Timestamp


from app.extensions import db


def _get_is_static_role_property(role_name, static_role):
    """
    A helper function that aims to provide a property getter and setter
    for static roles.

    Args:
        role_name (str)
        static_role (int) - a bit mask for a specific role

    Returns:
        property_method (property) - preconfigured getter and setter property
        for accessing role.
    """
    @property
    def _is_static_role_property(self):
        return self.has_static_role(static_role)

    @_is_static_role_property.setter
    def _is_static_role_property(self, value):
        if value:
            self.set_static_role(static_role)
        else:
            self.unset_static_role(static_role)

    _is_static_role_property.fget.__name__ = role_name
    return _is_static_role_property


class User(Document, Timestamp):
    meta = {'allow_inheritance': True, 'abstract': False, 'collection': 'users'}


    email = EmailField(unique=True)
    password = StringField(max_length=128)


    first_name = StringField(max_length=30)
    middle_name = StringField(max_length=30)
    last_name = StringField(max_length=30)

    class StaticRoles(enum.Enum):
        INTERNAL = (0x8000, "Internal")
        ADMIN = (0x4000, "Admin")
        REGULAR_USER = (0x2000, "Regular User")
        ACTIVE = (0x1000, "Active Account")

        @property
        def mask(self):
            return self.value[0]

        @property
        def title(self):
            return self.value[1]


    static_roles = IntField(default=0)

    is_internal = _get_is_static_role_property('is_internal', StaticRoles.INTERNAL)
    is_admin = _get_is_static_role_property('is_admin', StaticRoles.ADMIN)
    is_regular_user = _get_is_static_role_property('is_regular_user', StaticRoles.REGULAR_USER)
    is_active = _get_is_static_role_property('is_active', StaticRoles.ACTIVE)

    def __repr__(self):
        return (
            "<{class_name}("
            "id={self.id}, "
            "email=\"{self.email}\", "
            "is_internal={self.is_internal}, "
            "is_admin={self.is_admin}, "
            "is_regular_user={self.is_regular_user}, "
            "is_active={self.is_active}, "
            ")>".format(
                class_name=self.__class__.__name__,
                self=self
            )
        )

    def has_static_role(self, role):
        return (self.static_roles & role.mask) != 0

    def set_static_role(self, role):
        if self.has_static_role(role):
            return
        self.static_roles |= role.mask

    def unset_static_role(self, role):
        if not self.has_static_role(role):
            return
        self.static_roles ^= role.mask

    def check_owner(self, user):
        return self == user

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @classmethod
    def find_with_password(cls, email, password):
        """
        Args:
            email (str)
            password (str) - plain-text password

        Returns:
            user (User) - if there is a user with a specified email and
            password, None otherwise.
        """
        user = cls.objects(email=email).first()

        if not user:
            return None
        if user.password == password:
            return user
        return None


