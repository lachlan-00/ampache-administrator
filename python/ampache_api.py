#!/usr/bin/env python3

import ampache
import json
import os
import re
import sys
import xmltodict
import urllib.parse

BUILD_DIR = os.path.dirname(os.path.realpath(__file__))

OS = os.name
if OS == 'nt':
    SLASH = '\\'
else:
    SLASH = '/'

# [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/collection.bru
MYUSERNAME = '' # filled in by setup_ampache
TOKEN = 'YOURTOKEN'
URL = 'https://develop.ampache.dev'
DEMOPASSWORD = 'demodemo'

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
    if length > 1:
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

        # Not needed when using a bearer token
        #TOKEN = ampache_connection.encrypt_string('apikey', 'username')

        self.ampache_connection.set_url(URL)
        self.ampache_connection.set_bearer_token(TOKEN)
        self.headers = {}
        self.headers['Authorization'] = f'Bearer {TOKEN}'

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
        self.podcastid = '5'
        self.followusername = 'admin'
        self.albumname = urllib.parse.quote_plus('CC 20th Anniversary Open Mix')
        self.playlistname = urllib.parse.quote_plus('Example Playlist')
        self.scrobblesong = urllib.parse.quote_plus("You Fiddle, I'll Burn Rome")
        self.scrobblealbum = urllib.parse.quote_plus('I Made This While You Were Asleep')
        self.scrobbleartist = urllib.parse.quote_plus('Chris Zabriskie')
        self.lyricsartist = urllib.parse.quote_plus('Fog Lake')
        self.lyricssong = urllib.parse.quote_plus('roswell')

    def parse_response(self, response, format):
        # bad failures return false
        if not response:
            return {}

        # return a dict for easy processing
        if format == 'json':
            return json.loads(response)
        elif format == 'xml':
            try:
                return xmltodict.parse(response, attr_prefix='', cdata_key='text')['root']
            except KeyError:
                return xmltodict.parse(response, attr_prefix='', cdata_key='text')
        else:
            raise ValueError("Unsupported format. Use 'json' or 'xml'.")

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
        self.ampache_connection.set_debug(False)

        VERSION = '6.7.3'
        FORMAT = 'json'

        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', 'ping', self.headers), 'json')
        if response == {}:
            sys.exit(f"No response from {URL}")
        elif not "auth" in response:
            sys.exit(f"Could not connect to {URL}")
        MYUSERNAME = response['username']

        # GET RANDOM ID's to use in the tests

        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        for catalog in response['catalog']:
            if catalog['gather_types'] == 'music':
                self.musiccatalogid = catalog['id']
                continue
            if catalog['gather_types'] == 'podcast':
                self.podcastcatalogid = catalog['id']
                continue
            if catalog['gather_types'] == 'video':
                self.videocatalogid = catalog['id']
                continue

        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        for user in response['user']:
            if user['username'] == MYUSERNAME:
                self.followusername = user['username']
                break

        try:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlists XMLRENAME.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&offset=0&limit=4&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/xml-playlists JSONRENAME.bru
            xDELETEPLAYLIST = response['playlist'][0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/xml-playlist_delete XMLRENAME.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={xDELETEPLAYLIST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        except (IndexError, TypeError):
            pass

        try:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlists JSONRENAME.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter=renamejson&offset=0&limit=4&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlists JSONRENAME.bru
            jDELETEPLAYLIST = response['playlist']['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-playlist_delete JSONRENAME.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={jDELETEPLAYLIST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        except (IndexError, TypeError):
            pass

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-user_delete CHECK.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_json&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/xml-user_delete CHECK.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_xml&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.artistid = response['artist'][0]['id']
        self.artistid2 = response['artist'][1]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&version={VERSION}&cond=song_artist,1&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.songartistid = response['artist'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&version={VERSION}&cond=album_artist,1&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.albumartistid = response['artist'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.livestreamid = response['live_stream'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.songid = response['song'][0]['id']
        self.songid2 = response['song'][1]['id']
        self.songfilepath = response['song'][0]['filename']
        self.songdirpath = os.path.dirname(self.songfilename)
        self.scrobblesong = urllib.parse.quote_plus(response['song'][2]['title'])
        self.scrobblealbum = urllib.parse.quote_plus(response['song'][2]['album']['name'])
        self.scrobbleartist = urllib.parse.quote_plus(response['song'][2]['artist']['name'])

        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.albumid = response['album'][0]['id']
        self.albumname = urllib.parse.quote_plus(response['album'][1]['name'])

        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.playlistid = response['playlist'][0]['id']
        self.playlistname = urllib.parse.quote_plus(response['playlist'][1]['name'])

        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.videoid = response['video'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.podcastid = response['podcast'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter={self.podcastid}&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.podcastepisodeid = response['podcast_episode'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&version={VERSION}&sort=rand"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        self.shareid = response['share'][0]['id']

        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=and&type=song&offset=0&limit=4&random=1&rule_1=lyrics&rule_1_operator=5&rule_1_input=&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if response != {} and 'song' in response and len(response['song']) > 0:
            self.lyricsartist = urllib.parse.quote_plus(response['song'][0]['artist']['name'])
            self.lyricssong = urllib.parse.quote_plus(response['song'][0]['title'])

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-localplay CHECK.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=status&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-localplay CHECK.bru
        if 'error' in response:
            if response['error']['errorMessage'] == 'Unable to connect to localplay controller':
                print("Disable Localplay Checks")
                self.localplayenabled = False

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/0_setup/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=garbage_collect&catalog={self.musiccatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=garbage_collect&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=garbage_collect&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

    def ampache3(self):
        self.ampache_connection.set_debug(True)

        VERSION = '390001'
        FORMAT = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache3", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamexml&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_create.bru
        CREATEDPLAYLIST = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_xml&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_xml&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_xml@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET CREATED).bru
            CREATEDUSER = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_xml&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_xml@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user (GET REGISTERED).bru
            CREATEDUSER = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        #* filter  = (string) object_id //optional
        #* type    = (string) 'root', 'catalog', 'artist', 'album', 'podcast' // optional
        #* catalog = (integer) catalog ID you are browsing // optional
        #* add     = $browse->set_api_filter(date) //optional
        #* update  = $browse->set_api_filter(date) //optional
        #* offset  = (integer) //optional
        #* limit   = (integer) //optional
        #* cond    = (string) Apply additional filters to the browse using ';' separated comma string pairs (e.g. 'filter1,value1;filter2,value2') //optional
        #* sort    = (string) sort name or comma separated key pair. Order default 'ASC' (e.g. 'name,ASC' and 'name' are the same) //optional
        #*
        #ampache_connection.browse() docpath + "browse (root)." + api_format)
        #ampache_connection.browse(2, 'podcast', 3) docpath + "browse (podcast)." + api_format)
        #ampache_connection.browse(19, 'artist', 1) docpath + "browse (artist)." + api_format)
        #ampache_connection.browse(12, 'album', 1) docpath + "browse (album)." + api_format)
        #ampache_connection.browse(1, 'catalog') docpath + "browse (music catalog)." + api_format)
        #ampache_connection.browse(2, 'catalog') docpath + "browse (video catalog)." + api_format)
        #ampache_connection.browse(3, 'catalog') docpath + "browse (podcast catalog)." + api_format)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genres.bru
        GENREID = response["tag"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-democratic.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache3/xml/xml-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

    def ampache4(self):
        self.ampache_connection.set_debug(True)

        VERSION = '443000'
        FORMAT = 'json'

        docpath = os.path.join(BUILD_DIR, "python3-ampache4", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-handshake.bru
        AUTH = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter=4&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/bookmark/json-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/live_stream/json-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamejson&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_create.bru
        CREATEDPLAYLIST = response[0]['id']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_json&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/playlist/json-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response[0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response[0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_json&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_json@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET CREATED).bru
            CREATEDUSER = response["user"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_json&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_json&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_json@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user (GET REGISTERED).bru
            CREATEDUSER = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/create/user/json-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)


        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genres.bru
        GENREID = response[0]["tag"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-live_streams.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-democratic\.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast_episodes.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response[0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691768&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/json/json-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

        FORMAT = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache4", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-handshake.bru
        AUTH = response["auth"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamexml&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_create.bru
        CREATEDPLAYLIST = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_xml&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response["podcast"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_xml&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_xml@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET CREATED).bru
            CREATEDUSER = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_xml&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_xml@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user (GET REGISTERED).bru
            CREATEDUSER = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)


        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genres.bru
        GENREID = response["tag"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-democratic.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["code"] == "405":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

    def ampache5(self):
        self.ampache_connection.set_debug(True)

        VERSION = '5.5.6'
        FORMAT = 'json'

        docpath = os.path.join(BUILD_DIR, "python3-ampache5", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-handshake.bru
        AUTH = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response["bookmark"][0]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/json-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter=4&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/json-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/bookmark/json-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/live_stream/json-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamejson&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_create.bru
        CREATEDPLAYLIST = response['id']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_json&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/playlist/json-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_xml&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_xml@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET CREATED).bru
            CREATEDUSER = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_xml&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_xml@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user (GET REGISTERED).bru
            CREATEDUSER = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/create/user/json-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)


        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genres.bru
        GENREID = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-democratic\.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691768&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/json/json-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

        FORMAT = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache5", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-handshake.bru
        AUTH = response["auth"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response["bookmark"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamexml&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_create.bru
        CREATEDPLAYLIST = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_xml&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response["podcast"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_xml&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_xml@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET CREATED).bru
            CREATEDUSER = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_xml&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_xml@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user (GET REGISTERED).bru
            CREATEDUSER = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)


        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genres.bru
        GENREID = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-democratic.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache5/xml/xml-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

    def ampache6(self):
        self.ampache_connection.set_debug(True)

        VERSION = '6.7.3'
        FORMAT = 'json'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-handshake.bru
        AUTH = response['auth']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/0_setup/json-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/json-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter=4&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/json-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/bookmark/json-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/live_stream/json-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamejson&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_create.bru
        CREATEDPLAYLIST = response['id']

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_json&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/playlist/json-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/podcast/json-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/share/json-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_json&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_json@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET CREATED).bru
            CREATEDUSER = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_json&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_json&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_json@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user (GET REGISTERED).bru
            CREATEDUSER = response['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/create/user/json-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_json&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)


        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genres.bru
        GENREID = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-democratic\.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691768&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/json/json-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

        FORMAT = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", (FORMAT + "-responses")) + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&user=notauser&auth=badkey&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-handshake.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=handshake&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-handshake.bru
        AUTH = response["auth"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-ping TOKEN.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/0_setup/xml-ping.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=ping&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (no auth)", {}), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_create&filter={self.songid}&type=song&position=0&client=python3-ampache&include=False&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented bookmark_create " + VERSION)
        else:
            CREATEDBOOKMARK = response["bookmark"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_edit&filter={CREATEDBOOKMARK}&type=bookmark&position=10&client=python3-ampache&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-get_bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=get_bookmark&filter={self.songid}&type=song&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/xml-bookmark.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark&filter={CREATEDBOOKMARK}&include=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/bookmark/xml-bookmark_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmark_delete&filter={CREATEDBOOKMARK}&type=bookmark&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_create&name={RADIONAME}&url={STREAMURL}&codec=ogg&catalog={self.musiccatalogid}&api_url={STREAMHOMEURL}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_stream_create " + VERSION)
        else:
            CREATEDLIVESTREAM = response["live_stream"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_edit&filter={CREATEDLIVESTREAM}&api_url=http%3A%2F%2Fampache.org&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/live_stream/xml-live_stream_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream_delete&filter={CREATEDLIVESTREAM}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_create&name=renamexml&type=private&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_create.bru
        CREATEDPLAYLIST = response["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache4/xml/create/playlist/xml-playlist_hash.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_hash&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_add.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add&filter={CREATEDPLAYLIST}&id={self.playlistid}&type=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_add_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_add_song&song={self.songid}&filter={CREATEDPLAYLIST}&check=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_edit.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_edit&filter={CREATEDPLAYLIST}&name={EXAMPLEPLAYLISTNAME}_xml&type=public&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_remove_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_remove_song&filter={CREATEDPLAYLIST}&track=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_songs&filter={CREATEDPLAYLIST}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/playlist/xml-playlist_delete.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_delete&filter={CREATEDPLAYLIST}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_create&url={PODCASTFEEDURL}&catalog={self.podcastcatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_create " + VERSION)
        else:
            CREATEDPODCAST = response["podcast"]['id']

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_edit&filter={CREATEDPODCAST}&copyright=False&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-update_podcast.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/podcast/xml-podcast_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_delete&filter={CREATEDPODCAST}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share_create&filter={self.songid}&type=song&expires=7&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_create.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented share_create " + VERSION)
        else:
            CREATEDSHARE = response["share"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_edit&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/share/xml-share_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=share_delete&filter={CREATEDSHARE}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_xml&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_xml@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_create.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_create&username={TEMPUSERNAME}_xml&password=b4aa92f0f88c335369e52058b5d432a5e1b40440663bd97e86d9a796899acaf9&email={TEMPUSERNAME}_xml@gmail.com&disable=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET CREATED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET CREATED).bru
            CREATEDUSER = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_update.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_update&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_edit.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_edit&username={TEMPUSERNAME}_xml&disable=1&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_preference.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preference&username={TEMPUSERNAME}_xml&filter=ajax_load&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_preferences.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_preferences&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_delete.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={TEMPUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-register.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=register&username={REGISTERUSERNAME}_xml&fullname=fullname&password=password98hf29hf2390h&email={REGISTERUSERNAME}_xml@email.com&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented user_create " + VERSION)
        else:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET REGISTERED).bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

            # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user (GET REGISTERED).bru
            CREATEDUSER = response["user"]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/create/user/xml-user_delete REGISTERED.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=user_delete&username={REGISTERUSERNAME}_xml&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=album&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=artist&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-advanced_search.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=advanced_search&operator=or&type=song&offset=0&limit=4&random=0&rule_1=artist&rule_1_operator=2&rule_1_input=Pro&rule_2=artist&rule_2_operator=2&rule_2_input=Ma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-album.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album&filter={self.albumid}include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-album_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=album_songs&filter={self.albumid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=albums&filter={self.albumname}&exact=1&include=songs&offset=0&limit=10&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_albums&filter={self.artistid}&offset=0&limit=4&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artist_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artist_songs&filter={self.songartistid}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=artists&filter={self.artistid}&include=albums&include=songs&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include songs,albums)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-bookmarks.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=bookmarks&include=1&version={VERSION}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&type=root&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumid}&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.albumartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.artistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.musiccatalogid}&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.podcastcatalogid}&filter={self.podcastid}&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-browse.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=browse&catalog={self.musiccatalogid}&filter={self.songartistid}&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog&filter=1&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_file.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_file&task=clean&file={self.songfilepath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_folder.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_folder&task=clean&folder={self.songdirpath}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)


        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=add_to_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (add_to_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean_catalog&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (clean_catalog)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalog_action.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalog_action&task=clean&catalog={self.videocatalogid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-catalogs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=catalogs&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-deleted_podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_podcast_episodes&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-deleted_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-deleted_videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=deleted_videos&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-flag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=flag&type=song&id={self.songid}&flag=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-followers.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=followers&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-following.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=following&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-friends_timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=friends_timeline&limit=4&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tags&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genres.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genres&filter=D&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genres.bru
        GENREID = response["genre"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre&filter={GENREID}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-genre_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=genre_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag_albums.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_albums&filter={GENREID}&offset=0&limit=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_artists&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-tag_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=tag_songs&filter={GENREID}&offset=0&limit=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-index.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=index&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-get_indexes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=get_indexes&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=album_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (album_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=catalog&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (catalog with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=live_stream&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (live_stream with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=playlist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (playlist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=podcast_episode&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (podcast_episode with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=share&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (share with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song_artist&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (song_artist with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=0&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=video&include=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}  (video with include)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-label.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-label_artists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=label_artists&filter=2&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-labels.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=labels&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-last_shouts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=last_shouts&username=user&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-license.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-license_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=license_songs&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-licenses.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=licenses&update=4&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-list.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=list&type=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-live_streams.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=live_streams&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-live_streams.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented live_streams " + VERSION)
        else:
            LIVESTREAMID = response["live_stream"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-live_stream.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=live_stream&filter={LIVESTREAMID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-localplay.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=localplay&command=stop&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-democratic.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=democratic&method=playlist&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=id&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (id)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=index&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (index)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlist_generate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlist_generate&mode=random&format=song&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=playlists&filter={self.playlistname}&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast&filter=1&include=episodes&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (include episodes)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast_episodes.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episodes&filter=1&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast_episodes.bru
        if 'error' in response and response["error"]["errorCode"] == "4705":
            print("Not Implemented podcast_episodes " + VERSION)
        else:
            PODCASTEPISODEID = response["podcast_episode"][0]["id"]

            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcast_episode.bru
            api_url = f"{URL}/server/{FORMAT}.server.php?action=podcast_episode&filter={PODCASTEPISODEID}&version={VERSION}"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-podcasts.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=podcasts&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-rate.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=rate&type=song&id={self.songid}&rating=5&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-record_play.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=record_play&id={self.songid}&user=user&client=debug&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song={self.scrobblesong}&artist={self.scrobbleartist}&album={self.scrobblealbum}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-scrobble.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=scrobble&client=debug&date=1749691776&song=not&artist=not&album=not&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (error)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-now_playing.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=now_playing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=all&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (all)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=music&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (music)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_group.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_group&operator=or&type=podcast&offset=0&limit=4&random=0&rule_1=title&rule_1_operator=0&rule_1_input=D&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (podcast)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-search_songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=search_songs&filter=Da&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-share.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=share&filter=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-shares.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=shares&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-song_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=song_tags&filter={self.songid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-songs.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=songs&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=album&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (album)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=artist&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (artist)", self.headers), FORMAT)
        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-stats.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=stats&type=song&filter=newest&offset=0&limit=2&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)} (song)", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preferences.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preferences&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_preferences=.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_preference&filter=ajax_loadversion={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-system_update.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=system_update&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-timeline.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=timeline&username=user&limit=10&since=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-toggle_follow.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=toggle_follow&username={self.followusername}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_art.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_art&type=album&id={self.albumid}&overwrite=1&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_artist_info.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_artist_info&id={self.artistid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_from_tags.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_from_tags&type=album&id={self.albumid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-update_podcast.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=update_podcast&filter={self.podcastid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-url_to_song.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=url_to_song&url={URL}%2Fplay%2Findex.php%3Fssid%3Deeb9f1b6056246a7d563f479f518bb34%26type%3Dsong%26oid%3D{self.songid}%26uid%3D4%26player%3Dapi%26name%3DSynthetic%20-%20BrownSmoke.wma&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user&username=user&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_playlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_playlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-user_smartlists.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=user_smartlists&offset=0&limit=4&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-users.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=users&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-video.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=video&filter={self.videoid}&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/ampache/ampache6/xml/xml-videos.bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=videos&offset=0&limit=0&version={VERSION}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

    def opensubsonic(self):
        self.ampache_connection.set_debug(False)

        FORMAT = 'json'

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/0_setup/json-preference_edit (SET OPENSUBSONIC).bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=preference_edit&filter=subsonic_legacy&value=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        SONGPREFIX = "so-"
        SONGPREFIX2 = "so-"
        ALBUMPREFIX = "al-"
        ARTISTPREFIX = "ar-"
        PLAYLISTPREFIX = "pl-"
        VIDEOPREFIX = "vi-"

        # python3-ampache6/docs/ampache-subsonic
        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "opensubsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
            if radio["name"] == "4ZZZ Community Radio":
                CREATEDRADIO = radio["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-updateInternetRadioStation.bru
        api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}&id={CREATEDRADIO}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/live_stream/json-deleteInternetRadioStation.bru
        api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&name=testcreate&songId={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-createPlaylist.bru
        CREATEDPLAYLIST = response["subsonic-response"]["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-updatePlaylist.bru
        api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&playlistId={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/playlist/json-deletePlaylist.bru
        api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET CREATED).bru
        for channel in response["subsonic-response"]["podcasts"]["channel"]:
            if channel["title"] == "Dolly Parton's America":
                CREATEDPODCAST = channel["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}&includeEpisodes=1"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                CREATEDPODCASTEPISODE = response["subsonic-response"]["podcasts"]["channel"][0]["episode"][0]["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-downloadPodcastEpisode.bru
                api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-deletePodcastEpisode.bru
                api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/podcast/json-deletePodcastChannel.bru
                api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-createShare.bru
        CREATEDSHARE = response["subsonic-response"]["shares"]["share"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-updateShare.bru
        api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/create/share/json-deleteShare.bru
        api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={FORMAT}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={FORMAT}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getInternetRadioStations.bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={FORMAT}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={PLAYLISTPREFIX}{self.playlistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={FORMAT}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={VIDEOPREFIX}{self.videoid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX2}{self.songid2}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={FORMAT}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={FORMAT}&apiKey={TOKEN}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&current={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

        FORMAT = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "opensubsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&streamUrl={RADIOSTREAMURL}&name=4ZZZ%20Community%20Radio&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
            if radio["name"] == "4ZZZ Community Radio":
                CREATEDRADIO = radio["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-updateInternetRadioStation.bru
        api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/live_stream/xml-deleteInternetRadioStation.bru
        api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&name=testcreate&songId={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-createPlaylist.bru
        CREATEDPLAYLIST = response["subsonic-response"]["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-updatePlaylist.bru
        api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&playlistId={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/playlist/xml-deletePlaylist.bru
        api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        for channel in response["subsonic-response"]["podcasts"]["channel"]:
            if channel["title"] == "Dolly Parton's America":
                CREATEDPODCAST = channel["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}&includeEpisodes=1"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                CREATEDPODCASTEPISODE = response["subsonic-response"]["podcasts"]["channel"]["episode"][0]["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-downloadPodcastEpisode.bru
                api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-deletePodcastEpisode.bru
                api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/podcast/xml-deletePodcastChannel.bru
                api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX2}{self.songid2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-createShare.bru
        CREATEDSHARE = response["subsonic-response"]["shares"]["share"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-updateShare.bru
        api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/create/share/xml-deleteShare.bru
        api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={FORMAT}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={FORMAT}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX2}{self.songid2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/obensubsonic/xml/xml-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={FORMAT}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={PLAYLISTPREFIX}{self.playlistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={FORMAT}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={VIDEOPREFIX}{self.videoid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={FORMAT}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&current={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/xml/xml-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

    def subsoniclegacy(self):
        self.ampache_connection.set_debug(False)

        FORMAT = 'json'

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/0_setup/json-preference_edit (SET SUBSONIC_LEGACY).bru
        api_url = f"{URL}/server/{FORMAT}.server.php?action=preference_edit&filter=subsonic_legacy&value=1"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', f"{re.search(r'[?&]action=([^&]+)', api_url).group(1)}", self.headers), 'json')

        self.ampache_connection.set_debug(True)

        SONGPREFIX = "300000"
        SONGPREFIX2 = "3000000"
        ALBUMPREFIX = "2000000"
        ARTISTPREFIX = "10000000"
        PLAYLISTPREFIX = "80000000"
        VIDEOPREFIX = "50000000"

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "ampache-subsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&streamUrl={RADIOSTREAMURL}&name=4ZZZ%20Community%20Radio&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-getInternetRadioStations (GET CREATED).bru
        for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
            if radio["name"] == "4ZZZ Community Radio":
                CREATEDRADIO = radio["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-updateInternetRadioStation.bru
        api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/live_stream/json-deleteInternetRadioStation.bru
        api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&name=testcreate&songId={SONGPREFIX2}{self.songid2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-createPlaylist.bru
        CREATEDPLAYLIST = response["subsonic-response"]["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-updatePlaylist.bru
        api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&playlistId={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/playlist/json-deletePlaylist.bru
        api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET CREATED).bru
        for channel in response["subsonic-response"]["podcasts"]["channel"]:
            if channel["title"] == "Dolly Parton's America":
                CREATEDPODCAST = channel["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}&includeEpisodes=1"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-getPodcasts (GET EPISODE).bru
                CREATEDPODCASTEPISODE = response["subsonic-response"]["podcasts"]["channel"][0]["episode"][0]["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-downloadPodcastEpisode.bru
                api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-deletePodcastEpisode.bru
                api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/podcast/json-deletePodcastChannel.bru
                api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX2}{self.songid2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-createShare.bru
        CREATEDSHARE = response["subsonic-response"]["shares"]["share"][0]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-updateShare.bru
        api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/create/share/json-deleteShare.bru
        api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={FORMAT}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={FORMAT}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/opensubsonic/json/json-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getInternetRadioStations.bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={FORMAT}&id=mf-{self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={PLAYLISTPREFIX}{self.playlistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={FORMAT}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={VIDEOPREFIX}{self.videoid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX2}{self.songid2}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={FORMAT}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={FORMAT}&apiKey={TOKEN}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&current={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/json/json-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

        FORMAT = 'xml'

        docpath = os.path.join(BUILD_DIR, "python3-ampache6", "docs", "ampache-subsonic") + SLASH
        if not os.path.exists(docpath):
            os.makedirs(docpath)
        else:
            for root, dirs, files in os.walk(docpath):
                for file in files:
                    if file.endswith(f".{FORMAT}"):
                        os.remove(os.path.join(root, file))

        self.ampache_connection.set_debug_path(docpath)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-createInternetRadioStation.bru
        api_url = f"{URL}/rest/createInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&streamUrl={RADIOSTREAMURL}&name=4ZZZ%20Community%20Radio&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        api_url = f"{URL}/rest/getInternetRadioStations.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-getInternetRadioStations (GET CREATED).bru
        for radio in response["subsonic-response"]["internetRadioStations"]["internetRadioStation"]:
            if radio["name"] == "4ZZZ Community Radio":
                CREATEDRADIO = radio["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-updateInternetRadioStation.bru
        api_url = f"{URL}/rest/updateInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}&streamUrl={RADIOSTREAMURL}&name={STREAMNAME}&homepageUrl={RADIOHOMEURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/live_stream/xml-deleteInternetRadioStation.bru
        api_url = f"{URL}/rest/deleteInternetRadioStation.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDRADIO}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-createPlaylist.bru
        api_url = f"{URL}/rest/createPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&name=testcreate&songId={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-createPlaylist.bru
        CREATEDPLAYLIST = response["subsonic-response"]["playlist"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-updatePlaylist.bru
        api_url = f"{URL}/rest/updatePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&playlistId={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/playlist/xml-deletePlaylist.bru
        api_url = f"{URL}/rest/deletePlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPLAYLIST}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-createPodcastChannel.bru
        api_url = f"{URL}/rest/createPodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&url={PODCASTFEEDURL}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&includeEpisodes=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET CREATED).bru
        for channel in response["subsonic-response"]["podcasts"]["channel"]:
            if channel["title"] == "Dolly Parton's America":
                CREATEDPODCAST = channel["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}&includeEpisodes=1"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-getPodcasts (GET EPISODE).bru
                CREATEDPODCASTEPISODE = response["subsonic-response"]["podcasts"]["channel"]["episode"][0]["id"]

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-downloadPodcastEpisode.bru
                api_url = f"{URL}/rest/downloadPodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-deletePodcastEpisode.bru
                api_url = f"{URL}/rest/deletePodcastEpisode.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCASTEPISODE}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

                # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/podcast/xml-deletePodcastChannel.bru
                api_url = f"{URL}/rest/deletePodcastChannel.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDPODCAST}"
                response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-createShare.bru
        api_url = f"{URL}/rest/createShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX2}{self.songid2}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [VARS] /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-createShare.bru
        CREATEDSHARE = response["subsonic-response"]["shares"]["share"]["id"]

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-updateShare.bru
        api_url = f"{URL}/rest/updateShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/create/share/xml-deleteShare.bru
        api_url = f"{URL}/rest/deleteShare.view?v=1.16.1&c=Ampache&f={FORMAT}&id={CREATEDSHARE}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-addChatMessage.bru
        api_url = f"{URL}/rest/addChatMessage.view?v=1.16.1&c=Ampache&f={FORMAT}&message=Api%20Script%20Testing"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-changePassword.bru
        api_url = f"{URL}/rest/changePassword.view?v=1.16.1&c=Ampache&f={FORMAT}&username=demo&password={DEMOPASSWORD}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-createBookmark.bru
        api_url = f"{URL}/rest/createBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&position=2000"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-deleteBookmark.bru
        api_url = f"{URL}/rest/deleteBookmark.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-createUser.bru
        api_url = f"{URL}/rest/createUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-updateUser.bru
        api_url = f"{URL}/rest/updateUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created&password=34563737hdfrthdrt&email=created@gmail.com"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-deleteUser.bru
        api_url = f"{URL}/rest/deleteUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username=created"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbum.bru
        api_url = f"{URL}/rest/getAlbum.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumInfo.bru
        api_url = f"{URL}/rest/getAlbumInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumInfo2.bru
        api_url = f"{URL}/rest/getAlbumInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ALBUMPREFIX}{self.albumid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumList.bru
        api_url = f"{URL}/rest/getAlbumList.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getAlbumList2.bru
        api_url = f"{URL}/rest/getAlbumList2.view?v=1.16.1&c=Ampache&f={FORMAT}&type=newest"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtist.bru
        api_url = f"{URL}/rest/getArtist.view?v=1.16.1&c=Ampache&f={FORMAT}&id=100000002"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtistInfo.bru
        api_url = f"{URL}/rest/getArtistInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtistInfo2.bru
        api_url = f"{URL}/rest/getArtistInfo2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={ARTISTPREFIX}{self.artistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getArtists.bru
        api_url = f"{URL}/rest/getArtists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getBookmarks.bru
        api_url = f"{URL}/rest/getBookmarks.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getChatMessages.bru
        api_url = f"{URL}/rest/getChatMessages.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getGenres.bru
        api_url = f"{URL}/rest/getGenres.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getIndexes.bru
        api_url = f"{URL}/rest/getIndexes.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getLicense.bru
        api_url = f"{URL}/rest/getLicense.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getLyrics.bru
        api_url = f"{URL}/rest/getLyrics.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.lyricsartist}&title={self.lyricssong}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getMusicDirectory.bru
        api_url = f"{URL}/rest/getMusicDirectory.view?v=1.16.1&c=Ampache&f={FORMAT}&id={self.musiccatalogid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getMusicFolders.bru
        api_url = f"{URL}/rest/getMusicFolders.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getNewestPodcasts.bru
        api_url = f"{URL}/rest/getNewestPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getNowPlaying.bru
        api_url = f"{URL}/rest/getNowPlaying.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPlayQueue.bru
        api_url = f"{URL}/rest/getPlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPlaylist.bru
        api_url = f"{URL}/rest/getPlaylist.view?v=1.16.1&c=Ampache&f={FORMAT}&id={PLAYLISTPREFIX}{self.playlistid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPlaylists.bru
        api_url = f"{URL}/rest/getPlaylists.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getPodcasts.bru
        api_url = f"{URL}/rest/getPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getRandomSongs.bru
        api_url = f"{URL}/rest/getRandomSongs.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getScanStatus.bru
        api_url = f"{URL}/rest/getScanStatus.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getShares.bru
        api_url = f"{URL}/rest/getShares.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSimilarSongs.bru
        api_url = f"{URL}/rest/getSimilarSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSimilarSongs2.bru
        api_url = f"{URL}/rest/getSimilarSongs2.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSong.bru
        api_url = f"{URL}/rest/getSong.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-scrobble.bru
        api_url = f"{URL}/rest/scrobble.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getSongsByGenre.bru
        api_url = f"{URL}/rest/getSongsByGenre.view?v=1.16.1&c=Ampache&f={FORMAT}&genre=Electronic"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getStarred.bru
        api_url = f"{URL}/rest/getStarred.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getStarred2.bru
        api_url = f"{URL}/rest/getStarred2.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getTopSongs.bru
        api_url = f"{URL}/rest/getTopSongs.view?v=1.16.1&c=Ampache&f={FORMAT}&artist={self.scrobbleartist}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getUser.bru
        api_url = f"{URL}/rest/getUser.view?v=1.16.1&c=Ampache&f={FORMAT}&username={self.followusername}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getUsers.bru
        api_url = f"{URL}/rest/getUsers.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getVideoInfo.bru
        api_url = f"{URL}/rest/getVideoInfo.view?v=1.16.1&c=Ampache&f={FORMAT}&id={VIDEOPREFIX}{self.videoid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-getVideos.bru
        api_url = f"{URL}/rest/getVideos.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-hls.bru
        #api_url = f"{URL}/rest/hls.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        #response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        if self.localplayenabled:
            # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-jukeboxControl.bru
            api_url = f"{URL}/rest/jukeboxControl.view?v=1.16.1&c=Ampache&f={FORMAT}&action=get"
            response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-ping.bru
        api_url = f"{URL}/rest/ping.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-refreshPodcasts.bru
        api_url = f"{URL}/rest/refreshPodcasts.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-savePlayQueue.bru
        api_url = f"{URL}/rest/savePlayQueue.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&current={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-search2.bru
        api_url = f"{URL}/rest/search2.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-search3.bru
        api_url = f"{URL}/rest/search3.view?v=1.16.1&c=Ampache&f={FORMAT}&query=the&artistCount=20&albumCount=20&songCount=50"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-setRating.bru
        api_url = f"{URL}/rest/setRating.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}&rating=5"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-star.bru
        api_url = f"{URL}/rest/star.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-startScan.bru
        api_url = f"{URL}/rest/startScan.view?v=1.16.1&c=Ampache&f={FORMAT}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/subsonic/subsoniclegacy/xml/xml-unstar.bru
        api_url = f"{URL}/rest/unstar.view?v=1.16.1&c=Ampache&f={FORMAT}&id={SONGPREFIX}{self.songid}"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, FORMAT, f"{re.search(r'/rest/([a-zA-Z0-9_]+)\.view', api_url).group(1)}", self.headers), FORMAT)

        self.self_check(docpath)

    def cleanup(self):
        self.ampache_connection.set_debug(False)

        # [GET]  /opt/nextcloud/clientsync/Documents/Bruno/Ampache API/z_cleanup/json-preference_edit (SET OPENSUBSONIC).bru
        api_url = f"{URL}/server/json.server.php?action=preference_edit&filter=subsonic_legacy&value=0"
        response = self.parse_response(self.ampache_connection.fetch_url(api_url, 'json', '', self.headers), 'json')

    def self_check(self, docpath):
        if not os.path.isdir(docpath):
            sys.exit("Docpath not found: " + docpath)
            return
        print("Checking files in " + docpath + " for private strings")
        for files in os.listdir(docpath):
            if not os.path.isdir(docpath):
                f = open(os.path.join(docpath, files), 'r', encoding="utf-8")
                filedata = f.read()
                f.close()

                #url_text = URL.replace("https://", "")
                #url_text = URL.replace("http://", "")
                newdata = re.sub('ampache\.lachlandewaard\.org', "music.com.au", filedata)
                newdata = re.sub(r"CDATA\[/media/", "CDATA[/mnt/files-music/ampache-test/", newdata)
                newdata = re.sub(r"\\/media\\/", "\\/mnt\\/files-music\\/ampache-test\\/", newdata)
                #newdata = re.sub(url_text.replace("/", "\\/"), "music.com.au", newdata)
                #newdata = re.sub("http://music.com.au", "https://music.com.au", newdata)
                #newdata = re.sub(r"http:\\/\\/music.com.au", "https:\\/\\/music.com.au", newdata)
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

if __name__ == '__main__':
    runner = AmpacheRunner()
    runner.run_all()
