# -*- coding: utf-8 -*-
from django.conf import settings
from authy.api import AuthyApiClient

AUTHY_KEY = getattr(settings, 'AUTHY_KEY', None)
AUTHY_IS_SANDBOXED = getattr(settings, 'AUTHY_IS_SANDBOXED', False)
AUTHY_FORCE_VERIFICATION = getattr(settings, 'AUTHY_FORCE_VERIFICATION', True)

assert AUTHY_KEY, 'You must define a settings.AUTHY_KEY'

AUTHY_API_URL = 'http://sandbox-api.authy.com' if AUTHY_IS_SANDBOXED is True else 'https://api.authy.com'  # None as we then use the clients default which should be https://api.authy.com

from .signals import authy_event

import logging
logger = logging.getLogger('django.request')


class AuthyService(object):
    """
    Service for interacting with Authy
    """
    user = None
    authy_profile = None

    client = None
    force_verification = False
    errors = {}

    def __init__(self, user, *args, **kwargs):
        # Allow overrides
        self.user = user
        self.authy_profile = kwargs.get('authy_profile', user.authy_profile) # hope its passed in otherwise get it, efficent

        self.key = kwargs.get('key', AUTHY_KEY)
        self.force_verification = kwargs.get('force_verification', AUTHY_FORCE_VERIFICATION)
        self.errors = {}  # reset errors

        self.client = AuthyApiClient(api_key=self.key, api_uri=AUTHY_API_URL)

        logger.info('Initialized authy.Client with key: %s' % self.key)

        self.ensure_user_registered()

    @property
    def authy_id(self):
        return int(self.authy_profile.authy_id)

    def ensure_user_registered(self):
        """
        Create an authy user at authy if we dont have an authy_id for the
        current django user
        """
        if self.authy_profile.authy_id is None:

            authy_user = self.client.users.create(self.user.email,
                                                  int(self.authy_profile.cellphone.national_number), # phonenumberfield stores as long
                                                  int(self.authy_profile.cellphone.country_code)) #email, cellphone, area_code

            if authy_user.ok():
                self.authy_profile.authy_id = authy_user.id
                self.authy_profile.save(update_fields=['authy_id'])

            else:
                errors = authy_user.errors()
                msg = 'Could not register Auth.user: %s' % errors
                logger.error(msg)
                raise Exception(msg)

        logger.info(u'Authy user: %s %s' % (self.user, self.authy_profile.authy_id))

        return True

    def request_sms_token(self):
        """
        To be used when the user manually presses a buttton in your ui that
        says "I dont have a smartphone, please send me a token by sms"
        """
        if self.authy_profile.is_smartphone is True:
            sms = self.client.users.request_sms(self.authy_id)
        else:
            sms = self.client.users.request_sms(self.authy_id, {"force": True})  # force as the user is on an older phone with no app installed

        ok = sms.ok()
        return ok if ok is True else sms.errors()

    def verify_token(self, token):
        """
        Token should always be passed in as a string
        0000000 evaluates as 0 (sandbox test token)
        """
        if type(token) not in [str, unicode]:
            raise Exception('Token to validate should be a string.')

        verification = self.client.tokens.verify(self.authy_id, str(token), {"force": self.force_verification})
        verified = verification.ok()
        self.errors = verification.errors()

        if not verified:
            logger.error(u'User: %s could not be verified using the token: %s due to: %s' % (self.user, token, self.errors))
        else:
            logger.debug(u'User: %s has authenticated successfully with Authy using token: %s' % (self.user, token))

        return verified
