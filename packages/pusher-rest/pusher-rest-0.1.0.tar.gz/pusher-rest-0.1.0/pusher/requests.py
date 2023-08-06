# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.util import process_response

import requests

class RequestsBackend(object):
    """Adapter for the requests module.

    :param config: an instance of pusher.Config
    :param options: key-value passed into the requests.request constructor
    """
    def __init__(self, config, **options):
        self.options = {'verify': True}
        self.options.update(options)

    def send_request(self, request):
        resp = requests.request(
            request.method,
            request.url,
            headers=request.headers,
            data=request.body,
            **self.options
        )
        return process_response(resp.status_code, resp.text)
