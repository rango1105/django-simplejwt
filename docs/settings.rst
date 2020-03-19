.. _settings:

Settings
========

Some of Simple JWT's behavior can be customized through settings variables in
``settings.py``:

.. code-block:: python

  # Django project settings.py

  from datetime import timedelta

  ...

  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
      'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
      'ROTATE_REFRESH_TOKENS': False,
      'BLACKLIST_AFTER_ROTATION': True,

      'ALGORITHM': 'HS256',
      'SIGNING_KEY': settings.SECRET_KEY,
      'VERIFYING_KEY': None,
      'AUDIENCE': None,
      'ISSUER': None,

      'AUTH_HEADER_TYPES': ('Bearer',),
      'USER_ID_FIELD': 'id',
      'USER_ID_CLAIM': 'user_id',

      'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
      'TOKEN_TYPE_CLAIM': 'token_type',

      'JTI_CLAIM': 'jti',

      'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
      'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
      'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
  }

Above, the default values for these settings are shown.

``ACCESS_TOKEN_LIFETIME``
-------------------------

A ``datetime.timedelta`` object which specifies how long access tokens are
valid.  This ``timedelta`` value is added to the current UTC time during token
generation to obtain the token's default "exp" claim value.

``REFRESH_TOKEN_LIFETIME``
--------------------------

A ``datetime.timedelta`` object which specifies how long refresh tokens are
valid.  This ``timedelta`` value is added to the current UTC time during token
generation to obtain the token's default "exp" claim value.

``ROTATE_REFRESH_TOKENS``
-------------------------

When set to ``True``, if a refresh token is submitted to the
``TokenRefreshView``, a new refresh token will be returned along with the new
access token.  This new refresh token will be supplied via a "refresh" key in
the JSON response.  New refresh tokens will have a renewed expiration time
which is determined by adding the timedelta in the ``REFRESH_TOKEN_LIFETIME``
setting to the current time when the request is made.  If the blacklist app is
in use and the ``BLACKLIST_AFTER_ROTATION`` setting is set to ``True``, refresh
tokens submitted to the refresh view will be added to the blacklist.

``BLACKLIST_AFTER_ROTATION``
----------------------------

When set to ``True``, causes refresh tokens submitted to the
``TokenRefreshView`` to be added to the blacklist if the blacklist app is in
use and the ``ROTATE_REFRESH_TOKENS`` setting is set to ``True``.

``ALGORITHM``
-------------

The algorithm from the PyJWT library which will be used to perform
signing/verification operations on tokens.  To use symmetric HMAC signing and
verification, the following algorithms may be used: ``'HS256'``, ``'HS384'``,
``'HS512'``.  When an HMAC algorithm is chosen, the ``SIGNING_KEY`` setting
will be used as both the signing key and the verifying key.  In that case, the
``VERIFYING_KEY`` setting will be ignored.  To use asymmetric RSA signing and
verification, the following algorithms may be used: ``'RS256'``, ``'RS384'``,
``'RS512'``.  When an RSA algorithm is chosen, the ``SIGNING_KEY`` setting must
be set to a string that contains an RSA private key.  Likewise, the
``VERIFYING_KEY`` setting must be set to a string that contains an RSA public
key.

``SIGNING_KEY``
---------------

The signing key that is used to sign the content of generated tokens.  For HMAC
signing, this should be a random string with at least as many bits of data as
is required by the signing protocol.  For RSA signing, this should be a string
that contains an RSA private key that is 2048 bits or longer.  Since Simple JWT
defaults to using 256-bit HMAC signing, the ``SIGNING_KEY`` setting defaults to
the value of the ``SECRET_KEY`` setting for your django project.  Although this
is the most reasonable default that Simple JWT can provide, it is recommended
that developers change this setting to a value that is independent from the
django project secret key.  This will make changing the signing key used for
tokens easier in the event that it is compromised.

``VERIFYING_KEY``
-----------------

The verifying key which is used to verify the content of generated tokens.  If
an HMAC algorithm has been specified by the ``ALGORITHM`` setting, the
``VERIFYING_KEY`` setting will be ignored and the value of the ``SIGNING_KEY``
setting will be used.  If an RSA algorithm has been specified by the
``ALGORITHM`` setting, the ``VERIFYING_KEY`` setting must be set to a string
that contains an RSA public key.

``AUDIENCE``
-------------

The audience claim to be included in generated tokens and/or validated in
decoded tokens. When set to ``None``, this field is excluded from tokens and is
not validated.

``ISSUER``
----------

The issuer claim to be included in generated tokens and/or validated in decoded
tokens. When set to ``None``, this field is excluded from tokens and is not
validated.

``AUTH_HEADER_TYPES``
---------------------

The authorization header type(s) that will be accepted for views that require
authentication.  For example, a value of ``'Bearer'`` means that views
requiring authentication would look for a header with the following format:
``Authorization: Bearer <token>``.  This setting may also contain a list or
tuple of possible header types (e.g. ``('Bearer', 'JWT')``).  If a list or
tuple is used in this way, and authentication fails, the first item in the
collection will be used to build the "WWW-Authenticate" header in the response.

``USER_ID_FIELD``
-----------------

The database field from the user model that will be included in generated
tokens to identify users.  It is recommended that the value of this setting
specifies a field that does not normally change once its initial value is
chosen.  For example, specifying a "username" or "email" field would be a poor
choice since an account's username or email might change depending on how
account management in a given service is designed.  This could allow a new
account to be created with an old username while an existing token is still
valid which uses that username as a user identifier.

``USER_ID_CLAIM``
-----------------

The claim in generated tokens which will be used to store user identifiers.
For example, a setting value of ``'user_id'`` would mean generated tokens
include a "user_id" claim that contains the user's identifier.

``AUTH_TOKEN_CLASSES``
----------------------

A list of dot paths to classes that specify the types of token that are allowed
to prove authentication.  More about this in the "Token types" section below.

``TOKEN_TYPE_CLAIM``
--------------------

The claim name that is used to store a token's type.  More about this in the
"Token types" section below.

``JTI_CLAIM``
-------------

The claim name that is used to store a token's unique identifier.  This
identifier is used to identify revoked tokens in the blacklist app.  It may be
necessary in some cases to use another claim besides the default "jti" claim to
store such a value.

``SLIDING_TOKEN_LIFETIME``
--------------------------

A ``datetime.timedelta`` object which specifies how long sliding tokens are
valid to prove authentication.  This ``timedelta`` value is added to the
current UTC time during token generation to obtain the token's default "exp"
claim value.  More about this in the "Sliding tokens" section below.

``SLIDING_TOKEN_REFRESH_LIFETIME``
----------------------------------

A ``datetime.timedelta`` object which specifies how long sliding tokens are
valid to be refreshed.  This ``timedelta`` value is added to the current UTC
time during token generation to obtain the token's default "exp" claim value.
More about this in the "Sliding tokens" section below.

``SLIDING_TOKEN_REFRESH_EXP_CLAIM``
-----------------------------------

The claim name that is used to store the expiration time of a sliding token's
refresh period.  More about this in the "Sliding tokens" section below.
