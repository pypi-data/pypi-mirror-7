===================
SEO iframe Replacer
===================

SEO iframe Replacer is a wsgi middleware to replace iframes containing
'src' attribute by its rendered html code. It is used to allow content
rendered by Ajax to be indexed by search engines like Google. Typical
usage on a django's WSGI script::

    import os
    from django.core.wsgi import get_wsgi_application
    from wsgi_seo_iframe import IframeReplacerMiddleware

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    application = get_wsgi_application()
    application = IframeReplacerMiddleware(application)


Requirements
============
This packege requires `PhantomJS <http://phantomjs.org/>`_
to be installed manually.

You can download a compatible version of PhantomJS
here: http://phantomjs.org/download.html

In Debian based systems you can install it using:
``sudo apt-get install phantomjs``

