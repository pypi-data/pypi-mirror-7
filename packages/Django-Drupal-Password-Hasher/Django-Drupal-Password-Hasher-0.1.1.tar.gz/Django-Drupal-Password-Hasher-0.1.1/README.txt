=============================
Django-Drupal Password Hasher
=============================

Django-Drupal Password Hasher is a simple package created to hash Drupal 7
passwords with the prefix 'drupal'.

Taken from https://djangosnippets.org/snippets/3030/ 

Installation typically looks like::

    pip install Django-drupal-password-hasher

Typical usage in a python script looks like::

    from djangodrupalpasswordhasher import drupal_password_hasher

    hasher = DrupalPasswordHasher()
    salt = hasher.salt()
    password = "foobar"
    encoded_password = hasher.encode(password, salt)

In a django project, change the settings file to look like::

    PASSWORD_HASHERS = (
        'djangodrupalpasswordhasher.drupal_password_hasher.DrupalPasswordHasher',
    )

And user authentication continues as normal::

    from django.contrib.auth.models import User

    ...

    user = User(first_name='foo', last_name='bar', email='foobar@foobar.com')
    user.set_password("some_random_password")
    user.save()

Note: Django uses the first entry in the PASSWORD_HASHERS section of your
settings file for user authentication by default. If you have other password
hashers but want to use this one, make sure it is the first entry in the list.
