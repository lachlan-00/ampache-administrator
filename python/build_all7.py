#!/usr/bin/env python3

import ampache
import json
import os
import re
import sys
import time
import xmltodict
import urllib.parse

BUILD_DIR = os.path.dirname(os.path.realpath(__file__))

OS = os.name
if OS == 'nt':
    SLASH = '\\'
else:
    SLASH = '/'

# [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/collection.bru
MYUSERNAME = 'user' # filled in by setup_ampache
PASSWORD = "demodemo"
TOKEN = "31cf2a285fe139abef86e7f49728b0e6c8da5b828bf742445451a631ba8ad7d0"
URL = 'http://localhost:8989'
DEMOPASSWORD = 'demodemo'
try:
    length = len(sys.argv)
    if 1 < length and sys.argv[1].startswith("http"):
        URL = sys.argv[1]
    if 2 < length:
        TOKEN = sys.argv[2]
    if 3 < length:
        MYUSERNAME = sys.argv[3]
    if 4 < length:
        if sys.argv[4] == '1':
            ENABLEDEBUG = False
    if 5 < length:
        release_version = sys.argv[5]
except IndexError:
    pass

DEMOUSERTOKEN = 'e131647f22af624963e273c63659da1451d4e7f52442ec5362e660f9628bd2da'

CATALOGACTION = 'add_to_catalog'

EXAMPLEPLAYLISTNAME = urllib.parse.quote_plus('Example Playlist')

PODCASTFEEDURL = urllib.parse.quote_plus('https://feeds.simplecast.com/kZ0W9vjc')

RADIOSTREAMURL = urllib.parse.quote_plus('https://iheart.4zzz.org.au/4zzz')
RADIOHOMEURL = urllib.parse.quote_plus('https://4zzzfm.org.au')
RADIONAME = urllib.parse.quote_plus('HBR1.com - Tronic Lounge')

STREAMURL = urllib.parse.quote_plus('http://ubuntu.hbr1.com:19800/tronic.ogg')
STREAMHOMEURL = urllib.parse.quote_plus('http://www.hbr1.com/')
STREAMNAME = urllib.parse.quote_plus('4ZZZ Community Radio')

TEMPUSERNAME = 'temp_user'
REGISTERUSERNAME = 'register'

RUN6 = True
RUN5 = True
RUN4 = True
RUN3 = True
RUNSUBSONIC = True
RUNOPENSUBSONIC = True

try:
    length = len(sys.argv)
    if length >= 1:
        RUN6 = False
        RUN5 = False
        RUN4 = False
        RUN3 = False
        RUNSUBSONIC = False
        RUNOPENSUBSONIC = False
        for argument in sys.argv:
            if argument == '6':
                RUN6 = True
            if argument == '5':
                RUN5 = True
            if argument == '4':
                RUN4 = True
            if argument == '3':
                RUN3 = True
            if argument == '3':
                RUN3 = True
            if argument == 'o':
                RUNOPENSUBSONIC = True
            if argument == 's':
                RUNSUBSONIC = True
except IndexError:
    pass

