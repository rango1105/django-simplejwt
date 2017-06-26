from __future__ import unicode_literals

from django.contrib.auth import authenticate
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .exceptions import TokenError
from .settings import api_settings
from .state import User
from .tokens import RefreshToken, SlidingToken


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super(PasswordField, self).__init__(*args, **kwargs)


class TokenObtainSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super(TokenObtainSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        self.user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        # Prior to Django 1.10, inactive users could be authenticated with the
        # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
        # prevents inactive users from authenticating.  App designers can still
        # allow inactive users to authenticate by opting for the new
        # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
        # users from authenticating to enforce a reasonable policy and provide
        # sensible backwards compatibility with older Django versions.
        if self.user is None or not self.user.is_active:
            raise serializers.ValidationError(
                _('No active account found with the given credentials'),
            )

        return {}


class TokenObtainPairSerializer(TokenObtainSerializer):
    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)

        refresh = RefreshToken.for_user(self.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)

        return data


class TokenObtainSlidingSerializer(TokenObtainSerializer):
    def validate(self, attrs):
        data = super(TokenObtainSlidingSerializer, self).validate(attrs)

        data['token'] = text_type(SlidingToken.for_user(self.user))

        return data


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh'])
        except TokenError as e:
            raise serializers.ValidationError(e.args[0])

        return {'access': text_type(refresh.access_token)}


class TokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            token = SlidingToken(attrs['token'])
            # Check that the timestamp in the "refresh_exp" claim has not
            # passed
            token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)
        except TokenError as e:
            raise serializers.ValidationError(e.args[0])

        # Update the "exp" claim
        token.set_exp()

        return {'token': text_type(token)}
