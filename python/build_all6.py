#!/usr/bin/env python3

import configparser
import os
import re
import shutil
import sys
import subprocess
import time

import ampache

build_dir = os.path.dirname(os.path.realpath(__file__))
ampache_dir = os.getcwd()
OS = os.name
if OS == 'nt':
    SLASH = '\\'
else:
    SLASH = '/'

try:
    file_path = os.path.join(ampache_dir, '..', 'ampache-patch7', 'src', 'Config', 'Init',
                             'InitializationHandlerConfig.php')
    with open(file_path, 'r') as file:
        file_content = file.read()
except FileNotFoundError:
    file_path = os.path.join(ampache_dir, 'ampache-patch7', 'src', 'Config', 'Init', 'InitializationHandlerConfig.php')
    with open(file_path, 'r') as file:
        file_content = file.read()

release_version = re.search(r'[0-9]+\.[0-9]+\.[0-9]+', file_content).group()

# user variables
url = 'https://develop.ampache.dev'
api = 'demodemo'
user = 'demo'
limit = 4
offset = 0
api3_version = '390001'
api4_version = '443000'
api5_version = '5.5.6'
api6_version = '6.9.0'
subsonic_api = '1.16.1'
doc_path = build_dir + SLASH + "docs" + SLASH
song_url = url + '/play/index.php?ssid=eeb9f1b6056246a7d563f479f518bb34&type=song&oid=60&uid=4&player=api&name=Synthetic%20-%20BrownSmoke.wma'
APIVERSION = 0
ENABLEDEBUG = True
ampache_connection = ampache.API()
try:
    length = len(sys.argv)
    if 1 < length:
        url = sys.argv[1]
    if 2 < length:
        api = sys.argv[2]
    if 3 < length:
        user = sys.argv[3]
    if 4 < length:
        if sys.argv[4] == '1':
            ENABLEDEBUG = False
    if 5 < length:
        release_version = sys.argv[5]
except IndexError:
    try:
        if sys.argv[1]:
            APIVERSION = int(sys.argv[1])
    except IndexError:
        APIVERSION = 0
    if not ampache_connection.get_config():
        print()
        sys.exit('ERROR docs' + SLASH + 'examples' + SLASH + 'ampache.json not found and no arguments set')


def get_id(api_format, key, data, exit_file=True):
    try:
        if api_format == 'xml':
            result = False
            for child in data:
                if child.tag == key:
                    result = child.attrib['id']
            if not result:
                sys.exit('ERROR Failed to get id from ' + key)
        else:
            if not data:
                return False
            try:
                result = data[0][key][0]['id']
            except (KeyError, TypeError):
                try:
                    result = data[key][0]['id']
                except (KeyError, TypeError):
                    try:
                        result = data[key]['id']
                    except (KeyError, TypeError):
                        try:
                            result = data['id']
                        except TypeError:
                            try:
                                result = data[0][0]['id']
                            except KeyError:
                                try:
                                    result = data[0]['id']
                                except KeyError:
                                    result = data[0]

        return result
    except:
        if exit_file:
            sys.exit('ERROR Failed to get id from ' + key)
        else:
            pass


def get_value(api_format, key, value, data):
    """ get_value
        This function is used to parse all the various data responses you could get and return an ID.
        There are multiple possiblities depending on API version and we try to cover them all
    """
    try:
        if api_format == 'xml':
            result = False
            for child in data:
                if child.tag == key:
                    result = child.find(value).text
            if not result:
                sys.exit('ERROR Failed to get ' + value + ' from ' + key)
        else:
            if not data:
                return False
            try:
                result = data[0][key][0][value]
            except (KeyError, TypeError):
                try:
                    result = data[key][0][value]
                except (KeyError, TypeError):
                    try:
                        result = data[key][value]
                    except (KeyError, TypeError):
                        try:
                            result = data[value]
                        except TypeError:
                            try:
                                result = data[0][0][value]
                            except KeyError:
                                try:
                                    result = data[0][value]
                                except KeyError:
                                    result = data[0]

            return result
    except:
        sys.exit('ERROR Failed to get ' + value + ' from ' + key)


def build_docs(ampache_url, ampache_api, ampache_user, api_format, api_version):

    """ def set_debug(boolean):
        This function can be used to enable/disable debugging messages
    """
    ampache_connection.set_debug(ENABLEDEBUG)
    ampache_connection.set_format(api_format)
    ampache_connection.set_version(api_version)
    ampache_connection.set_url(ampache_url)
    ampache_connection.set_key(ampache_api)
    ampache_connection.set_user(ampache_user)

    if api_version == api3_version:
        docpath = os.path.join(build_dir, "python3-ampache3", "docs", (api_format + "-responses")) + SLASH
        ampache_connection.set_debug_path(docpath)
        ampache3_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath)
    if api_version == api4_version:
        docpath = os.path.join(build_dir, "python3-ampache4", "docs", (api_format + "-responses")) + SLASH
        ampache_connection.set_debug_path(docpath)
        ampache4_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath)
    if api_version == api5_version:
        docpath = os.path.join(build_dir, "python3-ampache5", "docs", (api_format + "-responses")) + SLASH
        ampache_connection.set_debug_path(docpath)
        ampache5_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath)
    if api_version == api6_version:
        docpath = os.path.join(build_dir, "python3-ampache6", "docs", (api_format + "-responses")) + SLASH
        ampache_connection.set_debug_path(docpath)
        ampache6_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath)
    if api_version == subsonic_api:
        docpath = os.path.join(build_dir, "python3-ampache6", "docs", "ampache-subsonic") + SLASH
        ampache_connection.set_debug_path(docpath)
        subsonic_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath)


def self_check(ampache_url, ampache_api, ampache_session, docpath):
    if not os.path.isdir(docpath):
        return
    print("Checking files in " + docpath + " for private strings")
    for files in os.listdir(docpath):
        f = open(os.path.join(docpath, files), 'r', encoding="utf-8")
        filedata = f.read()
        f.close()

        url_text = ampache_url.replace("https://", "")
        url_text = url_text.replace("http://", "")
        newdata = re.sub(url_text, "music.com.au", filedata)
        newdata = re.sub(r"CDATA\[/media/", "CDATA[/mnt/files-music/ampache-test/", newdata)
        newdata = re.sub(r"\\/media\\/", "\\/mnt\\/files-music\\/ampache-test\\/", newdata)
        #newdata = re.sub(url_text.replace("/", "\\/"), "music.com.au", newdata)
        newdata = re.sub("http://music.com.au", "https://music.com.au", newdata)
        newdata = re.sub(r"http:\\/\\/music.com.au", "https:\\/\\/music.com.au", newdata)
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
        newdata = re.sub(ampache_api, "eeb9f1b6056246a7d563f479f518bb34", newdata)
        newdata = re.sub(ampache_session, "cfj3f237d563f479f5223k23189dbb34", newdata)
        newdata = re.sub('auth=[a-z0-9]*', "auth=eeb9f1b6056246a7d563f479f518bb34", newdata)
        newdata = re.sub('ssid=[a-z0-9]*', "ssid=cfj3f237d563f479f5223k23189dbb34", newdata)

        f = open(os.path.join(docpath, files), 'w', encoding="utf-8")
        f.write(newdata)
        f.close()


