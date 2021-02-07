import configparser
import urllib.request
from urllib.error import HTTPError
import ssl
import json

config = configparser.ConfigParser()
config.read('tenable.ini')
downloads_config = config['downloads']
tio_config = config['tenable_io']
tsc_config = config['tenable_sc']


def request(method, host, endpoint, headers=None, data=None, proxy=None, verify=None):
    request_ = urllib.request.Request('https://' + host + endpoint)
    request_.method = method
    request_.add_header('accept', 'application/json')
    request_.add_header('content-type', 'application/json')
    context = ''
    if headers:
        for key, value in headers.items():
            request_.add_header(key, value)
    if data:
        request_.data = json.dumps(data).encode()
    if proxy:
        request_.set_proxy(proxy, 'https')
    if verify is False:
        # https://www.python.org/dev/peps/pep-0476
        context = ssl._create_unverified_context()
    try:
        response = urllib.request.urlopen(request_, context=context)
        return response
    except HTTPError as error:
        print('\nERROR: HTTP ' + str(error.code) + ' - https://' + host + endpoint)
        print(error.reason)


def auth_error(msg='ERROR: Invalid authentication data'):
    print(msg)
    quit()


class Downloads:
    def __init__(self, bearer_token=None, proxy=None, verify=True):
        # Set connection data in order of preference
        self.host = 'www.tenable.com'
        self.bearer_token = bearer_token
        self.proxy = proxy
        self.verify = verify
        if self.bearer_token:
            pass
        elif config.has_option('downloads', 'bearer_token'):
            self.bearer_token = config.get('downloads', 'bearer_token')
            if config.has_option('downloads', 'proxy'):
                self.proxy = config.get('downloads', 'proxy')
            else:
                self.proxy = None
            if config.has_option('downloads', 'verify'):
                self.verify = config.getboolean('downloads', 'verify')
            else:
                self.verify = True
        else:
            auth_error()

        # Create authentication headers
        self.headers = {
            "Host": "www.tenable.com",
            "User-agent": "Mozilla/5.0",
            "Authorization": "Bearer " + self.bearer_token
        }

    def request(self, endpoint):
        endpoint = '/downloads/api/v2' + endpoint
        response = request('GET', self.host, endpoint, self.headers, None, self.proxy, self.verify)
        return response


class TenableIO:
    def __init__(self, access_key=None, secret_key=None, username=None, password=None,
                 proxy=None, verify=True):
        # Set connection data in order of preference
        self.host = 'cloud.tenable.com'
        self.access_key = access_key
        self.secret_key = secret_key
        self.username = username
        self.password = password
        self.proxy = proxy
        self.verify = verify
        if self.access_key and self.secret_key:
            pass
        elif self.username and self.password:
            pass
        elif config.has_option('tenable_io', 'access_key') and config.has_option('tenable_io', 'secret_key'):
            self.access_key = config.get('tenable_io', 'access_key')
            self.secret_key = config.get('tenable_io', 'secret_key')
            if config.has_option('tenable_io', 'proxy'):
                self.proxy = config.get('tenable_io', 'proxy')
            else:
                self.proxy = None
            if config.has_option('tenable_io', 'verify'):
                self.verify = config.getboolean('tenable_io', 'verify')
            else:
                self.verify = True
        else:
            auth_error()

        # Create authentication headers
        if self.access_key and self.secret_key:
            self.headers = {"x-apikeys": "accessKey=" + self.access_key + ';secretKey=' + self.secret_key}
        else:
            auth = self._login()
            self.headers = {"x-cookie": "token=" + auth['token']}

    def request(self, method, endpoint, data=None):
        response = request(method, self.host, endpoint, self.headers, data, self.proxy, self.verify)
        return response

    def _login(self):
        response = request('POST', self.host, '/session', data={"username": self.username, "password": self.password},
                           proxy=self.proxy, verify=self.verify)
        return json.load(response)

    def logout(self):
        request('DELETE', self.host, '/session', self.headers, proxy=self.proxy, verify=self.verify)


class TenableSC:
    def __init__(self, host=None, access_key=None, secret_key=None, username=None, password=None,
                 proxy=None, verify=True):
        # Set connection data in order of preference
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key
        self.username = username
        self.password = password
        self.proxy = proxy
        self.verify = verify
        if self.host and self.access_key and self.secret_key:
            pass
        elif self.host and self.username and self.password:
            pass
        elif (config.has_option('tenable_sc', 'host') and config.has_option('tenable_sc', 'access_key')
                and config.has_option('tenable_sc', 'secret_key')):
            self.host = config.get('tenable_sc', 'host')
            self.access_key = config.get('tenable_sc', 'access_key')
            self.secret_key = config.get('tenable_sc', 'secret_key')
            if config.has_option('tenable_sc', 'proxy'):
                self.proxy = config.get('tenable_sc', 'proxy')
            else:
                self.proxy = None
            if config.has_option('tenable_sc', 'verify'):
                self.verify = config.getboolean('tenable_sc', 'verify')
            else:
                self.verify = True
        else:
            auth_error()

        # Create authentication headers
        if self.access_key and self.secret_key:
            self.headers = {"x-apikey": "accesskey=" + self.access_key + "; secretkey=" + self.secret_key}
        else:
            auth = self._login()
            self.headers = {"X-SecurityCenter": auth['token'], 'Cookie': auth['cookie']}

    def request(self, method, endpoint, data=None):
        endpoint = '/rest' + endpoint
        response = request(method, self.host, endpoint, self.headers, data, self.proxy, self.verify)
        return response

    def _login(self):
        response = request('GET', self.host, '/rest/system', proxy=self.proxy, verify=self.verify)
        cookie = response.headers['Set-Cookie'].split(';', 1)[0]
        response = request('POST', self.host, '/rest/token', headers={"Cookie": cookie},
                           data={"username": self.username, "password": self.password},
                           proxy=self.proxy, verify=self.verify)
        token = json.load(response)['response']['token']
        cookie = response.headers['Set-Cookie'].split(';', 1)[0]
        return {'token': token, 'cookie': cookie}

    def logout(self):
        self.request('DELETE', '/token')
