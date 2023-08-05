django-debreach
===============

Basic mitigation against the `BREACH attack <http://breachattack.com/>`_ for 
Django projects. 

When combined with rate limiting in your web-server, or by using something
like `django-ratelimit <http://django-ratelimit.readthedocs.org/>`_, the 
techniques here should provide at least some protection against the BREACH 
attack.

.. image:: https://badge.fury.io/py/django-debreach.png
    :target: http://badge.fury.io/py/django-debreach

.. image:: https://travis-ci.org/lpomfrey/django-debreach.png?branch=master
    :target: https://travis-ci.org/lpomfrey/django-debreach

.. image:: https://coveralls.io/repos/lpomfrey/django-debreach/badge.png?branch=master
    :target: https://coveralls.io/r/lpomfrey/django-debreach?branch=master

.. image:: https://pypip.in/d/django-debreach/badge.png
        :target: https://crate.io/packages/django-debreach?version=latest

Installation
------------

Install from PyPI using::

    $ pip install django-debreach

If installing from git you'll also need to install the ``PyCrypto`` library.

Add to your `INSTALLED_APPS`::

    INSTALLED_APPS = (
        ...
        'debreach',
        ...
    )

Configuration
-------------

CSRF token masking
++++++++++++++++++
To mask CSRF tokens in the template add the
``debreach.context_processors.csrf`` context processor to the end of your 
`TEMPLATE_CONTEXT_PROCESSORS`::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'debreach.context_processors.csrf',
    )

And add the ``debreach.middleware.CSRFCryptMiddleware`` to your middleware,
*before* ``django.middleware.csrf.CSRFMiddleware``::

    MIDDLEWARE_CLASSES = (
        'debreach.middleware.CSRFCryptMiddleware',
        ...
        'django.middleware.csrf.CSRFMiddleware',
        ...
    )

This works by AES encrypting the CSRF token when it is added to the template,
so that ``{% csrf_token %}`` now produces a hidden field with a value that is 
``"<random-crypt-text>$<actual-csrf-token-encrypted-with-random-crypt-text>"``.
Then, when the form is POSTed, the middleware decrypts the CSRF token back into
it's original form. This ensures that the CSRF content is never the same
between requests. If you are passing the token using the ``X-CSRFToken``
header (e.g. using XHR) that header will also be processed in the same way.

Note that values that are unencrypted, or rather, don't contain a delimiting
``$``, will be left unmodified.


Content length modification
+++++++++++++++++++++++++++

django-debreach also enables you to counter the BREACH attack by randomising the
content length of each response. This is acheived by adding a random string of 
between 12 and 25 characters as a comment to the end of the HTML content. Note
that this will only be applied to responses with a content type of
``text/html``.

To enable content length modification for all responses, add the
``debreach.middleware.RandomCommentMiddleware`` to the *start* of your
middleware, but *after* the ``GzipMiddleware`` if you are using that.::

    MIDDLEWARE_CLASSES = (
        'debreach.middleware.RandomCommentMiddleware',
        ...
    )

or::

    MIDDLEWARE_CLASSES = (
        'django.middleware.gzip.GzipMiddleware',
        'debreach.middleware.RandomCommentMiddleware',
        ...
    )

If you wish to disable this feature for selected views, simply apply the
``debreach.decorators.random_comment_exempt`` decorator to the view.

If you only want to protect a subset of views with content length modification
then it may be easier to not use the middleware, but to selectively apply the
``debreach.decorators.append_random_comment`` decorator to the views you want
protected.