def ampache3_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath):
    # send a bad ping
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/ping.xml)
    ampache_connection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampache_connection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake%20\(error\).xml)
    ampache_connection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake.xml)
    ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        ## try time handshake
        mytime = int(time.time())
        encrypted_key = ampache_connection.encrypt_password(ampache_api, mytime)
        ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, ampache_user, mytime, api_version)
        if not ampache_session:
            sys.exit(api_version + ' ERROR Failed to connect to ' + ampache_url)

    #if not ampache_connection.AMPACHE_SERVER == api3_version:
    #    print(ampache_connection.AMPACHE_SERVER)
    #    sys.exit(release_version + ' ERROR incorrect server api version ' + ampache_connection.AMPACHE_SERVER)

    my_ping = ampache_connection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit(api_version + ' ERROR Failed to ping ' + ampache_url)

    # get id lists for the catalog
    search_rules = [['title', 2, '']]
    songs = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    song_list = ampache_connection.get_id_list(songs, 'song')
    if not song_list:
        sys.exit("api3 no songs found")

    albums = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    album_list = ampache_connection.get_id_list(albums, 'album')
    if not album_list:
        sys.exit("api3 no album found")

    artists = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    artist_list = ampache_connection.get_id_list(artists, 'artist')
    if not artist_list:
        sys.exit("api3 no artist found")

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(song\).xml)
    search_song = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    song_id = get_id(api_format, 'song', search_song)
    #print(ampache_connection.get_id_list(search_song, 'song'))
    #print(ampache_connection.get_object_list(search_song, 'song'))
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(album\).xml)
    search_album = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    album_title = get_value(api_format, 'album', 'name', search_album)
    album_title = get_value(api_format, 'album', 'name', search_album)

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(artist\).xml)
    search_artist = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/album.xml)
    album = ampache_connection.album(2, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/album_songs.xml)
    ampache_connection.album_songs(12, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/albums%20\(with include\).xml)
    ampache_connection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/albums.xml)
    ampache_connection.albums(album_title, 1, False, False, 0, 10, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/stats%20\(album\).xml)
    ampache_connection.stats('album', 'newest', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist%20\(with include songs,albums\).xml)
    ampache_connection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist%20\(with include songs\).xml)
    ampache_connection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist%20\(with include albums\).xml)
    ampache_connection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist.xml)
    ampache_connection.artist(19, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist_albums.xml)
    ampache_connection.artist_albums(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist_songs.xml)
    ampache_connection.artist_songs(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists%20\(with include songs,albums\).xml)
    ampache_connection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists%20\(with include songs\).xml)
    ampache_connection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'albums')
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists%20\(with include albums\).xml)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists.xml)
    ampache_connection.artists(False, False, False, offset, limit, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/followers.xml)
    ampache_connection.followers(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/following.xml)
    ampache_connection.following(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/friends_timeline.xml)
    ampache_connection.friends_timeline(limit, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/last_shouts.xml)
    ampache_connection.last_shouts(ampache_user, limit)

    # delete it if it exists first
    lookup = ampache_connection.playlists('rename' + api_format, False, offset, limit)
    delete_id = get_id(api_format, 'playlist', lookup, False)
    ampache_connection.playlist_delete(delete_id)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_create.xml)
    playlist_create = ampache_connection.playlist_create('rename' + api_format, 'private')

    single_playlist = get_id(api_format, 'playlist', playlist_create)
    #print(ampache_connection.get_id_list(playlist_create, 'playlist'))

    #print(ampache_connection.get_object_list(playlist_create, 'playlist'))

    ampache_connection.playlist_add_song(single_playlist, 71, 0)
    ampache_connection.playlist_add_song(single_playlist, 72, 0)
    ampache_connection.playlist_add_song(single_playlist, 54, 0)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_add_song%20\(error\).xml)
    ampache_connection.playlist_add_song(single_playlist, 54, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampache_connection.playlist_add_song(single_playlist, 54, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_add_song.xml)
    ampache_connection.playlist_add_song(single_playlist, 54, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_remove_song.xml)
    ampache_connection.playlist_remove_song(single_playlist, False, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist.xml)
    ampache_connection.playlist(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_songs.xml)
    ampache_connection.playlist_songs(single_playlist, 0, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlists.xml)
    ampache_connection.playlists(False, False, offset, limit)

    lookup = ampache_connection.playlists('rename' + api_format, False, offset, limit)
    delete_id = get_id(api_format, 'playlist', lookup)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_delete.xml)
    ampache_connection.playlist_delete(delete_id)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/rate.xml)
    ampache_connection.rate('song', 93, 0)
    ampache_connection.rate('song', 93, 5)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/search_songs.xml)
    ampache_connection.search_songs(song_title, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/song.xml)
    ampache_connection.song(57)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/songs.xml)
    ampache_connection.songs(False, False, False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tags.xml)
    ampache_connection.tags('D', False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag.xml)
    ampache_connection.tag(4)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_albums.xml)
    tag_albums = ampache_connection.tag_albums(4, 0, 2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_artists.xml)
    tag_artists = ampache_connection.tag_artists(4, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_songs.xml)
    ampache_connection.tag_songs(4, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/localplay.xml)
    ampache_connection.localplay('stop', False, False, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/timeline.xml)
    ampache_connection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/toggle_follow.xml)
    ampache_connection.toggle_follow(toggle)
    ampache_connection.toggle_follow(toggle)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/url_to_song.xml)
    ampache_connection.url_to_song(song_url)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/user%20\(error\).xml)
    ampache_connection.user('nothereman')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/user.xml)
    ampache_connection.user('user')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/videos.xml)
    videos = ampache_connection.videos(False, False, 0, 0)
    single_video = 1

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/video.xml)
    ampache_connection.video(single_video)

    # Clean the files
    self_check(ampache_url, ampache_api, ampache_session, docpath)


