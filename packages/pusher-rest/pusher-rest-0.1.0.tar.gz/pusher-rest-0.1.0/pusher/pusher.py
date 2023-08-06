# -*- coding: utf-8 -*-

from __future__ import (print_function, unicode_literals, absolute_import,
                        division)
from pusher.config import Config
from pusher.request import Request
from pusher.sync import SynchronousBackend
from pusher.util import GET, POST, text, validate_channel

import collections
import json
import six

class RequestMethod(object):
    def __init__(self, pusher, f):
        self.pusher = pusher
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.pusher.backend.send_request(self.make_request(*args, **kwargs))

    def make_request(self, *args, **kwargs):
        return self.f(self.pusher, *args, **kwargs)

def doc_string(doc):
    def decorator(f):
        f.__doc__ = doc
        return f
    return decorator

def request_method(f):
    @property
    @doc_string(f.__doc__)
    def wrapped(self):
        return RequestMethod(self, f)
    return wrapped

def join_attributes(attributes):
    for attr in attributes:
        if not isinstance(attr, six.text_type):
            raise TypeError('Each attr should be %s' % text)

    return six.text_type(',').join(attributes)

class Pusher(object):
    """Client for the Pusher HTTP API.

    This client supports various backend adapters to support various http
    libraries available in the python ecosystem. 

    :param config: a pusher.Config instance
    :param backend: an object that responds to the send_request(request)
                    method. If none is provided, a
                    python.sync.SynchronousBackend instance is created.
    """
    def __init__(self, config, backend=None):
        if not isinstance(config, Config):
            raise TypeError("config should be a pusher.Config object")
        self.backend = backend or SynchronousBackend(config)
        self.config = config

    @request_method
    def trigger(self, channels, event_name, data, socket_id=None):
        '''
        Trigger an event on one or more channels, see:

        http://pusher.com/docs/rest_api#method-post-event
        '''
        if isinstance(channels, six.string_types) or not isinstance(channels, (collections.Sized, collections.Iterable)):
            raise TypeError("Expected a collection of channels (each channel should be %s)" % text)

        if len(channels) > 10:
            raise ValueError("Too many channels")

        for channel in channels:
            validate_channel(channel)

        if not isinstance(event_name, six.text_type):
            raise TypeError("event_name should be %s" % text)

        if len(event_name) > 200:
            raise ValueError("event_name too long")

        if not isinstance(data, six.text_type):
            data = json.dumps(data)

        if len(data) > 10240:
            raise ValueError("Too much data")

        params = {
            'name': event_name,
            'channels': channels,
            'data': data
        }
        if socket_id:
            if not isinstance(socket_id, six.text_type):
                raise TypeError("Socket ID should be %s" % text)
            params['socket_id'] = socket_id
        return Request(self.config, POST, "/apps/%s/events" % self.config.app_id, params)

    @request_method
    def channels_info(self, prefix_filter=None, attributes=[]):
        '''
        Get information on multiple channels, see:

        http://pusher.com/docs/rest_api#method-get-channels
        '''
        params = {}
        if attributes:
            params['info'] = join_attributes(attributes)
        if prefix_filter:
            params['filter_by_prefix'] = prefix_filter
        return Request(self.config, GET, "/apps/%s/channels" % self.config.app_id, params)

    @request_method
    def channel_info(self, channel, attributes=[]):
        '''
        Get information on a specific channel, see:

        http://pusher.com/docs/rest_api#method-get-channel
        '''
        validate_channel(channel)

        params = {}
        if attributes:
            params['info'] = join_attributes(attributes)
        return Request(self.config, GET, "/apps/%s/channels/%s" % (self.config.app_id, channel), params)

    @request_method
    def users_info(self, channel):
        '''
        Fetch user ids currently subscribed to a presence channel

        http://pusher.com/docs/rest_api#method-get-users
        '''
        validate_channel(channel)

        return Request(self.config, GET, "/apps/%s/channels/%s/users" % (self.config.app_id, channel))
