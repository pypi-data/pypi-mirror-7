import datetime
import json
import logging
import os
import random
import sys
import time

try:
    from cloghandler import (
        ConcurrentRotatingFileHandler as RotatingFileHandler
    )
except ImportError:
    from logging.handlers import RotatingFileHandler 

import requests
from requests.exceptions import ConnectionError

class MultyvacError(Exception):
    pass

class RequestError(MultyvacError):
    """Exception class for errors when making web requests to the
    Multyvac API."""

    def __init__(self, http_status_code, code, message, hint=None,
                 retry=False):
        Exception.__init__(self, http_status_code, code, message, hint, retry)
        self.http_status_code = http_status_code
        self.code = code
        self.message = message
        self.hint = hint
        self.retry = retry
    
    def __str__(self):
        return '%s (Code: %s Hint: %s)' % (self.message, self.code, self.hint)
    
    def __repr__(self):
        return 'RequestError({code}, "{message}", {hint})'.format(
                    code=self.code,
                    message=self.message,
                    hint=self.hint,
                )

class Multyvac(object):
    """
    Multyvac

    The primary object for interacting with the Multyvac API.
    All Multyvac modules are exposed through this.
    """
    
    _ASK_GET = 'GET'
    _ASK_POST = 'POST'
    _ASK_PUT = 'PUT'
    
    def __init__(self, api_key=None, api_secret_key=None, api_url=None):
        self._session = requests.session()
        
        from .config import ConfigModule
        # Note: At this time, the rest of the Multyvac modules have not been
        # initialized. So the constructor should not do anything that requires
        # any other modules (ie. Do not use the ApiKey module).
        self.config = ConfigModule(self, api_key, api_secret_key, api_url)
        
        # Must be after config
        self._setup_logger()
        
        from .job import JobModule
        self.job = JobModule(self)
        from .layer import LayerModule
        self.layer = LayerModule(self)
        from .volume import VolumeModule
        self.volume = VolumeModule(self)
        from .cluster import ClusterModule
        self.cluster = ClusterModule(self)
        from .api_key import ApiKeyModule
        self.api_key = ApiKeyModule(self)
    
    def _setup_logger(self):
        """
        Sets up a rotating file logger.
        TODO: Have config option for printing to screen.
        """
        
        logs_path = os.path.join(self.config.get_multyvac_path(), 'log')
        if not os.path.exists(logs_path):
            self.config._create_path_ignore_existing(logs_path)
        log_path = os.path.join(logs_path, 'multyvac.log')
            
        self._logger = logging.getLogger('multyvac')
        self._logger.setLevel(logging.INFO)
    
        try:
            handler = RotatingFileHandler(log_path, 'a', 1024*1024, 10)
        except OSError as e:
            if e.errno == 13:
                # Assume the permission denied is because the log is owned by
                # a different user (probably due to sudo). Use a different log
                # file with the user's uid embedded.
                # TODO: send_log_to_support() does not handle this case.
                log_path = os.path.join(logs_path,
                                        'multyvac.%s.log' % os.getuid())
                handler = RotatingFileHandler(log_path, 'a', 1024*1024, 10)
        # TODO: Fixing the permissions here only helps so much. If the user ran
        # this as sudo, the rotated logs will be owned by sudo's target user.
        # Our only option is to modify RotatingFileHandler to try to set the
        # calling user as the owner.
        self.config._fix_permission(log_path)
        lock_path = os.path.join(logs_path, 'multyvac.lock')
        self.config._fix_permission(lock_path)
        
        formatter = logging.Formatter(
            '[%(asctime)s] - [%(levelname)s] - %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
    
    def _get_session_method(self, method):
        if method == self._ASK_POST:
            return self._session.post
        elif method == self._ASK_GET:
            return self._session.get
        elif method == self._ASK_PUT:
            return self._session.put
        else:
            raise KeyError('Unknown method "%s"' % method)
    
    def _log_ask(self, method, uri, params, data, headers, files):
        """Use this to log a request.  It only logs params and data elements
        that are not overly large to prevent filling up the log."""
        self._logger.info('%s request to %s with params %r data %r files %r',
                          method,
                          uri,
                          self._log_ask_element(params),
                          self._log_ask_element(data),
                          [path for path, _ in files.values()] if files else None)
    
    def _log_ask_element(self, ele):
        """Recurses into dict and list objects replacing elements that are too
        large for a log file. This way we still see small elements, but filter
        our large things like stdin."""
        max_element_byte_size = 150
        ele_size = sys.getsizeof(ele)
        if isinstance(ele, dict):
            d = {}
            for k, v in ele.items():
                d[k] = self._log_ask_element(v)
            return d
        elif isinstance(ele, (tuple, list)):
            return [self._log_ask_element(v) for v in ele]
        elif ele_size > max_element_byte_size:
            return 'Too large to log: %s bytes' % ele_size
        else:
            return ele
    
    def _ask(self, method, uri, auth=None, params=None, data=None,
             headers=None, files=None, content_type_json=False):
        """
        Makes an HTTP request to Multyvac.
        
        :param method: HTTP Verb.
        :param uri: Resource path.
        :param auth: Authentication override. If not specified, falls back to
            any credentials available in the MultyvacConfigModule.
        :param params: Query string parameters specified as a dict.
        :param data: Specify as dict. If not a JSON request, the dict is
            form encoded and put into the body (typical POST). If its a JSON
            request, then the data is serialized JSON in the request body.
        :param files: List of tuples [(path, content), ...] specifying files
            that should be uploaded as part of a multipart request.
        :param content_type_json: Whether the request body should be encoded as
            JSON, along with the appropriate content-type header. If False,
            regular form encoding is used.
        """
        if content_type_json:
            headers = headers or {}
            headers['content-type'] = 'application/json'
            final_data = json.dumps(data)
        else:
            final_data = data
        
        attempt = 0
        max_attempts = 5
        while True:
            self._log_ask(method, uri, params, data, headers, files)
            try:
                r = self._ask_helper(method,
                                     uri,
                                     auth=auth,
                                     params=params,
                                     data=final_data,
                                     headers=headers,
                                     files=files)
                return r
            except (RequestError, ConnectionError) as e:
                attempt += 1
                if isinstance(e, RequestError) and e.http_status_code == 429:
                    # Add another attempt if error was due to rate limiting.
                    # This also increases the range of exponential backoff.
                    max_attempts += 1
                if ((isinstance(e, ConnectionError) or e.retry)
                        and attempt < max_attempts):
                    delay = 2**attempt * random.random()
                    self._logger.info('Request failed. Retrying in %.1fs',
                                      delay)
                    time.sleep(delay)
                    continue
                else:
                    raise
    
    def _ask_helper(self, method, uri, auth, params, data, headers, files):
        
        if not auth:
            auth = self.config.get_auth()
        
        r = self._get_session_method(method)(
                self.config.api_url + uri,
                auth=auth,
                params=params,
                data=data,
                headers=headers,
                files=files,
            )
        
        try:
            obj = r.json()
        except ValueError:
            raise RequestError(500,
                               None,
                               'Unknown error',
                               hint=r.text)
        if 'error' in obj:
            raise RequestError(r.status_code,
                               obj['error']['code'],
                               obj['error']['message'],
                               obj['error'].get('hint'),
                               obj['error'].get('retry'))
        
        return obj
        
    def on_multyvac(self):
        """Returns True if this process is currently running on Multyvac."""
        return os.getenv('ON_MULTYVAC') == 'true'
    
    def send_log_to_support(self):
        """Sends this machine's log file to Multyvac support."""
        log_path = os.path.join(self.config.get_multyvac_path(),
                                'log/multyvac.log')
        if os.path.exists(log_path):
            with open(log_path) as f:
                files = {'file': ('multyvac.log', f.read())}
            self._ask(self._ASK_POST,
                      '/report/client_log/',
                      files=files)
            return True
        else:
            return False

class MultyvacModule(object):
    """All modules should extend this class."""
    def __init__(self, multyvac):
        self.multyvac = multyvac
        logger_name = self.__class__.__name__.lower()[:-len('module')]
        self._logger = logging.getLogger('multyvac.%s' % logger_name)

    @staticmethod
    def clear_null_entries(d):
        for k, v in d.items():
            if v is None:
                del d[k]

    @staticmethod
    def convert_str_to_datetime(s):
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # FIXME
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def check_success(r):
        return r['status'] == 'ok'
    
    @staticmethod
    def is_iterable_list(obj):
        return hasattr(obj, '__iter__')


class MultyvacModel(object):
    def __init__(self, multyvac=None, **kwargs):
        if multyvac:
            self.multyvac = multyvac
        else:
            raise Exception('Needs multyvac object for now')
            
    def __str__(self):
        return repr(self)

