"""A class implementation of code found in
https://github.com/hackappcom/iloot"""

from xml.parsers.expat import ExpatError
from urllib.parse import urlparse
import plistlib
import http.client as http


class PlistRequester(object):
    """A class to make requesting plist data from a webserver easier"""
    def __init__(self, url, method="GET"):
        self.url = url
        self.method = method
        self.body = None
        self.headers = {}
        self.data = None

        self.headers['User-Agent'] = "iPhone OS 8.1.2 (12B440)"
        self.headers['X-MMe-Client-Info'] = "<iPhone7,2> <iPhone OS;8.1.2;12B440> <com.apple.SyncedDefaults/207.2>"

    def add_header(self, key, value):
        """Allows adding new values to the headers"""
        self.headers[key] = value

    def set_authorization(self, auth_value):
        self.add_header("Authorization", auth_value)

    def plist_as_dict(self):
        """Makes the network request and returns data"""
        if self.data:
            return self.data

        purl = urlparse(self.url)
        if purl.scheme == "https":
            conn = http.HTTPSConnection(purl.hostname, purl.port)
        else:
            conn = http.HTTPConnection(purl.hostname, purl.port)

        conn.request(self.method, purl.path, self.body, self.headers)
        response = conn.getresponse()

        data = response.read()
        try:
            self.data = plistlib.loads(data)
        except ExpatError:
            self.data = None

        if response.status != 200:
            print("Request %s returned code %d" % (self.url, response.status))
            return None

        return self.data
