'''
A Python library for working with Salt's REST API

(Specifically the rest_cherrypy netapi module.)

'''
import functools
import json
import logging
import os
import urllib
import urllib2
import urlparse

logger = logging.getLogger(__name__)

class PepperException(Exception): pass

class Pepper(object):
    '''
    A thin wrapper for making HTTP calls to the salt-api rest_cherrpy REST
    interface

    >>> api = Pepper('http://localhost:8000')
    >>> api.login('saltdev', 'saltdev', 'pam')
    {"return": [
            {
                "eauth": "pam",
                "expire": 1370434219.714091,
                "perms": [
                    "test.*"
                ],
                "start": 1370391019.71409,
                "token": "c02a6f4397b5496ba06b70ae5fd1f2ab75de9237",
                "user": "saltdev"
            }
        ]
    }
    >>> api.low([{'client': 'local', 'tgt': '*', 'fun': 'test.ping'}])
    {u'return': [{u'ms-0': True,
              u'ms-1': True,
              u'ms-2': True,
              u'ms-3': True,
              u'ms-4': True}]}

    '''
    def __init__(self, api_url='http://localhost:8000', debug_http=False):
        '''
        Initialize the class with the URL of the API

        :param api_url: Host or IP address of the salt-api URL;
            include the port number

        :param debug_http: Add a flag to urllib2 to output the HTTP exchange
        '''
        self.api_url = api_url
        self.debug_http = debug_http
        self.auth = {}

    def req(self, path, data=None):
        '''
        A thin wrapper around urllib2 to send requests and return the response

        If the current instance contains an authentication token it will be
        attached to the request as a custom header.

        :rtype: dictionary

        '''
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }

        handler=urllib2.HTTPHandler(debuglevel=1 if self.debug_http else 0)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # Build POST data
        if data != None:
            postdata = json.dumps(data).encode()
            clen = len(postdata)

        # Create request object
        url = urlparse.urljoin(self.api_url, path)
        req = urllib2.Request(url, postdata, headers)

        # Add POST data to request
        if data != None:
            req.add_header('Content-Length', clen)

        # Add auth header to request
        if self.auth and 'token' in self.auth and self.auth['token']:
            req.add_header('X-Auth-Token', self.auth['token'])

        # Send request
        try:
            f = urllib2.urlopen(req)
            ret = json.loads(f.read())
        except (urllib2.HTTPError, urllib2.URLError) as e:
            logger.debug('Error with request ' + str(e), exc_info=True)
            ret = {}
        except AttributeError:
            logger.debug('Error converting response from JSON', exc_info=True)
            ret = {}

        return ret

    def low(self, lowstate, path='/'):
        '''
        Execute a command through salt-api and return the response

        :param string path: URL path to be joined with the API hostname

        :param list lowstate: a list of lowstate dictionaries
        '''
        return self.req(path, lowstate)

    def local(self, tgt, fun, arg=None, kwarg=None, expr_form='glob',
            timeout=None, ret=None):
        '''
        Run a single command using the ``local`` client

        Wraps :meth:`low`.
        '''
        low = {
            'client': 'local',
            'tgt': tgt,
            'fun': fun,
        }

        if arg:
            low['arg'] = arg

        if kwarg:
            low['kwarg'] = kwarg

        if expr_form:
            low['expr_form'] = expr_form

        if timeout:
            low['timeout'] = timeout

        if ret:
            low['ret'] = ret

        return self.low([low], path='/')

    def local_async(self, tgt, fun, arg=None, kwarg=None, expr_form='glob', timeout=None, ret=None):
        '''
        Run a single command using the ``local_async`` client

        Wraps :meth:`low`.
        '''
        low = {
            'client': 'local_async',
            'tgt': tgt,
            'fun': fun,
        }

        if arg:
            low['arg'] = arg

        if kwarg:
            low['kwarg'] = kwarg

        if expr_form:
            low['expr_form'] = expr_form

        if timeout:
            low['timeout'] = timeout

        if ret:
            low['ret'] = ret

        return self.low([low], path='/')

    def lookup_jid(self, jid):
        '''
        Get job results

        Wraps :meth:`low`.
        '''
        low = {
            'client': 'runner',
            'fun': 'jobs.lookup_jid',
            'jid': jid
        }

        return self.low([low], path='/')

    def login(self, username, password, eauth):
        '''
        Authenticate with salt-api and return the user permissions and
        authentication token or an empty dict

        '''
        self.auth = self.req('/login', {
            'username': username,
            'password': password,
            'eauth': eauth}).get('return', [{}])[0]

        return self.auth
