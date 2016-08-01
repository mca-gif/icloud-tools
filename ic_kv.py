#!/usr/bin/env python3

import argparse
import sys
from pprint import PrettyPrinter
import plistlib

from libs.icloudsettingsclient import ICloudSettingsClient
from libs.plistrequester import PlistRequester
from libs.keyvaluerequest import KeyValueRequest


class ICKV(object):
    def __init__(self, apple_id: str, password: str, bundle_id: str=""):
        self.apple_id = apple_id
        self.password = password
        self.bundle_id = bundle_id

        self.icloud_settings = None  # type: ICloudSettingsClient

    def get_icloud_settings(self) -> ICloudSettingsClient:
        if self.icloud_settings is None:
            try:
                self.icloud_settings = ICloudSettingsClient(self.apple_id, self.password)
            except RuntimeError as err:
                print(str(err))
                sys.exit(1)

        return self.icloud_settings

    def url(self) -> str:
        return "%s/sync" % (self.get_icloud_settings().url_for_feature("com.apple.Dataclass.KeyValue"))

    def query(self, kvstore_id: str) -> dict:
        query = PlistRequester(self.url(), "POST")
        query.set_authorization(self.get_icloud_settings().http_token_authorization())

        kvreq = KeyValueRequest(self.bundle_id)
        kvreq.add_app_store(kvstore_id)
        query.body = kvreq.dumps()

        return query.plist_as_dict()

    def query_keys(self, kvstore_id: str) -> dict:
        return self.query(kvstore_id)["apps"][0]["keys"]

    def empty(self, kvstore_id: str):
        data = self.query(kvstore_id)

        data["service-id"] = "iOS"
        data.pop("status", None)
        data.pop("timestamp", None)

        for app in data['apps']:
            app.pop("registry-status", None)

            for key in app["keys"]:
                key.pop("data", None)
                key["delete"] = True

        req = PlistRequester(self.url(), "POST")
        req.set_authorization(self.get_icloud_settings().http_token_authorization())

        req.body = plistlib.dumps(data)
        response = req.plist_as_dict()

        if response["status"] != 0:
            raise RuntimeError("An error occurred while deleting the keys.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='ic_kv.py')
    parser.add_argument("apple_id", type=str, default=None, help="Apple ID")
    parser.add_argument("password", type=str, default=None, help="Password")
    parser.add_argument("--bundle", dest='bundle_id', type=str, default='', help="Claim to be accessing the KV Store from this application.")
    parser.add_argument("--plist", dest="is_value_plist", action="store_true", default=False, help="The values are plist data and will be converted.")
    parser.add_argument("--empty", dest="should_empty", action="store_true", default=False, help=argparse.SUPPRESS)
    parser.add_argument("kvstore_id", type=str, default=None, help="Key-Store")
    args = parser.parse_args()

    kv_tool = ICKV(args.apple_id, args.password, args.bundle_id)

    print("Endpoint: %s" % kv_tool.url())

    if args.should_empty is True:
        kv_tool.empty(args.kvstore_id)
        sys.exit(0)


    pp = PrettyPrinter(indent=4, width=120, compact=False)

    for key in kv_tool.query_keys(args.kvstore_id):
        print("Key: %s" % key["name"])
        to_print = key["data"]

        if args.is_value_plist is True:
            bdata = bytes(key['data'])
            plist_pos = bdata.find(b"bplist00")
            if plist_pos != -1:
                to_print = plistlib.loads(bdata[plist_pos:])

        pp.pprint(to_print)