class AmpacheRunner:
    def __init__(self):
        self.ampache_connection = ampache.API()

        self.ampache_connection.set_debug(False)

        # Not needed when using a bearer token
        #TOKEN = ampache_connection.encrypt_string('apikey', 'username')

        self.ampache_connection.set_url(URL)
        if not TOKEN:
            mytime = int(time.time())
            self.ampache_connection.set_user("user")
            encrypted_key = self.ampache_connection.encrypt_password(PASSWORD, mytime)
            self.ampache_connection.set_bearer_token(encrypted_key)
        else:
            self.ampache_connection.set_bearer_token(TOKEN)

        self.headers = {'Authorization': f'Bearer {TOKEN}'}
        self.demoheaders = {'Authorization': f'Bearer {DEMOUSERTOKEN}'}
        self.myusername = MYUSERNAME
        self.localplayenabled = True
        self.musiccatalogid = '1'
        self.podcastcatalogid = '2'
        self.videocatalogid = '3'
        self.artistid = '6'
        self.artistid2 = '2'
        self.songartistid = '42'
        self.albumid = '13'
        self.songid = '113'
        self.songid2 = '17'
        self.playlistid = '8'
        self.videoid = '1'
        self.podcastid = '1'
        self.podcastepisodeid = '1'
        self.livestreamid = '1'
        self.albumartistid = '43'
        self.shareid = '4'
        self.followusername = 'admin'
        self.albumname = urllib.parse.quote_plus('CC 20th Anniversary Open Mix')
        self.playlistname = urllib.parse.quote_plus('Example Playlist')
        self.scrobblesong = urllib.parse.quote_plus("You Fiddle, I'll Burn Rome")
        self.scrobblealbum = urllib.parse.quote_plus('I Made This While You Were Asleep')
        self.scrobbleartist = urllib.parse.quote_plus('Chris Zabriskie')
        self.lyricsartist = urllib.parse.quote_plus('Fog Lake')
        self.lyricssong = urllib.parse.quote_plus('roswell')
        self.songfilepath = urllib.parse.quote_plus('/path/to/song.mp3')
        self.songfolderpath = urllib.parse.quote_plus('/path/to/song/folder')

    @staticmethod
    def parse_response(response, api_format):
        # bad failures return false
        if not response:
            return {}

        # return a dict for easy processing
        if api_format == 'json':
            return json.loads(response)
        elif api_format == 'xml':
            try:
                return xmltodict.parse(response, attr_prefix='', cdata_key='text')['root']
            except KeyError:
                return xmltodict.parse(response, attr_prefix='', cdata_key='text')
        else:
            raise ValueError("Unsupported api_format. Use 'json' or 'xml'.")

    def run_all(self):
        # delete of check things to make sure we only get correct values
        self.setup_ampache()

        # ampache api for all versions
        if RUN6:
            self.ampache6()
        if RUN5:
            self.ampache5()
        if RUN4:
            self.ampache4()
        if RUN3:
            self.ampache3()

        # subsonic api for all versions
        if RUNOPENSUBSONIC:
            self.opensubsonic()
        if RUNSUBSONIC:
            self.subsoniclegacy()

        # any post completion settings or dfaults to restore
        self.cleanup()

    def setup_ampache(self):
        self.ampache_connection.set_debug(True)

        api_version = '6.7.3'
        api_format = 'json'

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-preference_edit (ENABLE API_ENABLE_6).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=api_enable_6&value=1&version=5.5.6"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        api_url = f"{URL}/server/json.server.php?action=ping"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', 'ping', self.headers), 'json')
        if response == {}:
            sys.exit(f"No response from {URL}")
        elif not "auth" in response:
            sys.exit(f"Could not connect to {URL}")
        self.myusername = response['username']

        # GET RANDOM ID's to use in the tests

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        for catalog in response['catalog']:
            if catalog['gather_types'] == 'music' and catalog['name'] != 'upload':
                self.musiccatalogid = catalog['id']
                continue
            if catalog['gather_types'] == 'podcast':
                self.podcastcatalogid = catalog['id']
                continue
            if catalog['gather_types'] == 'video':
                self.videocatalogid = catalog['id']
                continue

        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        for user in response['user']:
            if user['username'] == self.myusername:
                self.followusername = user['username']
                break

        try:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlists XMLRENAME.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=playlists&offset=0&limit=4&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/xml-playlists JSONRENAME.bru
            x_deleteplaylist = response['playlist'][0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/xml-playlist_delete XMLRENAME.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={x_deleteplaylist}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        except (IndexError, TypeError):
            pass

        try:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlists JSONRENAME.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter=renamejson&offset=0&limit=4&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlists JSONRENAME.bru
            j_deleteplaylist = response['playlist'][0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlist_delete JSONRENAME.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={j_deleteplaylist}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        except (IndexError, TypeError):
            pass

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-user_delete CHECK.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/xml-user_delete CHECK.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.livestreamid = response['live_stream'][0]['id']

        api_url = f"{URL}/server/{api_format}.server.php?action=artists&version={api_version}&cond=song_artist,1;album_artist,1&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.artistid = response['artist'][0]['id']
        self.artistid2 = response['artist'][1]['id']

        api_url = f"{URL}/server/{api_format}.server.php?action=artists&version={api_version}&cond=song_artist,1&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.songartistid = response['artist'][0]['id']

        api_url = f"{URL}/server/{api_format}.server.php?action=artists&version={api_version}&cond=album_artist,1&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.albumartistid = response['artist'][0]['id']

        api_url = f"{URL}/server/{api_format}.server.php?action=songs&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.songid = response['song'][0]['id']
        self.songid2 = response['song'][1]['id']
        self.songfilepath = urllib.parse.quote_plus(response['song'][0]['filename'])
        self.songfolderpath = urllib.parse.quote_plus(os.path.dirname(response['song'][0]['filename']))
        self.scrobblesong = urllib.parse.quote_plus(response['song'][2]['title'])
        self.scrobblealbum = urllib.parse.quote_plus(response['song'][2]['album']['name'])
        self.scrobbleartist = urllib.parse.quote_plus(response['song'][2]['artist']['name'])

        api_url = f"{URL}/server/{api_format}.server.php?action=albums&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.albumid = response['album'][0]['id']
        self.albumname = urllib.parse.quote_plus(response['album'][1]['name'])

        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        try:
            self.playlistid = response['playlist'][0]['id']
            self.playlistname = urllib.parse.quote_plus(response['playlist'][0]['name'])
        except (KeyError, IndexError, TypeError):
            api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=Example%20Playlist&type=private&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            self.playlistid = response['id']
            pass

        api_url = f"{URL}/server/{api_format}.server.php?action=shares&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        self.shareid = response['share'][0]['id']

        api_url = f"{URL}/server/{api_format}.server.php?action=videos&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        try:
            self.videoid = response['video'][0]['id']
        except (KeyError, IndexError, TypeError):
            pass

        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        try:
            self.podcastid = response['podcast'][0]['id']
        except (KeyError, IndexError, TypeError):
            pass

        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter={self.podcastid}&include=1&version={api_version}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        try:
            self.podcastepisodeid = response['podcast_episode'][0]['id']
        except (KeyError, IndexError, TypeError):
            pass

        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=and&type=song&offset=0&limit=4&random=1&rule_1=lyrics&rule_1_operator=5&rule_1_input=&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if response != {} and 'song' in response and len(response['song']) > 0:
            self.lyricsartist = urllib.parse.quote_plus(response['song'][0]['artist']['name'])
            self.lyricssong = urllib.parse.quote_plus(response['song'][0]['title'])

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-localplay CHECK.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-localplay CHECK.bru
        if 'error' in response:
            if response['error']['errorMessage'] == 'Unable to connect to localplay controller':
                print("Disable Localplay Checks")
                self.localplayenabled = False

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=garbage_collect&catalog={self.musiccatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=garbage_collect&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=garbage_collect&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

    def ampache3(self):
        self.ampache_connection.set_debug(True)

        api_version = '390001'
        api_format = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache3", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-handshake.bru
        auth = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamexml&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_create.bru
        createdplaylist = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET CREATED).bru
            createduser = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET REGISTERED).bru
            createduser = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albumsinclude=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genres.bru
        genreid = response["tag"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

    def ampache4(self):
        self.ampache_connection.set_debug(True)

        api_version = '443000'
        api_format = 'json'

        docpath = os.path.join(BUILD_DIR, "python3-ampache4", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-handshake.bru
        handshake_auth = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={handshake_auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter=4&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamejson&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_create.bru
        createdplaylist = response[0]['id']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response[0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response[0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET CREATED).bru
            createduser = response["user"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET REGISTERED).bru
            createduser = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genres.bru
        genreid = response[0]["tag"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-live_streams.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast_episodes.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response[0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691768&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

        api_format = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache4", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-handshake.bru
        handshake_auth = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={handshake_auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?createdbookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamexml&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_create.bru
        createdplaylist = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response["podcast"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET CREATED).bru
            createduser = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET REGISTERED).bru
            createduser = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache64/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genres.bru
        genreid = response["tag"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

    def ampache5(self):
        self.ampache_connection.set_debug(True)

        api_version = '5.5.6'
        api_format = 'json'

        docpath = os.path.join(BUILD_DIR, "python3-ampache5", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-handshake.bru
        handshake_auth = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={handshake_auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response["bookmark"][0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter=4&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamejson&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_create.bru
        createdplaylist = response['id']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET CREATED).bru
            createduser = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET REGISTERED).bru
            createduser = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genres.bru
        genreid = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691768&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

        api_format = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache5", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-handshake.bru
        handshake_auth = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={handshake_auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response["bookmark"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamexml&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_create.bru
        createdplaylist = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response["podcast"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET CREATED).bru
            createduser = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET REGISTERED).bru
            createduser = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genres.bru
        genreid = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

    def ampache6(self):
        self.ampache_connection.set_debug(True)

        api_version = '6.7.3'
        api_format = 'json'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4742", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4701", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4704", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4710", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4705", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4706", self.headers), api_format)

        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (DISABLE API_ENABLE_6).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=api_enable_6&value=0&version=5.5.6"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4700", self.headers), api_format)

        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (ENABLE API_ENABLE_6).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=api_enable_6&value=1&version=5.5.6"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (DISABLE VIDEO).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=allow_video&value=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4703", self.headers), api_format)

        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (ENABLE VIDEO).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=allow_video&value=1"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        handshake_auth = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={handshake_auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/preference/json-preference_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=preference_create&filter=temp_pref_{api_format}&type=boolean&default=0&category=interface&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented preference_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/preference/json-preference_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=preference_edit&filter=temp_pref_{api_format}&value=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/preference/json-preference_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=preference_delete&filter=temp_pref_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter=4&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamejson&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_create.bru
        createdplaylist = response['id']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET CREATED).bru
            createduser = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET REGISTERED).bru
            createduser = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genres.bru
        genreid = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691768&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

        api_format = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", (api_format + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # do all the bad stuff first

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (access error)", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4742", self.demoheaders), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&user=notauser&auth=badkey&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4701", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4704", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4710", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4705", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4706", self.headers), api_format)

        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (DISABLE API_ENABLE_6).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=api_enable_6&value=0&version=5.5.6"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4700", self.headers), api_format)

        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (ENABLE API_ENABLE_6).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=api_enable_6&value=1&version=5.5.6"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (DISABLE VIDEO).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=allow_video&value=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"error-4703", self.headers), api_format)

        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-preference_edit (ENABLE VIDEO).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=allow_video&value=1"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=handshake&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-handshake.bru
        handshake_auth = response["auth"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-goodbye.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=goodbye&auth={handshake_auth}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=ping&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/preference/json-preference_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=preference_create&filter=temp_pref_{api_format}&type=boolean&default=0&category=interface&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented preference_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/preference/json-preference_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=preference_edit&filter=temp_pref_{api_format}&value=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/preference/json-preference_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=preference_delete&filter=temp_pref_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + api_version)
        else:
            createdbookmark = response["bookmark"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_edit&filter={createdbookmark}&type=bookmark&position=10&client=python3-ampache&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=get_bookmark&filter={self.songid}&type=song&all=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (show all)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark&filter={createdbookmark}&include=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=bookmark_delete&filter={createdbookmark}&type=bookmark&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + api_version)
        else:
            createdlivestream = response["live_stream"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_edit&filter={createdlivestream}&api_url=http%3A%2F%2Fampache.org&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream_delete&filter={createdlivestream}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_create&name=renamexml&type=private&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_create.bru
        createdplaylist = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_hash&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add&filter={createdplaylist}&id={self.playlistid}&type=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_add_song&song={self.songid}&filter={createdplaylist}&check=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_edit&filter={createdplaylist}&name={EXAMPLEPLAYLISTNAME}_{api_format}&type=public&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_remove_song&filter={createdplaylist}&track=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_songs&filter={createdplaylist}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_delete&filter={createdplaylist}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + api_version)
        else:
            createdpodcast = response["podcast"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_edit&filter={createdpodcast}&copyright=False&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter=notapodcast&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_delete&filter={createdpodcast}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + api_version)
        else:
            createdshare = response["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_edit&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=share_delete&filter={createdshare}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_create.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_create&username={TEMPUSERNAME}_{api_format}&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_{api_format}@gmail.com&disable=0&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET CREATED).bru
            createduser = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_update&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_edit&username={TEMPUSERNAME}_{api_format}&disable=1&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET DISABLED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preference&username={TEMPUSERNAME}_{api_format}&filter=ajax_load&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_preferences&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={TEMPUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username=user&fullname=fullname&password=password98hf29hf2390h&email=user@ampache.dev&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=register&username={REGISTERUSERNAME}_{api_format}&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_{api_format}@email.com&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + api_version)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET REGISTERED).bru
            createduser = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=user_delete&username={REGISTERUSERNAME}_{api_format}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=album&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=artist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=label&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (label)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=podcast_episode&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_rules.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_rules&filter=video&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=A&rule_2=artist&rule_2_operator=2&rule_2_input=C&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-album.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album&filter={self.albumid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=albums&filter={self.albumname}&include=1&exact=1&offset=0&limit=10&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist&filter={self.artistid}&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=albums&include=songs&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=artists&include=1&limit=4&&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=bookmarks&include=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (root)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.podcastcatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=browse&filter={self.videocatalogid}&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog&filter=1&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_file&file={self.songfilepath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalog_folder&folder={self.songfolderpath}&task=clean&catalog={self.videocatalogid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=catalogs&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=deleted_videos&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-flag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-followers.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=followers&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-following.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=following&username=generic&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=friends_timeline&limit=4&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tags&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genres.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genres&filter=D&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genres.bru
        genreid = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre&filter={genreid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=genre_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_albums&filter={genreid}&offset=0&limit=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_artists&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=tag_songs&filter={genreid}&offset=0&limit=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist with include)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (catalog)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (live_stream)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast_episode)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (share)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song_artist)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (video)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-label.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=label_artists&filter=2&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-labels.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=labels&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=last_shouts&username=user&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-license.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=license_songs&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-licenses.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=licenses&update=4&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=list&type=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=live_streams&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + api_version)
        else:
            livestreamid = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=live_stream&filter={livestreamid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=stop&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-localplay.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=localplay&command=status&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=playlist&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (playlist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=play&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (play)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (vote)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-democratic.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=democratic&method=vote&oid={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast&filter=1&include=episodes&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + api_version)
        elif not 'podcast_episode' in response:
            pass
        else:
            podcastepisodeid = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{api_format}.server.php?action=podcast_episode&filter={podcastepisodeid}&version={api_version}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=podcasts&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-rate.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-record_play.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_group.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-share.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=share&filter=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-shares.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=shares&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_similar.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=get_similar&filter={self.songid}&type=song&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=song_tags&filter={self.songid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-songs.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=songs&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-stats.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preferences&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preference.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_preference&filter=ajax_load&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_update.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=system_update&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-timeline.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=timeline&username=user&limit=10&since=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=toggle_follow&username={self.followusername}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_art.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_artist_info&id={self.artistid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=update_podcast&filter={self.podcastid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=missing_user&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user&username=otheruser&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (disabled)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_playlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=user_smartlists&offset=0&limit=4&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-users.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=users&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-video.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=video&filter={self.videoid}&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-videos.bru
        api_url = f"{URL}/server/{api_format}.server.php?action=videos&offset=0&limit=0&version={api_version}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

    def opensubsonic(self):
        self.ampache_connection.set_debug(False)

        api_format = 'json'

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/0_setup/json-preference_edit (SET OPENSUBSONIC).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=subsonic_legacy&value=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        SONGPREFIX = "so-"
        SONGPREFIX2 = "so-"
        ALBUMPREFIX = "al-"
        ARTISTPREFIX = "ar-"
        PLAYLISTPREFIX = "pl-"
        VIDEOPREFIX = "vi-"

        # python3-ampache6/docs/opensubsonic
        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "opensubsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
                if radio["name"] == "4ZZZ Community Radio":
                    createdradio = radio["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-updateInternetRadioStation.bru
                    api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}&id={createdradio}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-deleteInternetRadioStation.bru
                    api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&name=testcreate&songId={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-createPlaylist.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdplaylist = response["subsonic-response"]["playlist"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-updatePlaylist.bru
            api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&playlistId={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-deletePlaylist.bru
            api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for channel in response["subsonic-response"]["podcasts"]["channel"]:
                if channel["title"] == "Dolly Parton's America":
                    createdpodcast = channel["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                    api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}&includeEpisodes=1"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                    createdpodcastepisode = response["subsonic-response"]["podcasts"]["channel"][0]["episode"][0]["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-downloadPodcastEpisode.bru
                    api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastepisode}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-deletePodcastEpisode.bru
                    api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastepisode}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-deletePodcastChannel.bru
                    api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-createShare.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdshare = response["subsonic-response"]["shares"]["share"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-updateShare.bru
            api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-deleteShare.bru
            api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={api_format}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={api_format}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={api_format}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={api_format}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getInternetRadioStations.bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={api_format}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={PLAYLISTPREFIX}{self.playlistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={api_format}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={api_format}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={VIDEOPREFIX}{self.videoid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX2}{self.songid2}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (get)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=status"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={api_format}&apiKey={TOKEN}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}&current={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-search.bru
        api_url = f"{URL}/rest/search.view?v=1.16.1&c=Ampache&f={api_format}&any=the&count=20"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

        api_format = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "opensubsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
                if radio["name"] == "4ZZZ Community Radio":
                    createdradio = radio["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-updateInternetRadioStation.bru
                    api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-deleteInternetRadioStation.bru
                    api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&name=testcreate&songId={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-createPlaylist.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdplaylist = response["subsonic-response"]["playlist"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-updatePlaylist.bru
            api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&playlistId={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-deletePlaylist.bru
            api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for channel in response["subsonic-response"]["podcasts"]["channel"]:
                if channel["title"] == "Dolly Parton's America":
                    createdpodcast = channel["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                    api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}&includeEpisodes=1"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                    createdpodcastepisode = response["subsonic-response"]["podcasts"]["channel"]["episode"][0]["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-downloadPodcastEpisode.bru
                    api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastepisode}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-deletePodcastEpisode.bru
                    api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastepisode}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-deletePodcastChannel.bru
                    api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX2}{self.songid2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-createShare.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdshare = response["subsonic-response"]["shares"]["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-updateShare.bru
            api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-deleteShare.bru
            api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={api_format}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={api_format}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={api_format}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={api_format}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/obensubsonic/xml/xml-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={api_format}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={PLAYLISTPREFIX}{self.playlistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={api_format}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={api_format}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={api_format}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={VIDEOPREFIX}{self.videoid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (get)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=status"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}&current={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-search.bru
        api_url = f"{URL}/rest/search.view?v=1.16.1&c=Ampache&f={api_format}&any=the&count=20"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={api_format}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

    def subsoniclegacy(self):
        self.ampache_connection.set_debug(False)

        api_format = 'json'

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/0_setup/json-preference_edit (SET SUBSONIC_LEGACY).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=subsonic_legacy&value=1"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        OLD_SUBID_ALBUM = 200000000
        OLD_SUBID_ARTIST = 100000000
        OLD_SUBID_PLAYLIST = 800000000
        OLD_SUBID_PODCAST = 600000000
        OLD_SUBID_PODCASTEP = 700000000
        OLD_SUBID_SMARTPL = 400000000
        OLD_SUBID_SONG = 300000000
        OLD_SUBID_VIDEO = 500000000

        OLD_SONG_ID2 = str(OLD_SUBID_SONG + int(self.songid2))
        OLD_SONG_ID = str(OLD_SUBID_SONG + int(self.songid))
        OLD_ALBUM_ID = str(OLD_SUBID_ALBUM + int(self.albumid))
        OLD_ARTIST_ID = str(OLD_SUBID_ARTIST + int(self.artistid))
        OLD_PLAYLIST_ID = str(OLD_SUBID_PLAYLIST + int(self.playlistid))
        OLD_VIDEO_ID = str(OLD_SUBID_VIDEO + int(self.videoid))

        # python3-ampache6/docs/ampache-subsonic
        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "ampache-subsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
                if radio["name"] == "4ZZZ Community Radio":
                    createdradio = radio["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-updateInternetRadioStation.bru
                    api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-deleteInternetRadioStation.bru
                    api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&name=testcreate&songId={OLD_SONG_ID2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-createPlaylist.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdplaylist = response["subsonic-response"]["playlist"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-updatePlaylist.bru
            api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&playlistId={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-deletePlaylist.bru
            api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for channel in response["subsonic-response"]["podcasts"]["channel"]:
                if channel["title"] == "Dolly Parton's America":
                    createdpodcast = channel["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                    api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}&includeEpisodes=1"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                    createdpodcastEPISODE = response["subsonic-response"]["podcasts"]["channel"][0]["episode"][0]["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-downloadPodcastEpisode.bru
                    api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastEPISODE}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-deletePodcastEpisode.bru
                    api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastEPISODE}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-deletePodcastChannel.bru
                    api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-createShare.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdshare = response["subsonic-response"]["shares"]["share"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-updateShare.bru
            api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-deleteShare.bru
            api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={api_format}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={api_format}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ALBUM_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ALBUM_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ALBUM_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ARTIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ARTIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ARTIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getInternetRadioStations.bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={api_format}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_PLAYLIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={api_format}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={api_format}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_VIDEO_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID2}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (get)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=status"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={api_format}&apiKey={TOKEN}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}&current={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-search.bru
        api_url = f"{URL}/rest/search.view?v=1.16.1&c=Ampache&f={api_format}&any=the&count=20"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

        api_format = 'xml'

        # python3-ampache6/docs/ampache-subsonic
        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "ampache-subsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{api_format}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
                if radio["name"] == "4ZZZ Community Radio":
                    createdradio = radio["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-updateInternetRadioStation.bru
                    api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-deleteInternetRadioStation.bru
                    api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={api_format}&id={createdradio}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&name=testcreate&songId={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-createPlaylist.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdplaylist = response["subsonic-response"]["playlist"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-updatePlaylist.bru
            api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&playlistId={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-deletePlaylist.bru
            api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={createdplaylist}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        if not 'subsonic-response' in response:
            pass
        else:
            for channel in response["subsonic-response"]["podcasts"]["channel"]:
                if channel["title"] == "Dolly Parton's America":
                    createdpodcast = channel["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                    api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}&includeEpisodes=1"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                    createdpodcastEPISODE = response["subsonic-response"]["podcasts"]["channel"]["episode"][0]["id"]

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-downloadPodcastEpisode.bru
                    api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastEPISODE}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-deletePodcastEpisode.bru
                    api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcastEPISODE}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

                    # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-deletePodcastChannel.bru
                    api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={api_format}&id={createdpodcast}"
                    response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-createShare.bru
        if not 'subsonic-response' in response:
            pass
        else:
            createdshare = response["subsonic-response"]["shares"]["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-updateShare.bru
            api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-deleteShare.bru
            api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={api_format}&id={createdshare}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={api_format}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={api_format}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={api_format}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ALBUM_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ALBUM_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ALBUM_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={api_format}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ARTIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ARTIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_ARTIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={api_format}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_PLAYLIST_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={api_format}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={api_format}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={api_format}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_VIDEO_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (get)", self.headers), api_format)
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={api_format}&action=status"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)} (status)", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}&current={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-search.bru
        api_url = f"{URL}/rest/search.view?v=1.16.1&c=Ampache&f={api_format}&any=the&count=20"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={api_format}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={api_format}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={api_format}&id={OLD_SONG_ID}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, api_format, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), api_format)

        self.self_check(docpath, URL)

    def cleanup(self):
        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/z_cleanup/json-preference_edit (SET OPENSUBSONIC).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=subsonic_legacy&value=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', '', self.headers), 'json')

    @staticmethod
    def self_check(docpath, url):
        if not os.path.isdir(docpath):
            sys.exit("Docpath not found: " + docpath)
        print("Checking files in " + docpath + " for private strings")
        for files in sorted(os.listdir(docpath)):
            if not os.path.isdir(files):
                try:
                    f = open(os.path.join(docpath, files), 'r', encoding="utf-8")
                    filedata = f.read()
                    f.close()

                    if ('<error code="405"><![CDATA[Invalid Request]]></error>' in filedata or
                            '<errorMessage><![CDATA[Invalid Request]]></errorMessage>' in filedata or
                            '"message": "Invalid Request"' in filedata or
                            '"errorMessage": "Invalid Request"' in filedata):
                        print(f"ERROR invalid request: {docpath} {files}")
                        os.remove(os.path.join(docpath, files))
                        continue
                    if ('<error code="401"><![CDATA[Incorrect object type' in filedata or
                            '<errorMessage><![CDATA[Incorrect object type' in filedata or
                            '"message": "Incorrect object type' in filedata or
                            '"errorMessage": "Incorrect object type' in filedata):
                        print(f"ERROR invalid object type: {files}")
                        os.remove(os.path.join(docpath, files))
                        continue

                    url_text = url.replace("https://", "")
                    url_text = url_text.replace("http://", "")
                    url_pattern = re.escape(url_text)
                    filedata = filedata.replace(url_text, "music.com.au")
                    newdata = re.sub(url_pattern, "music.com.au", filedata)
                    newdata = newdata.replace("http://music.com.au", "https://music.com.au")
                    newdata = newdata.replace("http:\\/\\/music.com.au", "https:\\/\\/music.com.au")
                    newdata = re.sub(r"CDATA\[/media/", "CDATA[/mnt/files-music/ampache-test/", newdata)
                    newdata = re.sub(r"\\/media\\/", "\\/mnt\\/files-music\\/ampache-test\\/", newdata)
                    newdata = re.sub(r"/mnt\\/music\\/ampache\\/music", "\\/mnt\\/files-music\\/ampache-test", newdata)
                    newdata = re.sub(r"/mnt/music/ampache/music", "/mnt/files-music/ampache-test", newdata)
                    newdata = re.sub("\"session_expire\": \"*.*\"*", "\"session_expire\": \"2022-08-17T06:21:00+00:00\",", newdata)
                    newdata = re.sub("<session_expire>.*</session_expire>",
                                    "<session_expire><![CDATA[2022-08-17T04:34:55+00:00]]></session_expire>", newdata)
                    newdata = re.sub("\"addition_time\": [0-9]*", "\"addition_time\": 1675665915", newdata)
                    newdata = re.sub("<addition_time>.*</addition_time>", "<addition_time>1675665915</addition_time>", newdata)
                    newdata = re.sub("\"delete_time\": [0-9]*", "\"delete_time\": 1670202698", newdata)
                    newdata = re.sub("<delete_time>.*</delete_time>", "<delete_time>1670202698</delete_time>", newdata)
                    newdata = re.sub("\"create_date\": [0-9]*", "\"create_date\": 1670202701", newdata)
                    newdata = re.sub("<create_date>.*</create_date>", "<create_date>1670202701</create_date>", newdata)
                    newdata = re.sub("\"creation_date\": [0-9]*", "\"creation_date\": 1670202706", newdata)
                    newdata = re.sub("<creation_date>[0-9]*</creation_date>", "<creation_date>1670202706</creation_date>", newdata)
                    newdata = re.sub("&secret=.{8}", "&secret=GJ7EzBPT", newdata)
                    newdata = re.sub("\"secret\": \"*.*\"*", "\"secret\": \"GJ7EzBPT\",", newdata)
                    newdata = re.sub("<secret>.*</secret>", "<secret><![CDATA[GJ7EzBPT]]></secret>", newdata)
                    newdata = re.sub("\"sync_date\": \"*.*\"*", "\"sync_date\": \"2022-08-17T05:07:11+00:00\",", newdata)
                    newdata = re.sub("<sync_date>.*</sync_date>", "<sync_date><![CDATA[2022-08-17T05:07:11+00:00]]></sync_date>",
                                    newdata)
                    #newdata = re.sub(ampache_api, "eeb9f1b6056246a7d563f479f518bb34", newdata)
                    #newdata = re.sub(ampache_session, "cfj3f237d563f479f5223k23189dbb34", newdata)
                    newdata = re.sub('auth=[a-z0-9]*', "auth=eeb9f1b6056246a7d563f479f518bb34", newdata)
                    newdata = re.sub('ssid=[a-z0-9]*', "ssid=cfj3f237d563f479f5223k23189dbb34", newdata)

                    f = open(os.path.join(docpath, files), 'w', encoding="utf-8")
                    f.write(newdata)
                    f.close()
                except IsADirectoryError:
                    pass

if __name__ == '__main__':
    runner = AmpacheRunner()
    runner.run_all()

