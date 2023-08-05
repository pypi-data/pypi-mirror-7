"""
this is the client api it's mostly sugar
"""
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    basestring
except NameError:
    basestring = str

from . import filters
from webob.client import send_request_app


from webob import Request


def client_pipeline(app=send_request_app,
                     cookie_support=True,
                     content_decoding=True,
                     logging=False, log_level=None):
    """
       :rtype: pre-configured :ref:`wsgi_application`

       :param app: is a :ref:`wsgi_application` to wrap, the default
       is :ref:`webob.client.send_request_app`

       :param cookie_support: enables/disables the
       :func:`filters.cookie_filter`

       :param content_decoding: enables/disables the
       :func:`filters.decode_filter`

       :param logging: enables/disables the :func:`filters.http_log_filter`

       :param log_level: the log_level for :func:`filters.http_log_filter`
    """
    if content_decoding:
        wsgi = filters.decode_filter(app)

    if logging:
        if log_level:
            wsgi = filters.http_log_filter(wsgi, level=log_level)
        else:
            wsgi = filters.http_log_filter(wsgi)

    if cookie_support:
        wsgi = filters.cookie_filter(wsgi)

    wsgi = filters.charset_filter(wsgi)
    return wsgi

client_app = client_pipeline()


class Client(object):
    """
    :param pipeline: wsgi application to pass requests to, default is
    :func:`client.client_app`

    :param assert_: a callback lambda: request, response: True that
    will be called for every call to app
    """

    def __init__(self, pipeline=None, assert_=None):
        self._pipeline = pipeline or client_pipeline()
        if assert_:
            self._assert_ = assert_
        else:
            self._assert_ = None

    def get(self, url, query_string=None, headers={}, assert_=None):
        """
        make an HTTP GET Request and return the response

        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param query_string: the querystring dict which will be
        urlencoded for you

        :param headers: extra headers for the request

        :param assert: a callback to be ran after the response is
        recieved in the form of lambda: request, response: True . If
        present it will be ran for this call only rather than the one
        set on the client
        """

        return self(url=url,
                    method="GET",
                    query_string=query_string,
                    headers=headers,
                    assert_=assert_)

    def head(self, url, query_string=None, headers={}, assert_=None):
        """make an HTTP HEAD Request and return the response

        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param query_string: the querystring dict which will be urlencoded for you

        :param headers: extra headers for the request

        :param assert: a callback to be ran after the response is
        recieved in the form of lambda: request, response: True . If
        present it will be ran for this call only rather than the one
        set on the client

        """

        return self(url=url,
                    method="HEAD",
                    query_string=query_string,
                    headers=headers,
                    assert_=assert_)

    def post(self, url, query_string=None, post={}, headers={}, assert_=None, files={}):
        """
        make an HTTP POST Request and return the response

        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param query_string: the querystring dict which will be
        urlencoded for you

        :param post: form post

        :param headers: extra headers fpr the request

        :param assert: a callback to be ran after the response is
        recieved in the form of lambda: request, response: True . If
        present it will be ran for this call only rather than the one
        set on the client
        """
        for k, v in files.items():
            try:
                filename, filevalue = v
            except ValueError:
                raise ValueError("files needs to contain 2 item sequences of (filename, filebody) %s" % v)

            if k not in post:
                post[k] = (filename, filevalue)
            else:
                raise KeyError("%s already exists in post" % k)

        return self(url=url,
                    method="POST",
                    query_string=query_string,
                    post=post,
                    headers=headers,
                    assert_=assert_)


    def put(self, url, query_string=None, post={}, headers={}, assert_=None):
        """
        make an HTTP PUT Request and return the response

        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param query_string: the querystring dict which will be
        urlencoded for you

        :param post: form post

        :param headers: extra headers fpr the request

        :param assert: a callback to be ran after the response is
        recieved in the form of lambda: request, response: True . If
        present it will be ran for this call only rather than the one
        set on the client
        """
        return self(url=url,
                    method="PUT",
                    query_string=query_string,
                    post=post,
                    headers=headers,
                    assert_=assert_)

    def delete(self, url, query_string=None, post={}, headers={}, assert_=None):
        """
        make an HTTP DELETE Request and return the response

        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param query_string: the querystring dict which will be urlencoded for you

        :param post: form post

        :param headers: extra headers fpr the request

        :param assert: a callback to be ran after the response is recieved in the form of lambda: request, response: True . If present it will be ran for this call only rather than the one set on the client
        """
        return self(url=url,
                    method="DELETE",
                    query_string=query_string,
                    post=post,
                    headers=headers,
                    assert_=assert_)

    def options(self, url, query_string=None, post={}, headers={}, assert_=None):
        """
        make an HTTP OPTIONS Request and return the response

        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param query_string: the querystring dict which will be urlencoded for you

        :param post: form post

        :param headers: extra headers fpr the request

        :param assert: a callback to be ran after the response is recieved in the form of lambda: request, response: True . If present it will be ran for this call only rather than the one set on the client
        """
        return self(url=url,
                    method="OPTIONS",
                    query_string=query_string,
                    post=post,
                    headers=headers,
                    assert_=assert_)

    def __call__(self, url, method="get", query_string=None, post=None, headers={}, assert_=None):
        """
        :rtype: :class:`webob.Response`

        :param url: the url for the request

        :param method: the method for the request

        :param query_string: the querystring dict which will be urlencoded for you

        :param post: form post

        :param headers: extra headers fpr the request

        :param assert: a callback to be ran after the response is recieved
        in the form of lambda: request, response: True . If present it
        will be ran for this call only rather than the one set on the
        client
        """
        request = self._make_request(url=url,
                                  method=method.upper(),
                                  query_string=query_string,
                                  post=post,
                                  headers=headers)
        response = request.send(self._pipeline)

        if assert_:
            assert_(request.copy(), response.copy())
        else:
            if self._assert_:
                self._assert_(request.copy(), response.copy())

        return response

    @classmethod
    def _make_request(cls, url, method="get", query_string=None, post=None, headers={}):
        """
        :rtype: :class:`webob.Request`

        :param url: the url for the request

        :param method: the method for the request

        :param query_string: the querystring dict which will be
        urlencoded for you or left alone if it's a string, ignored if
        there is a querystring portion on the url already

        :param post: form post

        :param headers: extra headers for the request
        """
        kw = {}

        if query_string and hasattr(query_string, "keys"):  # dict-like
            kw["query_string"] = dict_to_qs(query_string)
        elif query_string:  # treat as string /punt
            kw["query_string"] = str(query_string)

        if headers:
            kw["headers"] = headers.items()

        if method:
            kw["method"] = method.upper()

        if post:
            kw["POST"] = post

        kw = {k: v for k, v in kw.items() if v}
        return Request.blank(url, **kw)


def stringify_dict(d):
    """make sure all values are something urlencodeable"""
    if hasattr(d, "mixed"):
        d_iter = d.mixed().items
    else:
        d_iter = d.items
    for key, value in d_iter():
        if not isinstance(value, list):
            d[key] = _str(value)
        else:
            del d[key]
            for i in value:
                d.add(key, _str(i))

    return d


def dict_to_qs(d):
    return urlencode(stringify_dict(d))


def _str(v, charset="utf-8"):
    if isinstance(v, basestring):
        return v.encode(charset)
    else:
        return str(v).encode(charset)  # punt
