import json
import requests
import logging
from urllib.parse import urljoin

from ..exceptions import AuthenticationError, ResourceNotFoundError, InternalServerError, ConnectionError
from .. import settings

requests_log = logging.getLogger("requests")

if settings.REQUESTS_LOG_LEVEL == 'warning':
    requests_log.setLevel(logging.WARNING)
elif settings.REQUESTS_LOG_LEVEL == 'debug':
    requests_log.setLevel(logging.DEBUG)
elif settings.REQUESTS_LOG_LEVEL == 'info':
    requests_log.setLevel(logging.INFO)

JSON_HTTP_HEADERS = {'content-type': 'application/json'}

class RequestsMixin:
    def __init__(self):
        self.entity_id = ""
        self.api_key = ""
        self.session = requests.Session()
        self.connected = False
        
        self._add_hooks('pre_connect', 'post_connect', 'pre_disconnect', 'post_disconnect')


    def connect(self):
        """
        Register a connection with the HPIT Server.

        This essentially sets up a session and logs that you are actively using
        the system. This is mostly used to track plugin use with the site.
        """
        self._try_hook('pre_connect')

        connection = self._post_data('connect', {
                'entity_id': self.entity_id, 
                'api_key': self.api_key
            }
        )

        self.connected = True
        self._try_hook('post_connect')
       
        return self.connected


    def disconnect(self):
        """
        Tells the HPIT Server that you are not currently going to poll
        the server for messages or responses. This also destroys the current session
        with the HPIT server.
        """
        self._try_hook('pre_disconnect')
        
        self._post_data('disconnect', {
                'entity_id': self.entity_id,
                'api_key': self.api_key
            }
        )

        self.connected = False
        self._try_hook('post_disconnect')

        return self.connected


    def _post_data(self, url, data=None):
        """
        Sends arbitrary data to the HPIT server. This is mainly a thin
        wrapper ontop of requests that ensures we are using sessions properly.

        Returns: requests.Response : class - The response from HPIT. Normally a 200:OK.
        """
        url = urljoin(settings.HPIT_URL_ROOT, url)

        failure_count = 0
        while failure_count < 3:
            try:
                if data:
                    response = self.session.post(url, data=json.dumps(data), headers=JSON_HTTP_HEADERS)
                else:
                    response = self.session.post(url)
                break

            except requests.exceptions.ConnectionError:
                if failure_count == 3:
                    raise ConnectionError("Could not connect to server. Tried 3 times.")

                failure_count += 1
                continue

            except Exception:
                raise ConnectionError("The remote address is bogus.")
        
        if response.status_code == 200:
            return response
        elif response.status_code == 403:
            raise AuthenticationError("Request could not be authenticated")
        elif response.status_code == 404:
            raise ResourceNotFoundError("Requested resource not found")
        elif response.status_code == 500:
            raise InternalServerError("Internal server error")


    def _get_data(self, url):
        """
        Gets arbitrary data from the HPIT server. This is mainly a thin
        wrapper on top of requests that ensures we are using session properly.

        Returns: dict() - A Python dictionary representing the JSON recieved in the request.
        """
        url = urljoin(settings.HPIT_URL_ROOT, url)

        failure_count = 0
        while failure_count < 3:
            try:
                response = self.session.get(url)
                break

            except requests.exceptions.ConnectionError as e:
                if failure_count == 3:
                    raise e

                failure_count += 1
                continue

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            raise AuthenticationError("Request could not be authenticated")
        elif response.status_code == 404:
            raise ResourceNotFoundError("Requested resource not found")
        elif response.status_code == 500:
            raise InternalServerError("Internal server error")


    def send_log_entry(self, text):
        """
        Send a log entry to the HPIT server.
        """
        self._post_data("log", data={'log_entry':text})


    def _add_hooks(self, *hooks):
        """
        Adds hooks to this class. If the function is already defined, this leaves that definition. If 
        it doesn't exists the hook is created and set to None
        """
        for hook in hooks:
            if not hasattr(self, hook):
                setattr(self, hook, None)


    def _try_hook(self, hook_name):
        """
        Try's to call a signal hook. Hooks take in no parameters and return a boolean result.
        True will cause the plugin to continue execution.
        False will cause the plugon to stop execution.
        """
        hook = getattr(self, hook_name, None)

        if hook:
            return hook()
        else:
            return True

