backports.method_request
========================

A backport of the urllib.request.MethodRequest class from Python 3.4 which
allows overriding of the method in a class attribute or as a keyword
parameter to the initializer.

See `Python 18978 <http://bugs.python.org/issue18978>`_ for details.

Works on Python 2.6 and later.

Usage
-----

Use ``method_request.Request`` in place of ``urllib.request.Request``::

    from backports.method_request import Request

    req = Request(..., method='PATCH')
    resp = urllib.request.urlopen(req)
    ...
