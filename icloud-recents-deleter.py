#!/usr/bin/env python
"""Deletes all recent contacts from iCloud message history"""

from icloudsettingsclient import ICloudSettingsClient
from plistrequester import PlistRequester
import sys, argparse
import plistlib

parser = argparse.ArgumentParser(prog='icloud-recents-deleter.py')
parser.add_argument("apple_id", type=str, default=None, help="Apple ID")
parser.add_argument("password", type=str, default=None, help="Password")

args = parser.parse_args()


### GAIN ACCESS TO ICLOUD
try:
    icloud_settings = ICloudSettingsClient(args.apple_id, args.password)
except RuntimeError as err:
    print str(err)
    sys.exit(1)

sync_url = "%s/sync" % (icloud_settings.url_for_feature("com.apple.Dataclass.KeyValue"))

kvstores = ["com.apple.messages.recents", "com.apple.mail.recents", "com.apple.MapsSupport.history"]

for kvstore_id in kvstores:
    ### RETRIEVE CURRENT RECENTS LIST
    request_body = {
        "service-id": "iOS",
        "apps": [
            {
                "bundle-id":"com.apple.cloudrecents.CloudRecentsAgent",
                "kvstore-id":kvstore_id,
                "registry-version":""
            }
        ]
    }

    recents_request = PlistRequester(sync_url)
    recents_request.method = "POST"
    recents_request.add_header('Authorization', icloud_settings.http_token_authorization())
    recents_request.body = plistlib.writePlistToString(request_body)
    recents_data = recents_request.plist_data()



    ### RE-WRITE DATA AS A DELETION
    # Configure the plist so we can re-submit it
    recents_data["service-id"] = "iOS"
    recents_data.pop('status', None)
    recents_data.pop('timestamp', None)
    recents_data['apps'][0].pop('registry-status', None)

    # Mark all keys for deletion
    for recent_contact in recents_data['apps'][0]['keys']:
        recent_contact.pop('data', None)
        recent_contact['delete'] = True



    ### SEND DATA BACK TO SERVER
    # Clear data to force a new request
    recents_request.data = None
    recents_request.body = plistlib.writePlistToString(recents_data)
    response = recents_request.plist_data()

    if response['status'] == 0:
        print "Successfully deleted %s" % (kvstore_id)
    else:
        print "An error occurred while deleting %s" % (kvstore_id)
        sys.exit(2)
