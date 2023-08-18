#!/usr/bin/env python3

import configparser
import os
import re
import shutil
import sys
import time

import ampache

# user variables
url = 'https://demo.ampache.dev'
api = 'demo'
user = 'demodemo'
limit = 4
offset = 0
api3_version = '391000'
api4_version = '443000'
api5_version = '5.5.7'
api6_version = '6.0.0'
subsonic_api = '1.16.1'
docpath = "docs/"
song_url = 'https://music.com.au/play/index.php?ssid=eeb9f1b6056246a7d563f479f518bb34&type=song&oid=60&uid=4&player=api&name=Synthetic%20-%20BrownSmoke.wma'
APIVERSION = 0
try:
    if sys.argv[1]:
        url = sys.argv[1]
    if sys.argv[2]:
        user = sys.argv[2]
    if sys.argv[3]:
        api = sys.argv[3]
    if sys.argv[4]:
        APIVERSION = sys.argv[4]
except IndexError:
    APIVERSION = 0

def build_docs(ampache_url, ampache_api, ampache_user, api_format):
    ampacheConnection = ampache.API()

    ampacheConnection.set_debug(False)
    ampacheConnection.set_format(api_format)

    ampache6_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)


def ampache6_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    mytime = int(time.time())
    encrypted_key = ampacheConnection.encrypt_password(ampache_api, mytime)

    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, ampache_user, mytime, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    tempusername = 'demo'
    ampacheConnection.user_create(tempusername, 'demodemo', 'email@gmail.com', False, False)

    ampacheConnection.catalog_add('music', '/media/music', 'local', 'music')

    catalogs = ampacheConnection.catalogs('music')
    ampacheConnection.catalog_action('add_to_catalog', catalogs['catalog'][0]['id'])



api_version = api6_version
build_docs(url, api, user, 'json')
#build_docs(url, api, user, 'xml')

