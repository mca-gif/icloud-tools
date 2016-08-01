import base64
from libs.plistrequester import PlistRequester


class ICloudSettingsClient(object):
    """Implements a client to authorize and retrieve settings from iCloud"""
    def __init__(self, apple_id, password):
        self.url = "https://setup.icloud.com/setup/get_account_settings"

        self.apple_id = apple_id
        self.password = password
        self.data = None

        self.request()
        if self.data is None:
            raise RuntimeError("Unable to download settings from iCloud")

    @staticmethod
    def __encode_basic_auth_value(username: str, password: str) -> str:
        basic_auth_value = "%s:%s" % (username, password)
        basic_auth_value_b64 = base64.b64encode(basic_auth_value.encode(encoding="UTF-8"))
        return basic_auth_value_b64.decode(encoding="UTF-8")

    def request(self):
        """Actually process the request of settings"""
        if self.data is not None:
            return

        requester = PlistRequester(self.url)
        requester.add_header('Authorization', "Basic %s" % self.__encode_basic_auth_value(self.apple_id, self.password))

        self.data = requester.plist_as_dict()

    def person_id(self) -> str:
        """Return the user's Directory Services Person ID"""
        return self.data['appleAccountInfo']['dsPrsID']

    def mme_auth_token(self) -> str:
        """Returns an authorized iCloud (MobileMe) token"""
        return self.data['tokens']['mmeAuthToken']

    def http_token_authorization(self) -> str:
        """Returns a string fit for using as the value of a HTTP Authorization header"""
        return "X-MobileMe-AuthToken %s" % self.__encode_basic_auth_value(self.person_id(), self.mme_auth_token())

    def available_features(self) -> list:
        """Returns a list of strings indicating what features are available."""
        return self.data['com.apple.mobileme']['availableFeatures']

    def url_for_feature(self, feature_id: str) -> str:
        """Returns a URL for the given feature from the list of available features."""
        return self.data['com.apple.mobileme'][feature_id]['url']
