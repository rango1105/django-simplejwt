from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.six.moves import reload_module
from jose import jwt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.settings import api_settings

from .utils import override_api_settings

User = get_user_model()


class TestJWTAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.backend = authentication.JWTAuthentication()

        self.fake_token = b'TokenMcTokenface'
        self.fake_header = b'Bearer ' + self.fake_token

    def test_get_header(self):
        # Should return None if no authorization header
        request = self.factory.get('/test-url/')
        self.assertIsNone(self.backend.get_header(request))

        # Should pull correct header off request
        request = self.factory.get('/test-url/', HTTP_AUTHORIZATION=self.fake_header)
        self.assertEqual(self.backend.get_header(request), self.fake_header)

        # Should work for unicode headers
        request = self.factory.get('/test-url/', HTTP_AUTHORIZATION=self.fake_header.decode('utf-8'))
        self.assertEqual(self.backend.get_header(request), self.fake_header)

    def test_get_token(self):
        # Should return None if header lacks correct type keyword
        with override_api_settings(AUTH_HEADER_TYPE='JWT'):
            reload_module(authentication)
            self.assertIsNone(self.backend.get_token(self.fake_header))
        reload_module(authentication)

        # Should raise error if header is malformed
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_token(b'Bearer one two')

        with self.assertRaises(AuthenticationFailed):
            self.backend.get_token(b'Bearer')

        # Otherwise, should return token in header
        self.assertEqual(self.backend.get_token(self.fake_header), self.fake_token)

    def test_get_payload(self):
        payload = {'foo': 'bar'}

        # Should raise AuthenticationFailed if token not valid
        payload['exp'] = datetime.utcnow() - timedelta(days=1)
        bad_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_payload(bad_token)

        # Otherwise, should return data payload for token
        payload['exp'] = datetime.utcnow() + timedelta(days=1)
        good_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        self.assertEqual(self.backend.get_payload(good_token), payload)

    def test_get_user_id(self):
        payload = {'some_other_id': 'foo'}

        # Should raise error if no recognizable user identification
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user_id(payload)

        payload[api_settings.PAYLOAD_ID_FIELD] = 'foo'

        # Should return any recognizable user identification
        self.assertEqual(self.backend.get_user_id(payload), 'foo')

    def test_get_user(self):
        u = User.objects.create_user(username='markhamill')
        u.is_active = False
        u.save()

        correct_id = getattr(u, api_settings.USER_ID_FIELD)

        # Should raise exception if user not found
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(42)

        # Should raise exception if user is inactive
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(correct_id)

        u.is_active = True
        u.save()

        # Otherwise, should return correct user
        self.assertEqual(self.backend.get_user(correct_id).id, u.id)