def ampache4_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath):
    #TODO
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_similar.xml)

    #ampache_connection.catalog_action('clean_catalog', 2)
    #ampache_connection.catalog_action('add_to_catalog', 2)
    #ampache_connection.democratic()
    #ampache_connection.goodbye()

    ampache_connection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampache_connection.encrypt_string(ampache_api, ampache_user)

    ampache_connection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)

    ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        ## try time handshake
        mytime = int(time.time())
        encrypted_key = ampache_connection.encrypt_password(ampache_api, mytime)
        ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, ampache_user, mytime, api_version)
        if not ampache_session:
            sys.exit(api_version + ' ERROR Failed to connect to ' + ampache_url)

    #if not ampache_connection.AMPACHE_SERVER == api4_version:
    #    print(ampache_connection.AMPACHE_SERVER)
    #    sys.exit(release_version + ' ERROR incorrect server api version ' + ampache_connection.AMPACHE_SERVER)

    my_ping = ampache_connection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit(api_version + ' ERROR Failed to ping ' + ampache_url)

    ampache_connection.url_to_song(song_url)

    myuser = ampache_connection.users()

    tempusername = 'temp_user'
    ampache_connection.user_create(tempusername, 'supoersecretpassword', 'email@gmail.com', False, False)
    ampache_connection.user(tempusername)

    ampache_connection.user_update(tempusername, False, False, False, False, False, False, True, False)
    ampache_connection.user(tempusername)
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (disabled)." + api_format)

    ampache_connection.user_delete(tempusername)

    ampache_connection.user('missing_user')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    myuser = ampache_connection.user('demo')

    get_id(api_format, 'user', myuser)
    #print(ampache_connection.get_id_list(myuser, 'user'))
    #print(ampache_connection.get_object_list(myuser, 'user'))

    single_song = 54
    single_album = 12
    single_video = 1
    single_playlist = 2
    single_artist = 19

    songs = ampache_connection.get_indexes('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song)." + api_format)

    ampache_connection.get_indexes('song', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song with include)." + api_format)

    albums = ampache_connection.get_indexes('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album)." + api_format)

    ampache_connection.get_indexes('album', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album with include)." + api_format)

    artists = ampache_connection.get_indexes('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist)." + api_format)

    ampache_connection.get_indexes('artist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist with include)." + api_format)

    playlists = ampache_connection.get_indexes('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist)." + api_format)

    ampache_connection.get_indexes('playlist', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist with include)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast_episode)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast with include)." + api_format)

    videos = ampache_connection.videos(False, False, 0, 0)

    ampache_connection.video(single_video)

    # get id lists for the catalog
    search_rules = [['title', 2, '']]
    songs = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    song_list = ampache_connection.get_id_list(songs, 'song')
    if not song_list:
        sys.exit("api4 no songs found")

    albums = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    album_list = ampache_connection.get_id_list(albums, 'album')
    if not album_list:
        sys.exit("api4 no album found")

    artists = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    artist_list = ampache_connection.get_id_list(artists, 'artist')
    if not artist_list:
        sys.exit("api4 no artist found")

    playlists = ampache_connection.advanced_search(search_rules, 'or', 'playlist', offset, limit, 0)
    playlist_list = ampache_connection.get_id_list(playlists, 'playlist')

    users = ampache_connection.advanced_search(search_rules, 'or', 'user', offset, limit, 0)
    user_list = ampache_connection.get_id_list(users, 'user')

    videos = ampache_connection.advanced_search(search_rules, 'or', 'video', offset, limit, 0)
    video_list = ampache_connection.get_id_list(videos, 'video')

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    search_song = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    song_id = get_id(api_format, 'song', search_song)
    #print(ampache_connection.get_id_list(search_song, 'song'))
    #print(ampache_connection.get_object_list(search_song, 'song'))
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    search_album = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    album_title = get_value(api_format, 'album', 'name', search_album)

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    search_artist = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    artist_title = get_value(api_format, 'artist', 'name', search_artist)

    ampache_connection.album(2, True)
    if os.path.isfile(docpath + "album." + api_format):
        shutil.move(docpath + "album." + api_format,
                    docpath + "album (with include)." + api_format)

    album = ampache_connection.album(2, False)

    album_title = get_value(api_format, 'album', 'name', album)

    ampache_connection.album_songs(single_album, offset, limit)

    ampache_connection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    albums = ampache_connection.albums(album_title, 1, False, False, 0, 10, False)

    ampache_connection.stats('song', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (song)." + api_format)

    stats = ampache_connection.stats('artist', 'random', ampache_user, False, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (artist)." + api_format)

    single_artist = 19

    stats = ampache_connection.stats('album', 'newest', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    single_album = get_id(api_format, 'album', stats)
    #print(ampache_connection.get_id_list(stats, 'album'))
    #print(ampache_connection.get_object_list(stats, 'album'))
    album_title = get_value(api_format, 'album', 'name', stats)

    ampache_connection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)
    ampache_connection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)
    ampache_connection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)
    artist = ampache_connection.artist(19, False)

    ampache_connection.artist_albums(single_artist, offset, limit)

    ampache_connection.artist_songs(2, offset, limit)

    ampache_connection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'albums')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, False)

    ampache_connection.catalog_action('clean', 2)
    if os.path.isfile(docpath + "catalog_action." + api_format):
        shutil.move(docpath + "catalog_action." + api_format,
                    docpath + "catalog_action (error)." + api_format)

    ampache_connection.flag('song', 93, False)
    ampache_connection.flag('song', 93, True)

    ampache_connection.rate('song', 93, 0)
    ampache_connection.rate('song', 93, 5)

    ampache_connection.record_play(song_id, 4, 'debug')

    ampache_connection.followers(ampache_user)

    ampache_connection.following(ampache_user)

    ampache_connection.friends_timeline(limit, 0)

    ampache_connection.last_shouts(ampache_user, limit)

    # delete it if it exists first
    lookup = ampache_connection.playlists('rename' + api_format, False, offset, limit)
    delete_id = get_id(api_format, 'playlist', lookup, False)
    ampache_connection.playlist_delete(delete_id)

    playlist_create = ampache_connection.playlist_create('rename' + api_format, 'private')

    single_playlist = get_id(api_format, 'playlist', playlist_create)
    #print(ampache_connection.get_id_list(playlist_create, 'playlist'))
    #print(ampache_connection.get_object_list(playlist_create, 'playlist'))

    ampache_connection.playlist_edit(single_playlist, 'documentation ' + api_format, 'public')

    ampache_connection.playlists(False, False, offset, limit)

    ampache_connection.playlists('documentation ' + api_format, False, offset, limit)

    ampache_connection.playlist_add_song(single_playlist, 71, 0)
    ampache_connection.playlist_add_song(single_playlist, 72, 0)
    ampache_connection.playlist_add_song(single_playlist, single_song, 0)
    ampache_connection.playlist_add_song(single_playlist, single_song, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampache_connection.playlist_add_song(single_playlist, single_song, 1)
    ampache_connection.playlist_add_song(single_playlist, single_song, 0)

    ampache_connection.playlist_remove_song(single_playlist, False, 1)

    ampache_connection.playlist(single_playlist)

    ampache_connection.playlist_songs(single_playlist, 0, offset, limit)

    ampache_connection.playlist_delete(single_playlist)

    ampache_connection.playlist_generate('random', False, False, False, False, 'song', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (song)." + api_format)

    ampache_connection.playlist_generate('random', False, False, False, False, 'index', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (index)." + api_format)

    ampache_connection.playlist_generate('random', False, False, False, False, 'id', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (id)." + api_format)

    ampache_connection.scrobble('Hear. Life. Spoken', 'Sub Atari Knives', 'Sub Atari Knives', False, False, False,
                                int(time.time()), 'debug')
    if os.path.isfile(docpath + "scrobble." + api_format):
        shutil.move(docpath + "scrobble." + api_format,
                    docpath + "scrobble (error)." + api_format)

    ampache_connection.scrobble('Sensorisk Deprivation', 'IOK-1', 'Sensorisk Deprivation', False, False, False,
                                int(time.time()), 'debug')
    ampache_connection.record_play(93, ampache_user, 'debug')

    ampache_connection.search_songs(song_title, offset, limit)

    ampache_connection.song(single_song)

    ampache_connection.songs(False, False, False, False, offset, limit)

    genre = ''
    tags = ampache_connection.tags('D', False, offset, limit)
    genre = get_id(api_format, 'tag', tags)

    ampache_connection.tag(genre)

    ampache_connection.tag_albums(genre, 0, 2)

    ampache_connection.tag_artists(genre, 0, 1)

    ampache_connection.tag_songs(genre, 0, 1)

    ampache_connection.licenses(False, False, offset, limit)

    ampache_connection.license(1)

    ampache_connection.license_songs(1)

    catalogs = ampache_connection.catalogs('podcast')
    catalog_id = get_id(api_format, 'catalog', catalogs)

    # delete it if it exists first
    lookup = ampache_connection.podcasts('Trace', False, offset, limit)
    delete_id = get_id(api_format, 'podcast', lookup, False)
    ampache_connection.podcast_delete(delete_id)

    podcast_create = ampache_connection.podcast_create(
        'https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml', catalog_id)
    podcast_id = get_id(api_format, 'podcast', podcast_create)

    ampache_connection.podcast_edit(podcast_id)

    ampache_connection.podcasts(False, False, 0, 4)

    ampache_connection.update_podcast(podcast_id)

    ampache_connection.podcast(1, 'episodes')
    if os.path.isfile(docpath + "podcast." + api_format):
        shutil.move(docpath + "podcast." + api_format,
                    docpath + "podcast (include episodes)." + api_format)

    ampache_connection.podcast(1, False)

    ampache_connection.podcast_episodes(1, offset, limit)

    ampache_connection.podcast_episode(23)

    try:
        ampache_connection.podcast_delete(podcast_id)
    except UnboundLocalError:
        pass

    shares = ampache_connection.shares(False, False, offset, limit)
    share_id = get_id(api_format, 'share', shares)

    ampache_connection.share(share_id)

    share_create = ampache_connection.share_create(single_song, 'song', False, 7)
    share_new = get_id(api_format, 'share', shares)

    ampache_connection.share_edit(share_new, 0, 0, False, False)

    ampache_connection.share_delete(share_new)

    ampache_connection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # unfollow and refollow for timeline stuff
    ampache_connection.toggle_follow(toggle)
    ampache_connection.toggle_follow(toggle)

    ampache_connection.update_from_tags('album', 10)

    ampache_connection.update_artist_info(20)

    ampache_connection.update_art('album', 21, True)

    ampache_connection.localplay('status', False, False, 0)
    if os.path.isfile(docpath + "localplay." + api_format):
        shutil.move(docpath + "localplay." + api_format,
                    docpath + "localplay (status)." + api_format)

    ampache_connection.localplay('stop', False, False, 0)

    ampache_connection.catalogs()

    ampache_connection.catalog(1)

    # Clean the files
    self_check(ampache_url, ampache_api, ampache_session, docpath)


def ampache5_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath):
    #TODO
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/bookmark_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/bookmark_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/bookmark_delete)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/bookmark_delete)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/bookmark_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/bookmark_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/bookmarks.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/bookmarks.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_bookmark.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_bookmark.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_similar.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast_episode_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast_episode_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/preference_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/preference_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/preference_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/preference_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/preference_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/preference_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/song_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/song_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/system_preferences.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/system_preferences.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user_preferences.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user_preferences.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user_preference.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user_preference.xml)

    #ampache_connection.democratic()
    #ampache_connection.goodbye()
    #ampache_connection.catalog_action('clean_catalog', 2)
    #ampache_connection.catalog_action('clean_catalog', 2)
    # BINARY METHOD
    #ampache_connection.get_art(93, 'song', (os.path.join(os.getcwd(), 'get_art.jpg')))

    # send a bad ping
    ampache_connection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampache_connection.encrypt_string(ampache_api, ampache_user)

    ampache_connection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)
    # use correct details
    ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        ## try time handshake
        mytime = int(time.time())
        encrypted_key = ampache_connection.encrypt_password(ampache_api, mytime)
        ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, ampache_user, mytime, api_version)
        if not ampache_session:
            sys.exit(api_version + ' ERROR Failed to connect to ' + ampache_url)

    #if not ampache_connection.AMPACHE_SERVER == api5_version:
    #    print(ampache_connection.AMPACHE_SERVER)
    #    sys.exit(release_version + ' ERROR incorrect server api version ' + ampache_connection.AMPACHE_SERVER)

    my_ping = ampache_connection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit(api_version + ' ERROR Failed to ping ' + ampache_url)

    ampache_connection.system_update()

    ampache_connection.live_streams(False, False, offset, limit)

    ampache_connection.live_stream(3)

    ampache_connection.labels(False, False, offset, limit)

    ampache_connection.label(2)

    ampache_connection.label_artists(2)

    ampache_connection.url_to_song(song_url)

    ampache_connection.users()

    tempusername = 'temp_user'
    ampache_connection.user_create(tempusername, 'supoersecretpassword', 'email@gmail.com', False, False)
    ampache_connection.user(tempusername)

    ampache_connection.user_update(tempusername, False, False, False, False, False, False, True, False)
    ampache_connection.user(tempusername)
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (disabled)." + api_format)

    ampache_connection.user_delete(tempusername)

    ampache_connection.user('missing_user')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    ampache_connection.users()
    myuser = ampache_connection.user(ampache_user)

    get_id(api_format, 'user', myuser)

    songs = ampache_connection.get_indexes('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song)." + api_format)
    single_song = ampache_connection.get_id_list(songs, 'song')[0]
    #print(ampache_connection.get_object_list(songs, 'song'))

    ampache_connection.get_indexes('song', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song with include)." + api_format)

    albums = ampache_connection.get_indexes('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album)." + api_format)
    single_album = ampache_connection.get_id_list(albums, 'album')[0]
    #print(ampache_connection.get_object_list(albums, 'album'))

    ampache_connection.get_indexes('album', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album with include)." + api_format)
    single_album = ampache_connection.get_id_list(albums, 'album')[0]
    #print(ampache_connection.get_object_list(albums, 'album'))
    single_album = 12

    artists = ampache_connection.get_indexes('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist)." + api_format)
    single_artist = ampache_connection.get_id_list(artists, 'artist')[0]
    #print(ampache_connection.get_object_list(artists, 'artist'))

    ampache_connection.get_indexes('artist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist with include)." + api_format)
    single_artist = ampache_connection.get_id_list(artists, 'artist')[0]
    #print(ampache_connection.get_object_list(artists, 'artist'))

    playlists = ampache_connection.get_indexes('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist)." + api_format)
    #single_playlist = ampache_connection.get_id_list(playlists, 'playlist')[0]

    ampache_connection.get_indexes('playlist', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist with include)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast_episode)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast with include)." + api_format)

    videos = ampache_connection.videos(False, False, 0, 0)
    single_video = 1

    ampache_connection.video(single_video)

    # get id lists for the catalog
    search_rules = [['title', 2, '']]
    songs = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    song_list = ampache_connection.get_id_list(songs, 'song')
    if not song_list:
        sys.exit("api5 no songs found")

    albums = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    album_list = ampache_connection.get_id_list(albums, 'album')
    if not album_list:
        sys.exit("api5 no album found")

    artists = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    artist_list = ampache_connection.get_id_list(artists, 'artist')
    if not artist_list:
        sys.exit("api5 no artist found")

    labels = ampache_connection.advanced_search(search_rules, 'or', 'label', offset, limit, 0)
    label_list = ampache_connection.get_id_list(labels, 'label')

    playlists = ampache_connection.advanced_search(search_rules, 'or', 'playlist', offset, limit, 0)
    playlist_list = ampache_connection.get_id_list(playlists, 'playlist')

    podcasts = ampache_connection.advanced_search(search_rules, 'or', 'podcast', offset, limit, 0)
    podcast_list = ampache_connection.get_id_list(podcasts, 'podcast')

    podcast_episodes = ampache_connection.advanced_search(search_rules, 'or', 'podcast_episode', offset, limit, 0)
    podcast_episode_list = ampache_connection.get_id_list(podcast_episodes, 'podcast_episode')

    genres = ampache_connection.advanced_search(search_rules, 'or', 'genre', offset, limit, 0)
    genre_list = ampache_connection.get_id_list(genres, 'genre')

    users = ampache_connection.advanced_search(search_rules, 'or', 'user', offset, limit, 0)
    user_list = ampache_connection.get_id_list(users, 'user')

    videos = ampache_connection.advanced_search(search_rules, 'or', 'video', offset, limit, 0)
    video_list = ampache_connection.get_id_list(videos, 'video')

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    search_song = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    song_id = get_id(api_format, 'song', search_song)
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    search_album = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    album_title = get_value(api_format, 'album', 'name', search_album)

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    search_artist = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    artist_title = get_value(api_format, 'artist', 'name', search_artist)

    ampache_connection.album(2, True)
    if os.path.isfile(docpath + "album." + api_format):
        shutil.move(docpath + "album." + api_format,
                    docpath + "album (with include)." + api_format)

    album = ampache_connection.album(2, False)

    album_title = get_value(api_format, 'album', 'name', album)

    ampache_connection.album_songs(single_album, offset, limit)

    ampache_connection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    albums = ampache_connection.albums(album_title, 1, False, False, 0, 10, False)

    ampache_connection.stats('song', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (song)." + api_format)

    stats = ampache_connection.stats('artist', 'random', ampache_user, False, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (artist)." + api_format)

    single_artist = 19

    stats = ampache_connection.stats('album', 'newest', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    single_album = get_id(api_format, 'album', stats)
    album_title = get_value(api_format, 'album', 'name', album)

    ampache_connection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)
    ampache_connection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)
    ampache_connection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)
    ampache_connection.artist(16, False)

    ampache_connection.artist_albums(single_artist, offset, limit)

    ampache_connection.artist_songs(2, offset, limit)

    ampache_connection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'albums')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, False)

    ampache_connection.catalog_action('clean', 2)
    if os.path.isfile(docpath + "catalog_action." + api_format):
        shutil.move(docpath + "catalog_action." + api_format,
                    docpath + "catalog_action (error)." + api_format)

    ampache_connection.flag('playlist', 2, True)
    ampache_connection.flag('song', 93, False)
    ampache_connection.flag('song', 93, True)

    ampache_connection.rate('playlist', 2, 2)
    ampache_connection.rate('song', 93, 0)
    ampache_connection.rate('song', 93, 5)

    ampache_connection.record_play(song_id, 4, 'debug')

    ampache_connection.followers(ampache_user)

    ampache_connection.following(ampache_user)

    ampache_connection.friends_timeline(limit, 0)

    ampache_connection.last_shouts(ampache_user, limit)

    # delete it if it exists first
    lookup = ampache_connection.playlists('rename' + api_format, False, offset, limit)
    delete_id = get_id(api_format, 'playlist', lookup, False)
    ampache_connection.playlist_delete(delete_id)

    playlist_create = ampache_connection.playlist_create('rename' + api_format, 'private')

    single_playlist = get_id(api_format, 'playlist', playlist_create)
    #print(ampache_connection.get_id_list(playlist_create, 'playlist'))
    #print(ampache_connection.get_object_list(playlist_create, 'playlist'))

    ampache_connection.playlist_edit(single_playlist, 'documentation ' + api_format, 'public')

    ampache_connection.playlists(False, False, offset, limit)

    ampache_connection.playlists('documentation ' + api_format, False, offset, limit)

    ampache_connection.playlist_add_song(single_playlist, 71, 0)
    ampache_connection.playlist_add_song(single_playlist, 72, 0)
    ampache_connection.playlist_add_song(single_playlist, single_song, 0)
    ampache_connection.playlist_add_song(single_playlist, single_song, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampache_connection.playlist_add_song(single_playlist, single_song, 1)
    ampache_connection.playlist_add_song(single_playlist, single_song, 0)

    ampache_connection.playlist_remove_song(single_playlist, False, 1)

    ampache_connection.playlist(single_playlist)

    ampache_connection.playlist_songs(single_playlist, 0, offset, limit)

    ampache_connection.playlist_delete(single_playlist)

    ampache_connection.playlist_generate('random', False, False, False, False, 'song', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (song)." + api_format)

    ampache_connection.playlist_generate('random', False, False, False, False, 'index', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (index)." + api_format)

    ampache_connection.playlist_generate('random', False, False, False, False, 'id', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (id)." + api_format)

    ampache_connection.scrobble('Hear. Life. Spoken', 'Sub Atari Knives', 'Sub Atari Knives', False, False, False,
                                int(time.time()), 'debug')
    if os.path.isfile(docpath + "scrobble." + api_format):
        shutil.move(docpath + "scrobble." + api_format,
                    docpath + "scrobble (error)." + api_format)

    ampache_connection.scrobble('Sensorisk Deprivation', 'IOK-1', 'Sensorisk Deprivation', False, False, False,
                                int(time.time()), 'debug')

    ampache_connection.record_play(93, ampache_user, 'debug')

    ampache_connection.search_songs(song_title, offset, limit)

    ampache_connection.song(single_song)

    ampache_connection.songs(False, False, False, False, offset, limit)

    genre = ''
    tags = ampache_connection.genres('D', False, offset, limit)
    genre = get_id(api_format, 'genre', tags)

    ampache_connection.genre(genre)

    ampache_connection.genre_albums(genre, 0, 2)

    ampache_connection.genre_artists(genre, 0, 1)

    ampache_connection.genre_songs(genre, 0, 1)

    ampache_connection.licenses(False, False, offset, limit)

    ampache_connection.license(1)

    ampache_connection.license_songs(1)

    ampache_connection.labels(False, False, offset, limit)

    ampache_connection.label(2)

    ampache_connection.label_artists(2)

    catalogs = ampache_connection.catalogs('podcast')
    catalog_id = get_id(api_format, 'catalog', catalogs)

    # delete it if it exists first
    lookup = ampache_connection.podcasts('Trace', False, offset, limit)
    delete_id = get_id(api_format, 'podcast', lookup, False)
    ampache_connection.podcast_delete(delete_id)

    podcast_create = ampache_connection.podcast_create(
        'https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml', catalog_id)
    podcast_id = get_id(api_format, 'podcast', podcast_create)

    ampache_connection.podcast_edit(podcast_id)

    ampache_connection.podcasts(False, False, 0, 4)

    ampache_connection.update_podcast(podcast_id)

    ampache_connection.podcast(1, 'episodes')
    if os.path.isfile(docpath + "podcast." + api_format):
        shutil.move(docpath + "podcast." + api_format,
                    docpath + "podcast (include episodes)." + api_format)

    ampache_connection.podcast(1, False)

    ampache_connection.podcast_episodes(1, offset, limit)

    ampache_connection.podcast_episode(23)

    ampache_connection.podcast_delete(podcast_id)

    shares = ampache_connection.shares(False, False, offset, limit)
    share_id = ampache_connection.get_id_list(shares, 'share')[0]
    #print(ampache_connection.get_object_list(shares, 'share'))

    ampache_connection.share(share_id)

    share_create = ampache_connection.share_create(single_song, 'song', False, 7)
    share_new = get_id(api_format, 'share', share_create)

    ampache_connection.share_edit(share_new, 0, 0, False, False)

    ampache_connection.share_delete(share_new)

    ampache_connection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # unfollow and refollow for timeline stuff
    ampache_connection.toggle_follow(toggle)
    ampache_connection.toggle_follow(toggle)

    ampache_connection.update_from_tags('album', 10)

    ampache_connection.update_artist_info(26)

    ampache_connection.update_art('album', 21, True)

    ampache_connection.localplay('status', False, False, 0)
    if os.path.isfile(docpath + "localplay." + api_format):
        shutil.move(docpath + "localplay." + api_format,
                    docpath + "localplay (status)." + api_format)

    ampache_connection.localplay('stop', False, False, 0)

    ampache_connection.catalogs()

    ampache_connection.catalog(1)

    ampache_connection.deleted_songs()

    ampache_connection.deleted_podcast_episodes()

    ampache_connection.deleted_videos()

    # Clean the files
    self_check(ampache_url, ampache_api, ampache_session, docpath)


def ampache6_methods(ampache_connection: ampache.API, ampache_url, ampache_api, ampache_user, api_format,
                     api_version, docpath):
    #TODO undocumented methods
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog_folder.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog_folder.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_similar.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/lost_password.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/lost_password.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast_episode_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast_episode_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/preference_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/preference_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/preference_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/preference_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/preference_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/preference_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/song_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/song_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/system_preferences.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/system_preferences.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user_preferences.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user_preferences.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user_preference.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user_preference.xml)

    #ampache_connection.democratic()
    #ampache_connection.goodbye()
    #ampache_connection.catalog_action('clean_catalog', 2)
    #ampache_connection.catalog_action('clean_catalog', 2)
    # BINARY METHOD
    #ampache_connection.get_art(93, 'song', (os.path.join(os.getcwd(), 'get_art.jpg')))

    # send a bad ping
    ampache_connection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    ampache_connection.set_version(api6_version)
    ampache_connection.set_url(ampache_url)
    ampache_connection.set_key(ampache_api)
    ampache_connection.set_user(ampache_user)

    ampache_connection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)
    # use correct details
    # ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    ampache_session = ampache_connection.execute('handshake')
    if not ampache_session:
        ## try time handshake
        mytime = int(time.time())
        encrypted_key = ampache_connection.encrypt_password(ampache_api, mytime)
        ampache_session = ampache_connection.handshake(ampache_url, encrypted_key, ampache_user, mytime, api_version)
        if not ampache_session:
            sys.exit(api_version + ' ERROR Failed to connect to ' + ampache_url)


    #if not ampache_connection.AMPACHE_SERVER == release_version:
    #    print(ampache_connection.AMPACHE_SERVER)
    #    sys.exit(release_version + ' ERROR incorrect server api version ' + ampache_connection.AMPACHE_SERVER)

    my_ping = ampache_connection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit(api_version + ' ERROR Failed to ping ' + ampache_url)

    # Registration should be disabled
    ampache_connection.register('user', 'no', 'passwonord', 'no')
    if os.path.isfile(docpath + "register." + api_format):
        shutil.move(docpath + "register." + api_format,
                    docpath + "register (error)." + api_format)

    ampache_connection.register('username' + api_format, 'fullname', 'password', 'test' + api_format + '@email.com')

    ampache_connection.system_update()

    ampache_connection.live_stream(3)

    stream_name = 'HBR1.com - Tronic Lounge'
    stream_website = 'http://www.hbr1.com/'
    stream_url = 'http://ubuntu.hbr1.com:19800/tronic.ogg'
    stream_codec = 'ogg'

    songs = ampache_connection.get_indexes('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song)." + api_format)
    single_song = ampache_connection.get_id_list(songs, 'song')[0]
    #print(ampache_connection.get_object_list(songs, 'song'))

    tempusername = 'temp_user'
    ampache_connection.user_create(tempusername, 'supoersecretpassword', 'email@gmail.com', False, False)
    ampache_connection.user(tempusername)

    ampache_connection.bookmark_create(55, 'song', 0, 'client1')
    ampache_connection.bookmark_create(54, 'song', 10, 'client')
    ampache_connection.bookmark_create(103, 'song')
    time.sleep(2)
    ampache_connection.bookmark_create(103, 'song')

    # delete it if it exists first
    lookup = ampache_connection.playlists('rename' + api_format, False, offset, limit)
    delete_id = get_id(api_format, 'playlist', lookup, False)
    ampache_connection.playlist_delete(delete_id)

    playlist_create = ampache_connection.playlist_create('rename' + api_format, 'private')
    single_playlist = get_id(api_format, 'playlist', playlist_create)
    #print(ampache_connection.get_id_list(playlist_create, 'playlist'))
    #print(ampache_connection.get_object_list(playlist_create, 'playlist'))

    catalogs = ampache_connection.catalogs('podcast')
    catalog_id = get_id(api_format, 'catalog', catalogs)

    # delete it if it exists first
    lookup = ampache_connection.podcasts('Trace', False, offset, limit)
    delete_id = get_id(api_format, 'podcast', lookup, False)
    ampache_connection.podcast_delete(delete_id)

    podcast_create = ampache_connection.podcast_create(
        'https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml', catalog_id)
    podcast_id = get_id(api_format, 'podcast', podcast_create)

    share_create = ampache_connection.share_create(single_song, 'song', False, 7)
    share_new = get_id(api_format, 'share', share_create)

    catalog_id = 1

    ampache_connection.live_stream_create(stream_name, stream_url, stream_codec, catalog_id, stream_website)

    single_live_stream = ampache_connection.live_streams(stream_name)
    live_stream_new = get_id(api_format, 'live_stream', single_live_stream)

    ampache_connection.live_stream_edit(live_stream_new, False, False, False, False, "http://ampache.org")

    ampache_connection.live_stream_delete(live_stream_new)

    ampache_connection.live_streams(False, False, offset, limit)

    ampache_connection.labels(False, False, offset, limit)

    ampache_connection.label(2)

    ampache_connection.label_artists(2)

    ampache_connection.url_to_song(song_url)

    ampache_connection.browse()
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (root)." + api_format)

    ampache_connection.browse(2, 'podcast', 3)
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (podcast)." + api_format)

    ampache_connection.browse(19, 'artist', 1)
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (artist)." + api_format)

    ampache_connection.browse(12, 'album', 1)
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (album)." + api_format)

    ampache_connection.browse(1, 'catalog')
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (music catalog)." + api_format)

    ampache_connection.browse(2, 'catalog')
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (video catalog)." + api_format)

    ampache_connection.browse(3, 'catalog')
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (podcast catalog)." + api_format)

    ampache_connection.browse()

    ampache_connection.users()

    ampache_connection.user_edit(tempusername, False, False, False, False, False, False, True, False)
    ampache_connection.user(tempusername)
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (disabled)." + api_format)

    ampache_connection.user_delete(tempusername)

    ampache_connection.user('missing_user')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    ampache_connection.users()
    myuser = ampache_connection.user(ampache_user)

    get_id(api_format, 'user', myuser)

    ampache_connection.user_playlists(False, False, offset, limit)

    ampache_connection.user_smartlists(False, False, offset, limit)

    ampache_connection.index('catalog', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (catalog)." + api_format)

    ampache_connection.index('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (song)." + api_format)

    ampache_connection.index('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (album)." + api_format)

    ampache_connection.index('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (artist)." + api_format)

    ampache_connection.index('album_artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (album_artist)." + api_format)

    ampache_connection.index('song_artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (song_artist)." + api_format)

    ampache_connection.index('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (playlist)." + api_format)

    ampache_connection.index('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (podcast)." + api_format)

    ampache_connection.index('podcast_episode', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (podcast_episode)." + api_format)

    ampache_connection.index('video', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (video)." + api_format)

    ampache_connection.index('live_stream', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (live_stream)." + api_format)

    ampache_connection.index('catalog', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (catalog with include)." + api_format)

    ampache_connection.index('song', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (song with include)." + api_format)

    ampache_connection.index('album', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (album with include)." + api_format)

    ampache_connection.index('artist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (artist with include)." + api_format)

    ampache_connection.index('album_artist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (album_artist with include)." + api_format)

    ampache_connection.index('song_artist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (song_artist with include)." + api_format)

    ampache_connection.index('playlist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (playlist with include)." + api_format)

    ampache_connection.index('podcast', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (podcast with include)." + api_format)

    ampache_connection.index('podcast_episode', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (podcast_episode with include)." + api_format)

    ampache_connection.index('video', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (video with include)." + api_format)

    ampache_connection.index('live_stream', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "index." + api_format):
        shutil.move(docpath + "index." + api_format,
                    docpath + "index (live_stream with include)." + api_format)

    ampache_connection.list('song', False, False, False, False, offset, limit)

    ampache_connection.get_indexes('song', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song with include)." + api_format)

    albums = ampache_connection.get_indexes('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album)." + api_format)
    single_album = ampache_connection.get_id_list(albums, 'album')[0]
    #print(ampache_connection.get_object_list(albums, 'album'))

    ampache_connection.get_indexes('album', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album with include)." + api_format)
    single_album = ampache_connection.get_id_list(albums, 'album')[0]
    #print(ampache_connection.get_object_list(albums, 'album'))
    single_album = 12

    artists = ampache_connection.get_indexes('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist)." + api_format)
    single_artist = ampache_connection.get_id_list(artists, 'artist')[0]
    #print(ampache_connection.get_object_list(artists, 'artist'))

    ampache_connection.get_indexes('artist', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist with include)." + api_format)
    single_artist = ampache_connection.get_id_list(artists, 'artist')[0]
    #print(ampache_connection.get_object_list(artists, 'artist'))

    playlists = ampache_connection.get_indexes('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist)." + api_format)
    #single_playlist = ampache_connection.get_id_list(playlists, 'playlist')[0]

    ampache_connection.get_indexes('playlist', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist with include)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast_episode)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast)." + api_format)

    ampache_connection.get_indexes('podcast', False, False, False, False, 1, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast with include)." + api_format)

    videos = ampache_connection.videos(False, False, 0, 0)
    single_video = 1

    ampache_connection.video(single_video)

    # get id lists for the catalog
    search_rules = [['title', 2, '']]
    songs = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    song_list = ampache_connection.get_id_list(songs, 'song')
    if not song_list:
        sys.exit("api6 no songs found")

    albums = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    album_list = ampache_connection.get_id_list(albums, 'album')
    if not album_list:
        sys.exit("api6 no album found")

    artists = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    artist_list = ampache_connection.get_id_list(artists, 'artist')
    if not artist_list:
        sys.exit("api6 no artist found")

    labels = ampache_connection.search(search_rules, 'or', 'label', offset, limit, 0)
    label_list = ampache_connection.get_id_list(labels, 'label')

    playlists = ampache_connection.search(search_rules, 'or', 'playlist', offset, limit, 0)
    playlist_list = ampache_connection.get_id_list(playlists, 'playlist')

    podcasts = ampache_connection.search(search_rules, 'or', 'podcast', offset, limit, 0)
    podcast_list = ampache_connection.get_id_list(podcasts, 'podcast')

    podcast_episodes = ampache_connection.search(search_rules, 'or', 'podcast_episode', offset, limit, 0)
    podcast_episode_list = ampache_connection.get_id_list(podcast_episodes, 'podcast_episode')

    genres = ampache_connection.search(search_rules, 'or', 'genre', offset, limit, 0)
    genre_list = ampache_connection.get_id_list(genres, 'genre')

    users = ampache_connection.search(search_rules, 'or', 'user', offset, limit, 0)
    user_list = ampache_connection.get_id_list(users, 'user')

    videos = ampache_connection.search(search_rules, 'or', 'video', offset, limit, 0)
    video_list = ampache_connection.get_id_list(videos, 'video')

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    ampache_connection.search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "search." + api_format):
        shutil.move(docpath + "search." + api_format,
                    docpath + "search (song)." + api_format)

    search_song = ampache_connection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    song_id = get_id(api_format, 'song', search_song)
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    ampache_connection.search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "search." + api_format):
        shutil.move(docpath + "search." + api_format,
                    docpath + "search (album)." + api_format)
    search_album = ampache_connection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    album_title = get_value(api_format, 'album', 'name', search_album)

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    ampache_connection.search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "search." + api_format):
        shutil.move(docpath + "search." + api_format,
                    docpath + "search (album)." + api_format)
    search_artist = ampache_connection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    artist_title = get_value(api_format, 'artist', 'name', search_artist)

    search_rules = [['favorite', 0, '%'], ['title', 0, 'd']]
    ampache_connection.search_group(search_rules, 'or', 'all', offset, limit, 0)
    if os.path.isfile(docpath + "search_group." + api_format):
        shutil.move(docpath + "search_group." + api_format,
                    docpath + "search_group (all)." + api_format)

    search_rules = [['artist', 0, 'Synthetic']]
    ampache_connection.search_group(search_rules, 'or', 'music', offset, limit, 0)
    if os.path.isfile(docpath + "search_group." + api_format):
        shutil.move(docpath + "search_group." + api_format,
                    docpath + "search_group (music)." + api_format)

    search_rules = [['title', 0, 'D']]
    ampache_connection.search_group(search_rules, 'or', 'podcast', offset, limit, 0)
    if os.path.isfile(docpath + "search_group." + api_format):
        shutil.move(docpath + "search_group." + api_format,
                    docpath + "search_group (podcast)." + api_format)

    ampache_connection.album(2, True)
    if os.path.isfile(docpath + "album." + api_format):
        shutil.move(docpath + "album." + api_format,
                    docpath + "album (with include)." + api_format)

    album = ampache_connection.album(2, False)

    album_title = get_value(api_format, 'album', 'name', album)

    ampache_connection.album_songs(single_album, offset, limit)

    ampache_connection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    albums = ampache_connection.albums(album_title, 1, False, False, 0, 10, False)

    ampache_connection.stats('song', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (song)." + api_format)

    stats = ampache_connection.stats('artist', 'random', ampache_user, False, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (artist)." + api_format)

    single_artist = 19

    stats = ampache_connection.stats('album', 'newest', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    single_album = get_id(api_format, 'album', stats)
    album_title = get_value(api_format, 'album', 'name', stats)

    ampache_connection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)
    ampache_connection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)
    ampache_connection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)
    ampache_connection.artist(16, False)

    ampache_connection.artist_albums(single_artist, offset, limit)

    ampache_connection.artist_songs(2, offset, limit)

    ampache_connection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, 'albums')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    ampache_connection.artists(False, False, False, offset, limit, False)

    ampache_connection.catalog_action('clean', 2)
    if os.path.isfile(docpath + "catalog_action." + api_format):
        shutil.move(docpath + "catalog_action." + api_format,
                    docpath + "catalog_action (error)." + api_format)

    ampache_connection.get_bookmark(54, 'song', 1)
    if os.path.isfile(docpath + "get_bookmark." + api_format):
        shutil.move(docpath + "get_bookmark." + api_format,
                    docpath + "get_bookmark (with include)." + api_format)
    ampache_connection.get_bookmark(54, 'song', 0, 1)
    if os.path.isfile(docpath + "get_bookmark." + api_format):
        shutil.move(docpath + "get_bookmark." + api_format,
                    docpath + "get_bookmark (show all)." + api_format)
    bookmark = ampache_connection.get_bookmark(54, 'song')
    mybookmark = get_id(api_format, 'bookmark', bookmark)

    ampache_connection.bookmarks(False, True)
    if os.path.isfile(docpath + "bookmarks." + api_format):
        shutil.move(docpath + "bookmarks." + api_format,
                    docpath + "bookmarks (with include)." + api_format)
    ampache_connection.bookmarks()

    ampache_connection.bookmark(4, 1)
    if os.path.isfile(docpath + "bookmark." + api_format):
        shutil.move(docpath + "bookmark." + api_format,
                    docpath + "bookmark (with include)." + api_format)
    ampache_connection.bookmark(4)

    ampache_connection.bookmark_edit(mybookmark, 'bookmark', 10)

    ampache_connection.bookmark_delete(mybookmark, 'bookmark')

    ampache_connection.flag('playlist', 2, True)
    ampache_connection.flag('song', 93, False)
    ampache_connection.flag('song', 93, True)

    ampache_connection.rate('playlist', 2, 2)
    ampache_connection.rate('song', 93, 0)
    ampache_connection.rate('song', 93, 5)

    ampache_connection.record_play(song_id, 4, 'debug')

    ampache_connection.followers(ampache_user)

    ampache_connection.following(ampache_user)

    ampache_connection.friends_timeline(limit, 0)

    ampache_connection.last_shouts(ampache_user, limit)

    ampache_connection.playlist_edit(single_playlist, 'documentation ' + api_format, 'public')

    ampache_connection.playlists(False, False, offset, limit)

    ampache_connection.playlists('documentation ' + api_format, False, offset, limit)

    ampache_connection.playlist_add_song(single_playlist, 71, 0)
    ampache_connection.playlist_add_song(single_playlist, 72, 0)
    ampache_connection.playlist_add_song(single_playlist, single_song, 0)
    ampache_connection.playlist_add_song(single_playlist, single_song, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampache_connection.playlist_add_song(single_playlist, single_song, 1)
    ampache_connection.playlist_add_song(single_playlist, single_song, 0)

    ampache_connection.playlist_add(single_playlist, 2, 'playlist')

    ampache_connection.playlist_remove_song(single_playlist, False, 1)

    ampache_connection.playlist(single_playlist)

    ampache_connection.playlist_songs(single_playlist, 0, offset, limit)

    ampache_connection.playlist_hash(single_playlist)

    ampache_connection.playlist_delete(single_playlist)

    ampache_connection.playlist_generate('random', False, False, False, False, 'song', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (song)." + api_format)

    ampache_connection.playlist_generate('random', False, False, False, False, 'index', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (index)." + api_format)

    ampache_connection.playlist_generate('random', False, False, False, False, 'id', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (id)." + api_format)

    ampache_connection.scrobble('Hear. Life. Spoken', 'Sub Atari Knives', 'Sub Atari Knives', False, False, False,
                                int(time.time()), 'debug')
    if os.path.isfile(docpath + "scrobble." + api_format):
        shutil.move(docpath + "scrobble." + api_format,
                    docpath + "scrobble (error)." + api_format)

    ampache_connection.scrobble('Sensorisk Deprivation', 'IOK-1', 'Sensorisk Deprivation', False, False, False,
                                int(time.time()), 'debug')

    ampache_connection.record_play(93, ampache_user, 'debug')

    ampache_connection.search_songs(song_title, offset, limit)

    ampache_connection.song(single_song)

    ampache_connection.song_tags(single_song)

    ampache_connection.songs(False, False, False, False, offset, limit)

    genre = ''
    tags = ampache_connection.genres('D', False, offset, limit)
    genre = get_id(api_format, 'genre', tags)

    ampache_connection.genre(genre)

    ampache_connection.genre_albums(genre, 0, 2)

    ampache_connection.genre_artists(genre, 0, 1)

    ampache_connection.genre_songs(genre, 0, 1)

    ampache_connection.licenses(False, False, offset, limit)

    ampache_connection.license(1)

    ampache_connection.license_songs(1)

    ampache_connection.labels(False, False, offset, limit)

    ampache_connection.label(2)

    ampache_connection.label_artists(2)

    ampache_connection.podcast(1, 'episodes')
    if os.path.isfile(docpath + "podcast." + api_format):
        shutil.move(docpath + "podcast." + api_format,
                    docpath + "podcast (include episodes)." + api_format)

    ampache_connection.podcast(1, False)

    ampache_connection.podcast_episodes(1, offset, limit)

    ampache_connection.podcast_episode(23)

    ampache_connection.podcast_edit(podcast_id)

    ampache_connection.podcasts(False, False, 0, 4)

    ampache_connection.update_podcast(podcast_id)

    ampache_connection.podcast_delete(podcast_id)

    shares = ampache_connection.shares(False, False, offset, limit)
    share_id = ampache_connection.get_id_list(shares, 'share')[0]
    #print(ampache_connection.get_object_list(shares, 'share'))

    ampache_connection.share(share_id)

    ampache_connection.share_edit(share_new, 0, 0, False, False)

    ampache_connection.share_delete(share_new)

    ampache_connection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # unfollow and refollow for timeline stuff
    ampache_connection.toggle_follow(toggle)
    ampache_connection.toggle_follow(toggle)

    ampache_connection.update_from_tags('album', 10)

    ampache_connection.update_artist_info(26)

    ampache_connection.update_art('album', 21, True)

    ampache_connection.localplay('status', False, False, 0)
    if os.path.isfile(docpath + "localplay." + api_format):
        shutil.move(docpath + "localplay." + api_format,
                    docpath + "localplay (status)." + api_format)

    ampache_connection.localplay('stop', False, False, 0)

    ampache_connection.catalogs()

    ampache_connection.catalog(1)

    ampache_connection.deleted_songs()

    ampache_connection.deleted_podcast_episodes()

    ampache_connection.deleted_videos()

    # Clean the files
    self_check(ampache_url, ampache_api, ampache_session, docpath)


def subsonic_methods(ampache_connection, ampache_url, ampache_api, ampache_user, api_format, api_version, docpath):
    # Base subsonic url data
    base_url = ampache_url + "/rest/"

    #token auth
    if ampache_connection.AMPACHE_BEARER_TOKEN:
        headers = {}
        headers['Authorization'] = f'Bearer {ampache_connection.AMPACHE_BEARER_TOKEN}'
        base_parameters = ".view?&v=1.16.1&c=Ampache&f=" + api_format
    else:
        base_parameters = ".view?u=" + ampache_user + "&p=" + ampache_api + "&v=1.16.1&c=Ampache&f=" + api_format

    # Returns an empty <subsonic-response> element on success.
    action = "ping"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getLicense"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)
    fetch_url = base_url + action + base_parameters
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getMusicFolders"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getIndexes"
    # musicFolderId (optional)
    # ifModifiedSince (optional)
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getMusicDirectory"
    # id
    params = '&id=1'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getGenres"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getArtists"
    # musicFolderId (optional)
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getArtist"
    # id
    params = '&id=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getAlbum"
    # id
    params = '&id=200000021'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getSong"
    # id
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getVideos"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getVideoInfo"
    # id
    params = '&id=500000001'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getArtistInfo"
    # id
    # count
    # includeNotPresent
    params = '&id=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getArtistInfo2"
    # id
    # count
    # includeNotPresent
    params = '&id=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getAlbumInfo"
    # id
    params = '&id=200000021'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getAlbumInfo2"
    # id
    params = '&id=200000021'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getSimilarSongs"
    # id
    # count
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getSimilarSongs2"
    # id
    # count
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getTopSongs"
    # artist
    # count
    params = '&artist=Smashing+Pumpkins'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getAlbumList"
    # type
    # size
    # offset
    # fromYear
    # toYear
    # genre
    # musicFolderId
    params = '&type=newest'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getAlbumList2"
    # type
    # size
    # offset
    # fromYear
    # toYear
    # genre
    # musicFolderId
    params = '&type=newest'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getRandomSongs"
    # size
    # genre
    # fromYear
    # toYear
    # musicFolderId
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getSongsByGenre"
    # genre
    # count
    # offset
    # musicFolderId
    params = '&genre=Electronic'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getNowPlaying"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getStarred"
    # musicFolderId
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getStarred2"
    # musicFolderId
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "search"
    # artist
    # album
    # title
    # any
    # count
    # offset
    # newerThan
    params = '&any=m'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "search2"
    # query
    # artistCount
    # artistOffset
    # albumCount
    # albumOffset
    # songCount
    # songOffset
    # musicFolderId
    params = '&query=thet&artistCount=20&albumCount=20&songCount=50'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "search3"
    # query
    # artistCount
    # artistOffset
    # albumCount
    # albumOffset
    # songCount
    # songOffset
    # musicFolderId
    params = '&query=thet&artistCount=20&albumCount=20&songCount=50'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getPlaylists"
    # username
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getPlaylist"
    # id
    params = '&id=1770'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "createPlaylist"
    # playlistId
    # name
    # songId
    params = '&name=testcreate&songId=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updatePlaylist"
    # playlistId
    # name
    # comment
    # public
    # songIdToAdd
    params = '&playlistId=4'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deletePlaylist"
    # id
    params = '&id=291770'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns binary data on success, or an XML document on error (in which case the HTTP content type will start with "text/xml").
    # action = "stream"
    # #id
    # #maxBitRate
    # #format
    # #timeOffset
    # #size
    # #estimateContentLength
    # #converted
    # params = ''
    # fetch_url = base_url + action + base_parameters + params
    # ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns binary data on success, or an XML document on error (in which case the HTTP content type will start with "text/xml").
    # action = "download"
    # #id
    # params = ''
    # fetch_url = base_url + action + base_parameters + params
    # ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "hls"
    # id
    # bitRate
    # audioTrack
    params = '&id=82'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns the raw video captions.
    # action = "getCaptions"
    # #id
    # #format
    # params = '&id=460'
    # fetch_url = base_url + action + base_parameters + params
    # ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns the cover art image in binary form.
    # action = "getCoverArt"
    # #id
    # #size
    # params = ''
    # fetch_url = base_url + action + base_parameters + params
    # ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getLyrics"
    # artist
    # title
    params = '&artist=METISSE&title=What%20to%20do'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns the avatar image in binary form.
    # action = "getAvatar"
    # #username
    # params = '&username=guest'
    # fetch_url = base_url + action + base_parameters + params
    # ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "star"
    # id
    # albumId
    # artistId
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "unstar"
    # id
    # albumId
    # artistId
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "setRating"
    # id
    # rating
    params = '&id=300000060&rating=5'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "scrobble"
    # id
    # time
    # submission
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getShares"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "createShare"
    # id
    # description
    # expires
    params = '&id=300000078'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updateShare"
    # id
    # description
    # expires
    params = '&id=300000075'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteShare"
    # id
    params = '&id=29770'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getPodcasts"
    # includeEpisodes
    # id
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getNewestPodcasts"
    # count
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getPodcasts"
    # includeEpisodes
    # id
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "refreshPodcasts"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "createPodcastChannel"
    # url
    params = '&url=https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deletePodcastChannel"
    # id
    params = '&id=600000003'
    if api_format == 'xml':
        params = '&id=600000004'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "downloadPodcastEpisode"
    # id
    params = '&id=700000102'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deletePodcastEpisode"
    # id
    params = '&id=700000102'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "jukeboxControl"
    # action
    # index
    # offset
    # id
    # gain
    params = '&action=status'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)
    if os.path.isfile(docpath + "jukeboxControl." + api_format):
        shutil.move(docpath + "jukeboxControl." + api_format,
                    docpath + "jukeboxControl (status)." + api_format)
    params = '&action=get'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)
    if os.path.isfile(docpath + "jukeboxControl." + api_format):
        shutil.move(docpath + "jukeboxControl." + api_format,
                    docpath + "jukeboxControl (get)." + api_format)

    action = "getInternetRadioStations"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "createInternetRadioStation"
    # streamUrl
    # name
    # homepageUrl
    # stream_name = 'HBR1.com - Tronic Lounge'
    #     stream_website = 'http://www.hbr1.com/'
    #     stream_url = 'http://ubuntu.hbr1.com:19800/tronic.ogg'
    params = '&streamUrl=https://iheart.4zzz.org.au/4zzz&name=4ZZZ%20Community%20Radio&homepageUrl=https://4zzzfm.org.au'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updateInternetRadioStation"
    # id
    # streamUrl
    # name
    # homepageUrl
    params = '&id=3&streamUrl=https://iheart.4zzz.org.au/4zzz&name=4ZZZ%20Community%20Radio&homepageUrl=https://4zzzfm.org.au'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteInternetRadioStation"
    # id
    params = '&id=29864'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getChatMessages"
    # since
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "addChatMessage"
    # message
    params = '&message=Api%20Script%20Testing'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getUser"
    # username
    params = '&username=guest'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getUsers"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "createUser"
    # username
    # password
    # email
    # ldapAuthenticated
    # adminRole
    # settingsRole
    # streamRole
    # jukeboxRole
    # downloadRole
    # uploadRole
    # playlistRole
    # coverArtRole
    # commentRole
    # podcastRole
    # shareRole
    # videoConversionRole
    # musicFolderId
    params = '&username=created&password=34563737hdfrthdrt&email=created@gmail.com'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updateUser"
    # username
    # password
    # email
    # ldapAuthenticated
    # adminRole
    # settingsRole
    # streamRole
    # jukeboxRole
    # downloadRole
    # uploadRole
    # coverArtRole
    # commentRole
    # podcastRole
    # shareRole
    # videoConversionRole
    # musicFolderId
    # maxBitRate
    params = '&username=created&password=34563737hdfrthdrt&email=created@gmail.com'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteUser"
    # username
    params = '&username=created'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "changePassword"
    # username
    # password
    params = '&username=demo&password=demodemo'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "createBookmark"
    # id
    # position
    # comment
    params = '&id=300000060&position=2000'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getBookmarks"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteBookmark"
    # id
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getPlayQueue"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "savePlayQueue"
    # id
    # current
    # position
    params = '&id=300000060&current=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "getScanStatus"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)

    action = "startScan"
    fetch_url = base_url + action + base_parameters
    ampache_connection.fetch_url(fetch_url, api_format, action)


if APIVERSION == 6:
    build_docs(url, api, user, 'json', api6_version)
    build_docs(url, api, user, 'xml', api6_version)
elif APIVERSION == 5:
    build_docs(url, api, user, 'json', api5_version)
    build_docs(url, api, user, 'xml', api5_version)
elif APIVERSION == 4:
    build_docs(url, api, user, 'json', api4_version)
    build_docs(url, api, user, 'xml', api4_version)
elif APIVERSION == 3:
    build_docs(url, api, user, 'xml', api3_version)
elif APIVERSION == 16:
    build_docs(url, api, user, 'json', subsonic_api)
    build_docs(url, api, user, 'xml', subsonic_api)
else:
    build_docs(url, api, user, 'json', api6_version)
    build_docs(url, api, user, 'xml', api6_version)
    build_docs(url, api, user, 'json', api5_version)
    build_docs(url, api, user, 'xml', api5_version)
    build_docs(url, api, user, 'json', api4_version)
    build_docs(url, api, user, 'xml', api4_version)
    build_docs(url, api, user, 'xml', api3_version)
    build_docs(url, api, user, 'json', subsonic_api)
    build_docs(url, api, user, 'xml', subsonic_api)

print("build_all6.py COMPLETED")
