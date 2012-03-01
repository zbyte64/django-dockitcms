from django import http

class HttpException(Exception):
    def __init__(self, response):
        #response = HttpResponse instance
        self.response = response

class HttpForbidden(HttpException):
    def __init__(self, *args, **kwargs):
        super(HttpForbidden, self).__init__(http.HttpResponseForbidden(*args, **kwargs))

