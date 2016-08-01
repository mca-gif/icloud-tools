import plistlib


class KeyValueRequest(object):
    def __init__(self, bundle_id: str=""):
        self.bundle_id = bundle_id
        self.data = dict()
        self.data["service-id"] = "iOS"
        self.data["apps"] = list()

    def add_app_store(self, kvstore_id: str, registry_version: str=""):
        self.data['apps'].append({
            "bundle-id": self.bundle_id,
            "kvstore-id": kvstore_id,
            "registry-version": registry_version
        })

    def dumps(self) -> bytes:
        return plistlib.dumps(self.data)
