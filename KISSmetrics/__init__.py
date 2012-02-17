"""
Example usage:

km = KM('my-api-key')
km.identify('simon')
km.record('an event', {'attr': '1'})
"""

import urllib
import socket
import httplib
from datetime import datetime

class KM(object):
    
    def __init__(self, key, host='trk.kissmetrics.com:80', http_timeout=2,
                 logging=True, fail_silently=True):
        self._id = None
        self._key    = key
        self._host = host
        self._http_timeout = http_timeout
        self._logging = logging
        self._silent = fail_silently

    def identify(self, id):
        self._id = id

    def record(self, action, props=None):
        if props is None:
            props = {}
        self.check_id_key()
        if isinstance(action, dict):
            self.set(action)

        props.update({'_n': action})
        self.request('e', props)

    def set(self, data):
        self.check_id_key()
        self.request('s',data)

    def alias(self, name, alias_to):
        self.check_init()
        self.request('a', {'_n': alias_to, '_p': name}, False)

    def log_file(self):
        return '/tmp/kissmetrics_error.log'

    def reset(self):
        self._id = None
        self._key = None

    def check_identify(self):
        if self._id is None:
            raise Exception, "Need to identify first (KM.identify <user>)"

    def check_init(self):
        if self._key is None:
            raise Exception, "Need to initialize first (KM.init <your_key>)"

    def now(self):
        return datetime.utcnow()

    def check_id_key(self):
        self.check_init()
        self.check_identify()

    def logm(self, msg):
        if not self._logging:
            return
        msg = self.now().strftime('<%c> ') + msg
        try:
            fh = open(self.log_file(), 'a')
            fh.write(msg)
            fh.close()
        except IOError:
            pass #just discard at this point

    def request(self, type, data, update=True):
        query = []

        # if user has defined their own _t, then include necessary _d
        if '_t' in data:
            data['_d'] = 1
        else:
            data['_t'] = self.now().strftime('%s')

        # add customer key to data sent
        data['_k'] = self._key

        if update:
            data['_p'] = self._id

        try:
            connection = httplib.HTTPConnection(self._host, timeout=self._http_timeout)
            data_str = '/%s?%s' % (type, urllib.urlencode(data))
            connection.request('GET', data_str)
            r = connection.getresponse()
        except Exception, e:
            err_msg = "Could not transmit to %s, error %s, data str %s"\
                      % (self._host, e, data_str)
            self.logm(err_msg)
            if not self._silent:
                connection.close()
                raise Exception, err_msg
        finally:
            connection.close()

