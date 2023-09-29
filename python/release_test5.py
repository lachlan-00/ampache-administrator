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

    ampache5_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)


def ampache5_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    mytime = int(time.time())
    encrypted_key = ampacheConnection.encrypt_password(ampache_api, mytime)

    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, ampache_user, mytime, api_version)
    if not ampache_session:
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    tempusername = 'demo'
    ampacheConnection.user_create(tempusername, 'demodemo', 'email@gmail.com', False, False)
    ampacheConnection.user_create('generic', 'demodemo', 'generic@gmail.com', False, False)

    # add an api key for use later
    #ampacheConnection.user_update(tempusername, False, False, False, False, False, False, False, False, False, 1, False, False)
    #ampacheConnection.user_update('admin', False, False, False, False, False, False, False, False, False, 1, False, False)

    catalogs = ampacheConnection.catalogs('music')
    catalog_id = catalogs['catalog'][0]['id']
    # add items to the catalog
    ampacheConnection.catalog_action('add_to_catalog', catalog_id)
    # update the counts after adding
    ampacheConnection.catalog_action('garbage_collect', catalog_id)
    # enable share and video access
    ampacheConnection.preference_edit('share', 1, 1)
    ampacheConnection.preference_edit('allow_video', 1, 1)
    # ampache-test data
    ampacheConnection.live_stream_create('HBR1.com - Dream Factory', 'http://ubuntu.hbr1.com:19800/ambient.aac', 'mp4', catalog_id, 'http://www.hbr1.com/')
    ampacheConnection.live_stream_create('HBR1.com - I.D.M. Tranceponder', 'http://ubuntu.hbr1.com:19800/trance.ogg', 'ogg', catalog_id, 'http://www.hbr1.com/')
    ampacheConnection.live_stream_create('4ZZZ Community Radio', 'https://stream.4zzz.org.au:9200/4zzz', 'mp3', catalog_id, 'https://4zzzfm.org.au')
    ampacheConnection.podcast_create('http://rss.sciam.com/sciam/60secsciencepodcast', catalog_id)
    ampacheConnection.podcast_create('https://anchor.fm/s/90932e8/podcast/rss', catalog_id)
    ampacheConnection.podcast_create('https://anchor.fm/s/90932e8/podcast/rss', catalog_id)
    ampacheConnection.share_create(5, 'artist')
    ampacheConnection.share_create(2, 'album')
    ampacheConnection.share_create(15, 'song')

    # return the api key to run build_all
    user = ampacheConnection.user('admin')
    if not user['auth']:
        print(ampache_api)
    else:
        print(user['auth'])

api_version = api5_version
build_docs(url, api, user, 'json')
#build_docs(url, api, user, 'xml')

