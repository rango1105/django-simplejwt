from __future__ import unicode_literals

from django.contrib.auth import models as auth_models
from django.db.models.manager import EmptyManager
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property

from .compat import CallableFalse, CallableTrue
from .settings import api_settings


@python_2_unicode_compatible
class TokenUser(object):
    """
    A dummy user class modeled after django.contrib.auth.models.AnonymousUser.
    Used in conjunction with the `JWTTokenUserAuthentication` backend to
    implement single sign-on functionality across services which share the same
    secret key.  `JWTTokenUserAuthentication` will return an instance of this
    class instead of a `User` model instance.  Instances of this class act as
    stateless user objects which are built from validated token payloads.
    """
    username = ''

    # User is always active since SimpleJWT will never issue a token for an
    # inactive user
    is_active = True

    _groups = EmptyManager(auth_models.Group)
    _user_permissions = EmptyManager(auth_models.Permission)

    def __init__(self, token_payload):
        self.token_payload = token_payload

    def __getattr__(self, name):
        try:
            return self.token_payload[name]
        except KeyError:
            raise AttributeError("'{}' object has no attirbute '{}'".format(self.__class__.__name__, name))

    def __str__(self):
        return 'TokenUser {}'.format(self.id)

    @cached_property
    def id(self):
        return self.token_payload[api_settings.PAYLOAD_ID_FIELD]

    @cached_property
    def pk(self):
        return self.id

    @cached_property
    def is_staff(self):
        return self.token_payload.get('is_staff', False)

    @cached_property
    def is_superuser(self):
        return self.token_payload.get('is_superuser', False)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def save(self):
        raise NotImplementedError('Token users have no DB representation.')

    def delete(self):
        raise NotImplementedError('Token users have no DB representation.')

    def set_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation.')

    def check_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation.')

    @property
    def groups(self):
        return self._groups

    @property
    def user_permissions(self):
        return self._user_permissions

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        return False

    def has_perms(self, perm_list, obj=None):
        return False

    def has_module_perms(self, module):
        return False

    @property
    def is_anonymous(self):
        return CallableFalse

    @property
    def is_authenticated(self):
        return CallableTrue

    def get_username(self):
        return self.username
