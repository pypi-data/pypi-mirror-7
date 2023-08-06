#-*- coding: utf-8 -*-
"""
:Author: Arne Simon [arne.simon@slice-dice.de]
"""
import django.core.exceptions

try:
    from django.conf import settings
    from django.contrib.auth.backends import ModelBackend
    from django.contrib.auth import get_user_model
except django.core.exceptions.ImproperlyConfigured:
    # Sphinx complains about improperly configured django project at build time
    # so we create a dummy ModelBackend class for proper docu creation.
    class ModelBackend:
        pass

import logging


logger = logging.getLogger("aboutyou.backend")


class AboutyouBackend(ModelBackend):
    """
    An aboutyou backend which authenticates a user by its access token.

    .. note::

        If no user with the corresponding aboutyou id exists a new one will be created.

    .. note::

        Your user model has to have a field **aboutyou_id**.

    .. rubric:: Usage

    .. code-block:: python

        AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'aboutyou.django.backend.AboutyouBackend',
        )

    .. rubric:: Testing

        For testing set in the following values in djangos settings.py

    .. code-block:: python

        API_TEST_TOKEN = hashlib.sha512('testing') # used as authentication token
        API_TEST_USER = 1                          # The id of the user model which is associated with the test token
    """
    def authenticate(self, aboutyou_token=None):
        """
        :param aboutyou_token: The aboutyou access token.
        """
        user = None

        if aboutyou_token == settings.API_TEST_TOKEN:
                if settings.DEBUG:
                    user = get_user_model().objects.get(pk=settings.API_TEST_USER)
                else:
                    logger.warn('some one tries to use the test token')
        elif aboutyou_token is not None:

            data = settings.AUTH.get_me(aboutyou_token)

            if data:

                try:
                    user, created = get_user_model().objects.get_or_create(aboutyou_id=data.get("id"))

                    # user.token = aboutyou_token
                    firstname, lastname, email = data.get("firstname"), data.get("lastname"), data.get('email')

                    if email:
                        user.email = email

                    if firstname:
                        user.first_name = firstname

                    if lastname:
                        user.last_name = lastname

                    if created:
                        firstname, lastname = data.get("firstname"), data.get("lastname")

                        if firstname and lastname:
                            user.username = "{}_{}.".format([0])
                        elif firstname:
                            user.username = firstname

                        logger.info("created user %s %s %s", user.aboutyou_id, user.username, user.email)

                    user.save()

                except Exception:
                    logger.exception('aboutyou_token: {}'.format(aboutyou_token))
                    user = None

        if user is not None:
            logger.debug("authenticated user %s %s %s %s", user.id, user.aboutyou_id, user.username, user.email)

            return user


