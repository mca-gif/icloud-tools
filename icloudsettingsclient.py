from plistrequester import PlistRequester
import base64

class ICloudSettingsClient(object):
    """Implements a client to authorize and retrieve settings from iCloud"""
    def __init__(self, apple_id, password):
        self.url = "https://setup.icloud.com/setup/get_account_settings"

        self.apple_id = apple_id
        self.password = password
        self.data = None

        self.request()
        if self.data == None:
            raise RuntimeError("Unable to download settings from iCloud")

    def request(self):
        """Actually process the request of settings"""
        if self.data != None:
            return

        requester = PlistRequester(self.url)

        basic_auth = "Basic %s" % base64.b64encode("%s:%s" % (self.apple_id, self.password))
        requester.add_header('Authorization', basic_auth)

        self.data = requester.plist_data()

    def person_id(self):
        """Return the user's Directory Services Person ID"""
        return self.data['appleAccountInfo']['dsPrsID']

    def mme_auth_token(self):
        return self.data['tokens']['mmeAuthToken']

    def http_token_authorization(self):
        """Returns a string fit for using as an HTTP authorization string"""
        return "X-MobileMe-AuthToken %s" % (base64.b64encode("%s:%s" % (self.person_id(), self.mme_auth_token())))

    def available_features(self):
        return self.data['com.apple.mobileme']['availableFeatures']

    def url_for_feature(self, feature_id):
        return self.data['com.apple.mobileme'][feature_id]['url']
