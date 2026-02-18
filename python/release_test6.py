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
api6_version = '6.6.5'
subsonic_api = '1.16.1'
docpath = "docs/"
song_url = 'https://music.com.au/play/index.php?ssid=eeb9f1b6056246a7d563f479f518bb34&type=song&oid=60&uid=4&player=api&name=Synthetic%20-%20BrownSmoke.wma'
APIVERSION = 0
try:
    length = len(sys.argv)
    if 1 < length:
        url = sys.argv[1]
    if 2 < length:
        api = sys.argv[2]
    if 3 < length:
        user = sys.argv[3]
    if 4 < length:
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
        print(ampache_api, ' ', ampache_user, ' ', encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print(ampache_api, ' ', ampache_user, ' ', encrypted_key)
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    tempusername = 'demo'
    ampacheConnection.user_create(tempusername, 'demodemo', 'email@gmail.com', False, False)
    ampacheConnection.user_create('generic', 'demodemo', 'generic@gmail.com', False, False)

    # add an api key for use later
    ampacheConnection.user_edit(tempusername, False, False, False, False, False, False, False, False, False, 1, False, False)
    ampacheConnection.user_edit('admin', False, False, False, False, False, False, False, False, False, 1, False, False)

    ampacheConnection.catalog_add('music', '/media/music', 'local', 'music')
    ampacheConnection.catalog_add('video', '/media/video', 'local', 'clip')
    ampacheConnection.catalog_add('podcast', '/media/podcast', 'local', 'podcast')

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
    ampacheConnection.bookmark_create(5, 'song')
    ampacheConnection.bookmark_create(2, 'podcast_episode')
    ampacheConnection.bookmark_create(2, 'podcast_episode')
    ampacheConnection.bookmark_create(15, 'song')

    ampacheConnection.bookmark_create(54, 'song', 0, 'client1')
    ampacheConnection.bookmark_create(64, 'song', 10, 'client')
    ampacheConnection.bookmark_create(54, 'song', 0, 'client1')
    ampacheConnection.bookmark_create(64, 'song', 10, 'client')
    ampacheConnection.bookmark_create(54, 'song', 0, 'client1')
    ampacheConnection.bookmark_create(64, 'song', 10, 'client')

    # return the api key to run build_all
    user = ampacheConnection.user('admin')
    if not user['auth']:
        print()
        sys.exit('ERROR: NO AUTH KEY')

    print(user['auth'])

api_version = api6_version
build_docs(url, api, user, 'json')
#build_docs(url, api, user, 'xml')

