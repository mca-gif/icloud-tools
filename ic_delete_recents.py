#!/usr/bin/env python3
"""Deletes various most recently used lists from iCloud history.

Currently supports Messages, Mail, and Maps"""

from ic_kv import ICKV
import sys
import argparse

parser = argparse.ArgumentParser(prog='ic_recents_deleter.py')
parser.add_argument("apple_id", type=str, default=None, help="Apple ID")
parser.add_argument("password", type=str, default=None, help="Password")
args = parser.parse_args()

try:
    ickv = ICKV(args.apple_id, args.password)
except RuntimeError as err:
    print(str(err))
    sys.exit(1)

kvstores = ["com.apple.messages.recents", "com.apple.mail.recents", "com.apple.MapsSupport.history"]
map(ickv.empty, kvstores)
