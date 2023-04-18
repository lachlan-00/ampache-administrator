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
        api = sys.argv[2]
    if sys.argv[3]:
        user = sys.argv[3]
except IndexError:
    if os.path.isfile(os.path.join(os.pardir, 'ampache.conf')):
        conf = configparser.RawConfigParser()
        conf.read(os.path.join(os.pardir, 'ampache.conf'))
        url = conf.get('conf', 'ampache_url')
        api = conf.get('conf', 'ampache_apikey')
        user = conf.get('conf', 'ampache_user')
    elif os.path.isfile('ampache.conf'):
        conf = configparser.RawConfigParser()
        conf.read(os.path.join('ampache.conf'))
        url = conf.get('conf', 'ampache_url')
        api = conf.get('conf', 'ampache_apikey')
        user = conf.get('conf', 'ampache_user')
    elif os.path.isfile('docs/examples/ampyche.conf'):
        conf = configparser.RawConfigParser()
        conf.read('docs/examples/ampyche.conf')
        url = conf.get('conf', 'ampache_url')
        api = conf.get('conf', 'ampache_apikey')
        user = conf.get('conf', 'ampache_user')
    else:
        print()
        sys.exit('Error: docs/examples/ampyche.conf not found and no arguments set')
    try:
        if sys.argv[1]:
            APIVERSION = int(sys.argv[1])
    except IndexError:
        APIVERSION = 0


def build_docs(ampache_url, ampache_api, ampache_user, api_format):
    ampacheConnection = ampache.API()

    """ def set_debug(boolean):
        This function can be used to enable/disable debugging messages
    """
    ampacheConnection.set_debug(True)
    # ampacheConnection.set_debug(False)
    ampacheConnection.set_format(api_format)

    if (api_version == api3_version):
        ampacheConnection.set_debug_path("python3-ampache3/docs/" + api_format + "-responses/")
        docpath = "python3-ampache3/docs/" + api_format + "-responses/"
        ampache3_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)
    if (api_version == api4_version):
        ampacheConnection.set_debug_path("python3-ampache4/docs/" + api_format + "-responses/")
        docpath = "python3-ampache4/docs/" + api_format + "-responses/"
        ampache4_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)
    if (api_version == api5_version):
        ampacheConnection.set_debug_path("python3-ampache5/docs/" + api_format + "-responses/")
        docpath = "python3-ampache5/docs/" + api_format + "-responses/"
        ampache5_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)
    if (api_version == api6_version):
        ampacheConnection.set_debug_path("python3-ampache6/docs/" + api_format + "-responses/")
        docpath = "python3-ampache6/docs/" + api_format + "-responses/"
        ampache6_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)
    if (api_version == subsonic_api):
        ampacheConnection.set_debug_path("python3-ampache6/docs/ampache-subsonic/" + api_format + "-responses/")
        docpath = "subsonic/docs/" + api_format + "-responses/"
        subsonic_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)


def self_check(api_format, ampache_url, ampache_api, ampache_session, docpath):
    print("Checking files in " + docpath + " for private strings")
    for files in os.listdir("./" + docpath):
        f = open("./" + docpath + files, 'r', encoding="utf-8")
        filedata = f.read()
        f.close()

        url_text = ampache_url.replace("https://", "")
        url_text = url_text.replace("http://", "")
        newdata = re.sub(url_text, "music.com.au", filedata)
        newdata = re.sub("CDATA\[\/media\/", "CDATA[/mnt/files-music/ampache-test/", newdata)
        newdata = re.sub("\\\/media\\\/", "\\\/mnt\\\/files-music\\\/ampache-test\\\/", newdata)
        newdata = re.sub(url_text.replace("/", "\\\/"), "music.com.au", newdata)
        newdata = re.sub("http://music.com.au", "https://music.com.au", newdata)
        newdata = re.sub("http:\\\/\\\/music.com.au", "https:\\\/\\\/music.com.au", newdata)
        newdata = re.sub("\"session_expire\": \"*.*\"*", "\"session_expire\": \"2022-08-17T06:21:00+00:00\",", newdata)
        newdata = re.sub("<session_expire>.*</session_expire>", "<session_expire><![CDATA[2022-08-17T04:34:55+00:00]]></session_expire>", newdata)
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
        newdata = re.sub("<sync_date>.*</sync_date>", "<sync_date><![CDATA[2022-08-17T05:07:11+00:00]]></sync_date>", newdata)
        newdata = re.sub(ampache_api, "eeb9f1b6056246a7d563f479f518bb34", newdata)
        newdata = re.sub(ampache_session, "cfj3f237d563f479f5223k23189dbb34", newdata)
        newdata = re.sub('auth=[a-z0-9]*', "auth=eeb9f1b6056246a7d563f479f518bb34", newdata)
        newdata = re.sub('ssid=[a-z0-9]*', "ssid=cfj3f237d563f479f5223k23189dbb34", newdata)

        f = open("./" + docpath + files, 'w', encoding="utf-8")
        f.write(newdata)
        f.close()


def ampache3_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    # send a bad ping
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/ping.xml)
    ampacheConnection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(song\).xml)
    search_song = ampacheConnection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    if api_format == 'xml':
        song_id = search_song[1].attrib['id']
    else:
        song_id = search_song['song'][0]['id']
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(album\).xml)
    search_album = ampacheConnection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    if api_format == 'xml':
        for child in search_album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album['album'][0]['name']

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(artist\).xml)
    search_artist = ampacheConnection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/album.xml)
    album = ampacheConnection.album(2, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/album_songs.xml)
    ampacheConnection.album_songs(12, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/albums%20\(with include\).xml)
    ampacheConnection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/albums.xml)
    ampacheConnection.albums(album_title, 1, False, False, 0, 10, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/stats%20\(album\).xml)
    ampacheConnection.stats('album', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist%20\(with include songs,albums\).xml)
    ampacheConnection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist%20\(with include songs\).xml)
    ampacheConnection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist%20\(with include albums\).xml)
    ampacheConnection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist.xml)
    ampacheConnection.artist(19, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist_albums.xml)
    ampacheConnection.artist_albums(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist_songs.xml)
    ampacheConnection.artist_songs(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists%20\(with include songs,albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists%20\(with include songs\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    ampacheConnection.artists(False, False, False, offset, limit, 'albums')
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists%20\(with include albums\).xml)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists.xml)
    ampacheConnection.artists(False, False, False, offset, limit, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/followers.xml)
    ampacheConnection.followers(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/following.xml)
    ampacheConnection.following(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/friends_timeline.xml)
    ampacheConnection.friends_timeline(limit, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/last_shouts.xml)
    ampacheConnection.last_shouts(ampache_user, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlists.xml)
    ampacheConnection.playlists(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_create.xml)
    playlist_create = ampacheConnection.playlist_create('rename', 'private')
    if api_format == 'xml':
        for child in playlist_create:
            if child.tag == 'playlist':
                tmp_playlist = child.attrib['id']
                single_playlist = tmp_playlist
    else:
        single_playlist = playlist_create[0]['id']

    ampacheConnection.playlist_add_song(single_playlist, 71, 0)
    ampacheConnection.playlist_add_song(single_playlist, 72, 0)
    ampacheConnection.playlist_add_song(single_playlist, 54, 0)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_add_song%20\(error\).xml)
    ampacheConnection.playlist_add_song(single_playlist, 54, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampacheConnection.playlist_add_song(single_playlist, 54, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_add_song.xml)
    ampacheConnection.playlist_add_song(single_playlist, 54, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_remove_song.xml)
    ampacheConnection.playlist_remove_song(single_playlist, False, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist.xml)
    ampacheConnection.playlist(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_songs.xml)
    ampacheConnection.playlist_songs(single_playlist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_delete.xml)
    params = 65
    if (api_format == 'xml'):
        params = 66
    ampacheConnection.playlist_delete(params)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/rate.xml)
    ampacheConnection.rate('song', 93, 0)
    ampacheConnection.rate('song', 93, 5)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/search_songs.xml)
    ampacheConnection.search_songs(song_title, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/song.xml)
    ampacheConnection.song(57)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/songs.xml)
    ampacheConnection.songs(False, False, False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tags.xml)
    ampacheConnection.tags('D', False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag.xml)
    ampacheConnection.tag(4)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_albums.xml)
    tag_albums = ampacheConnection.tag_albums(4, 0, 2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_artists.xml)
    tag_artists = ampacheConnection.tag_artists(4, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_songs.xml)
    ampacheConnection.tag_songs(4, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/localplay.xml)
    ampacheConnection.localplay('stop', False, False, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/timeline.xml)
    ampacheConnection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/toggle_follow.xml)
    ampacheConnection.toggle_follow(toggle)
    ampacheConnection.toggle_follow(toggle)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/url_to_song.xml)
    ampacheConnection.url_to_song(song_url)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/user%20\(error\).xml)
    ampacheConnection.user('nothereman')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/user.xml)
    ampacheConnection.user('user')


    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/videos.xml)
    videos = ampacheConnection.videos(False, False, 0, 0)
    single_video = 1

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/video.xml)
    ampacheConnection.video(single_video)

    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


def ampache4_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    #TODO
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_similar.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_action%20\(clean_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_action%20\(clean_catalog\).xml)
    #ampacheConnection.catalog_action('clean_catalog', 2)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_action%20\(add_to_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_action%20\(add_to_catalog\).xml)
    #ampacheConnection.catalog_action('add_to_catalog', 2)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/democratic%20\(play\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/democratic%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/democratic%20\(vote\).json)
    #ampacheConnection.democratic()
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/goodbye.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/goodbye.xml)
    #ampacheConnection.goodbye()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/ping.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/ping.xml)
    ampacheConnection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/handshake%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/handshake.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/url_to_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/url_to_song.xml)
    ampacheConnection.url_to_song(song_url)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/users.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/users.xml)
    myuser = ampacheConnection.users()

    tempusername = 'temp_user'
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user_create.xml)
    ampacheConnection.user_create(tempusername, 'supoersecretpassword', 'email@gmail.com', False, False)
    ampacheConnection.user(tempusername)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user_update.xml)
    ampacheConnection.user_update(tempusername, False, False, False, False, False, False, True, False)
    ampacheConnection.user(tempusername)
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (disabled)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user_delete.xml)
    ampacheConnection.user_delete(tempusername)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user%20\(error\).xml)
    ampacheConnection.user('missing_user')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user.xml)
    myuser = ampacheConnection.user('demo')
    if api_format == 'xml':
        for child in myuser:
            if child.tag == 'user':
                myuser = child.attrib['id']
    else:
        user_id = myuser['user']['id']

    single_song = 54
    single_album = 12
    single_video = 1
    single_playlist = 2
    single_artist = 19

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(song\).xml)
    songs = ampacheConnection.get_indexes('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(song with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(song with include\).xml)
    ampacheConnection.get_indexes('song', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(album\).xml)
    albums = ampacheConnection.get_indexes('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(album with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(album with include\).xml)
    ampacheConnection.get_indexes('album', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(artist\).xml)
    artists = ampacheConnection.get_indexes('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(artist with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(artist with include\).xml)
    ampacheConnection.get_indexes('artist', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(playlist\).xml)
    playlists = ampacheConnection.get_indexes('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(playlist with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(playlist with include\).xml)
    ampacheConnection.get_indexes('playlist', False, False, False, False, True, offset, 1)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(podcast_episode\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(podcast_episode\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast_episode)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(podcast\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(podcast\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(podcast with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(podcast with include\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/videos.xml)
    videos = ampacheConnection.videos(False, False, 0, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/video.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/video.xml)
    ampacheConnection.video(single_video)

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/advanced_search%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/advanced_search%20\(song\).xml)
    search_song = ampacheConnection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    if api_format == 'xml':
        song_id = search_song[1].attrib['id']
    else:
        song_id = search_song[0]['id']
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/advanced_search%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/advanced_search%20\(album\).xml)
    search_album = ampacheConnection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    if api_format == 'xml':
        for child in search_album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album[0]['name']

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/advanced_search%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/advanced_search%20\(artist\).xml)]]
    search_artist = ampacheConnection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    if api_format == 'xml':
        for child in search_artist:
            if child.tag == 'artist':
                artist_title = child.find('name').text
    else:
        artist_title = search_artist[0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/album.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/album.xml)
    ampacheConnection.album(2, True)
    if os.path.isfile(docpath + "album." + api_format):
        shutil.move(docpath + "album." + api_format,
                    docpath + "album (with include)." + api_format)

    album = ampacheConnection.album(2, False)

    if api_format == 'xml':
        for child in album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album[0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/album_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/album_songs.xml)
    ampacheConnection.album_songs(single_album, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/albums.xml)
    ampacheConnection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    albums = ampacheConnection.albums(album_title, 1, False, False, 0, 10, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/stats%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/stats%20\(song\).xml)
    ampacheConnection.stats('song', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/stats%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/stats%20\(artist\).xml)
    stats = ampacheConnection.stats('artist', 'random', ampache_user, False, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (artist)." + api_format)

    single_artist = 19

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/stats%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/stats%20\(album\).xml)
    stats = ampacheConnection.stats('album', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    if api_format == 'xml':
        for child in stats:
            if child.tag == 'album':
                single_album = child.attrib['id']
                album_title = child.find('name').text
    else:
        album_title = stats[0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist%20\(with include songs,albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist%20\(with include songs,albums\).xml)
    ampacheConnection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist%20\(with include songs\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist%20\(with include songs\).xml)
    ampacheConnection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist%20\(with include albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist%20\(with include albums\).xml)
    ampacheConnection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist.xml)
    artist = ampacheConnection.artist(19, False)


    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist_albums.xml)
    ampacheConnection.artist_albums(single_artist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist_songs.xml)
    ampacheConnection.artist_songs(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artists%20\(with include songs,albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artists%20\(with include songs,albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artists%20\(with include songs\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artists%20\(with include songs\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artists.xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'albums')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artists%20\(with include albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artists%20\(with include albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_action%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_action%20\(error\).xml)
    ampacheConnection.catalog_action('clean', 2)
    if os.path.isfile(docpath + "catalog_action." + api_format):
        shutil.move(docpath + "catalog_action." + api_format,
                    docpath + "catalog_action (error)." + api_format)


    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/flag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/flag.xml)
    ampacheConnection.flag('song', 93, False)
    ampacheConnection.flag('song', 93, True)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/rate.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/rate.xml)
    ampacheConnection.rate('song', 93, 0)
    ampacheConnection.rate('song', 93, 5)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/record_play.xml)
    ampacheConnection.record_play(song_id, 4, 'debug')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/followers.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/followers.xml)
    ampacheConnection.followers(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/following.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/following.xml)
    ampacheConnection.following(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/friends_timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/friends_timeline.xml)
    ampacheConnection.friends_timeline(limit, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/last_shouts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/last_shouts.xml)
    ampacheConnection.last_shouts(ampache_user, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlists.xml)
    ampacheConnection.playlists(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_create.xml)
    playlist_create = ampacheConnection.playlist_create('rename', 'private')

    if api_format == 'xml':
        for child in playlist_create:
            if child.tag == 'playlist':
                tmp_playlist = child.attrib['id']
                single_playlist = tmp_playlist
    else:
        single_playlist = playlist_create[0]['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_edit.xml)
    ampacheConnection.playlist_edit(single_playlist, 'documentation', 'public')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_add_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_add_song.xml)
    ampacheConnection.playlist_add_song(single_playlist, 71, 0)
    ampacheConnection.playlist_add_song(single_playlist, 72, 0)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 0)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 1)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_remove_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_remove_song.xml)
    ampacheConnection.playlist_remove_song(single_playlist, False, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist.xml)
    ampacheConnection.playlist(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_songs.xml)
    ampacheConnection.playlist_songs(single_playlist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_delete.xml)
    ampacheConnection.playlist_delete(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_generate%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(song\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'song', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_generate%20\(index\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(index\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'index', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (index)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_generate%20\(id\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(id\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'id', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (id)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/scrobble%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/scrobble%20\(error\).xml)
    ampacheConnection.scrobble('Hear. Life. Spoken', 'Sub Atari Knives', 'Sub Atari Knives', False, False, False,
                               int(time.time()), 'debug')
    if os.path.isfile(docpath + "scrobble." + api_format):
        shutil.move(docpath + "scrobble." + api_format,
                    docpath + "scrobble (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/scrobble.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/scrobble.xml)
    ampacheConnection.scrobble('Sensorisk Deprivation', 'IOK-1', 'Sensorisk Deprivation', False, False, False,
                               int(time.time()), 'debug')
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/record_play.xml)
    ampacheConnection.record_play(93, ampache_user, 'debug')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/search_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/search_songs.xml)
    ampacheConnection.search_songs(song_title, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/song.xml)
    ampacheConnection.song(single_song)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/songs.xml)
    ampacheConnection.songs(False, False, False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tags.xml)
    genre = ''
    tags = ampacheConnection.tags('D', False, offset, limit)
    if api_format == 'xml':
        for child in tags:
            if child.tag == 'tag':
                genre = child.attrib['id']
    else:
        for tag in tags[0]['tag']:
            tmp_genre = tag['id']
        genre = tmp_genre

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag.xml)
    ampacheConnection.tag(genre)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag_albums.xml)
    ampacheConnection.tag_albums(genre, 0, 2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag_artists.xml)
    ampacheConnection.tag_artists(genre, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag_songs.xml)
    ampacheConnection.tag_songs(genre, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/licenses.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/licenses.xml)
    ampacheConnection.licenses(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/license.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/license.xml)
    ampacheConnection.license(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/license_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/license_songs.xml)
    ampacheConnection.license_songs(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast%20\(with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast%20\(with include\).xml)
    ampacheConnection.podcast(1, 'episodes')
    if os.path.isfile(docpath + "podcast." + api_format):
        shutil.move(docpath + "podcast." + api_format,
                    docpath + "podcast (include episodes)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast.xml)
    ampacheConnection.podcast(1, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_episodes.xml)
    ampacheConnection.podcast_episodes(1, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_episode.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_episode.xml)
    ampacheConnection.podcast_episode(23)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_create.xml)
    ampacheConnection.podcast_create('https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml', 3)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_edit.xml)
    ampacheConnection.podcast_edit(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_delete.xml)
    podcasts = ampacheConnection.podcasts('Trace', 1)
    if api_format == 'xml':
        for child in podcasts:
            if child.tag == 'podcast':
                podcast_id = child.attrib['id']
    else:
        for podcast in podcasts:
            if podcast['name'] == "Trace":
                podcast_id = podcast['id']
    try:
        ampacheConnection.podcast_delete(podcast_id)
    except UnboundLocalError:
        pass

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcasts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcasts.xml)
    ampacheConnection.podcasts(False, False, 0, 4)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_podcast.xml)
    ampacheConnection.update_podcast(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/shares.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/shares.xml)
    shares = ampacheConnection.shares(False, False, offset, limit)
    if api_format == 'xml':
        share_id = shares[1].attrib['id']
    else:
        share_id = shares[0]['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share.xml)
    ampacheConnection.share(share_id)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share_create.xml)
    share_create = ampacheConnection.share_create(single_song, 'song', False, 7)
    if api_format == 'xml':
        share_new = share_create[1].attrib['id']
    else:
        share_new = share_create[0]['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share_edit.xml)
    ampacheConnection.share_edit(share_new, 0, 0, False, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share_delete.xml)
    ampacheConnection.share_delete(share_new)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/timeline.xml)
    ampacheConnection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # unfollow and refollow for timeline stuff
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/toggle_follow.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/toggle_follow.xml)
    ampacheConnection.toggle_follow(toggle)
    ampacheConnection.toggle_follow(toggle)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_from_tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_from_tags.xml)
    ampacheConnection.update_from_tags('album', 10)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_artist_info.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_artist_info.xml)
    ampacheConnection.update_artist_info(20)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_art.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_art.xml)
    ampacheConnection.update_art('album', 21, True)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/localplay%20\(status\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/localplay%20\(status\).xml)
    ampacheConnection.localplay('status', False, False, 0)
    if os.path.isfile(docpath + "localplay." + api_format):
        shutil.move(docpath + "localplay." + api_format,
                    docpath + "localplay (status)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/localplay.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/localplay.xml)
    ampacheConnection.localplay('stop', False, False, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalogs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalogs.xml)
    ampacheConnection.catalogs()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog.xml)
    ampacheConnection.catalog(1)

    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


def ampache5_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
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
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/democratic%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/democratic%20\(playlist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/democratic%20\(play\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/democratic%20\(play\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/democratic%20\(vote\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/democratic%20\(vote\).xml)
    #ampacheConnection.democratic()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/goodbye.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/goodbye.xml)
    #ampacheConnection.goodbye()
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/catalog_action%20\(add_to_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/catalog_action%20\(add_to_catalog\).xml)
    #ampacheConnection.catalog_action('clean_catalog', 2)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/catalog_action%20\(clean_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/catalog_action%20\(clean_catalog\).xml)
    #ampacheConnection.catalog_action('clean_catalog', 2)
    # BINARY METHOD
    #ampacheConnection.get_art(93, 'song', (os.path.join(os.getcwd(), 'get_art.jpg')))

    # send a bad ping
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/ping.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/ping.xml)
    ampacheConnection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/handshake%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/handshake.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/system_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/system_update.xml)
    ampacheConnection.system_update()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/live_streams.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/live_streams.xml)
    ampacheConnection.live_streams(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/live_stream.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/live_stream.xml)
    ampacheConnection.live_stream(3)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/labels.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/labels.xml)
    ampacheConnection.labels(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/label.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/label.xml)
    ampacheConnection.label(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/label_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/label_artists.xml)
    ampacheConnection.label_artists(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/url_to_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/url_to_song.xml)
    ampacheConnection.url_to_song(song_url)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/users.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/users.xml)
    ampacheConnection.users()

    tempusername = 'temp_user'
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user_create.xml)
    ampacheConnection.user_create(tempusername, 'supoersecretpassword', 'email@gmail.com', False, False)
    ampacheConnection.user(tempusername)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user_update.xml)
    ampacheConnection.user_update(tempusername, False, False, False, False, False, False, True, False)
    ampacheConnection.user(tempusername)
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (disabled)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user_delete.xml)
    ampacheConnection.user_delete(tempusername)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user%20\(error\).xml)
    ampacheConnection.user('missing_user')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/user.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/user.xml)
    myuser = ampacheConnection.user(ampache_user)
    if api_format == 'xml':
        for child in myuser:
            if child.tag == 'user':
                myuser = child.attrib['id']
    else:
        user_id = myuser['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(song\).xml)
    songs = ampacheConnection.get_indexes('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song)." + api_format)
    single_song = ampacheConnection.get_id_list(songs, 'song')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(song with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(song with include\).xml)
    ampacheConnection.get_indexes('song', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(album\).xml)
    albums = ampacheConnection.get_indexes('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album)." + api_format)
    single_album = ampacheConnection.get_id_list(albums, 'album')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(album with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(album with include\).xml)
    ampacheConnection.get_indexes('album', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album with include)." + api_format)
    single_album = ampacheConnection.get_id_list(albums, 'album')[0]
    single_album = 12

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(artist\).xml)
    artists = ampacheConnection.get_indexes('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist)." + api_format)
    single_artist = ampacheConnection.get_id_list(artists, 'artist')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(artist with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(artist with include\).xml)
    ampacheConnection.get_indexes('artist', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist with include)." + api_format)
    single_artist = ampacheConnection.get_id_list(artists, 'artist')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(playlist\).xml)
    playlists = ampacheConnection.get_indexes('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist)." + api_format)
    single_playlist = ampacheConnection.get_id_list(playlists, 'playlist')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(playlist with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(playlist with include\).xml)
    ampacheConnection.get_indexes('playlist', False, False, False, False, True, offset, 1)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(podcast_episode\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(podcast_episode\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast_episode)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(podcast\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(podcast\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/get_indexes%20\(podcast with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/get_indexes%20\(podcast with include\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/videos.xml)
    videos = ampacheConnection.videos(False, False, 0, 0)
    single_video = 1

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/video.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/video.xml)
    ampacheConnection.video(single_video)

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/advanced_search%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/advanced_search%20\(song\).xml)]]
    search_song = ampacheConnection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    if api_format == 'xml':
        song_id = search_song[1].attrib['id']
    else:
        song_id = search_song['song'][0]['id']
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/advanced_search%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/advanced_search%20\(album\).xml)]]
    search_album = ampacheConnection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    if api_format == 'xml':
        for child in search_album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album['album'][0]['name']

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/advanced_search%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/advanced_search%20\(artist\).xml)]]
    search_artist = ampacheConnection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    if api_format == 'xml':
        for child in search_artist:
            if child.tag == 'artist':
                artist_title = child.find('name').text
    else:
        artist_title = search_artist['artist'][0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/album%20\(with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/album%20\(with include\).xml)
    ampacheConnection.album(2, True)
    if os.path.isfile(docpath + "album." + api_format):
        shutil.move(docpath + "album." + api_format,
                    docpath + "album (with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/album.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/album.xml)
    album = ampacheConnection.album(2, False)

    if api_format == 'xml':
        for child in album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album['album'][0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artist_songs.xml)
    ampacheConnection.album_songs(single_album, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/albums%20\(with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/albums%20\(with include\).xml)
    ampacheConnection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/albums.xml)
    albums = ampacheConnection.albums(album_title, 1, False, False, 0, 10, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/stats%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/stats%20\(song\).xml)
    ampacheConnection.stats('song', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/stats%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/stats%20\(artist\).xml)
    stats = ampacheConnection.stats('artist', 'random', ampache_user, False, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (artist)." + api_format)

    single_artist = 19

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/stats%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/stats%20\(album\).xml)
    stats = ampacheConnection.stats('album', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    if api_format == 'xml':
        for child in stats:
            if child.tag == 'album':
                single_album = child.attrib['id']
                album_title = child.find('name').text
    else:
        album_title = stats['album'][0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artist%20\(with include songs,albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artist%20\(with include songs,albums\).xml)
    ampacheConnection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artist%20\(with include songs\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artist%20\(with include songs\).xml)
    ampacheConnection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artist%20\(with include albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artist%20\(with include albums\).xml)
    ampacheConnection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artist.xml)
    ampacheConnection.artist(16, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artist_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artist_albums.xml)
    ampacheConnection.artist_albums(single_artist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/album_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/album_songs.xml)
    ampacheConnection.artist_songs(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artists%20\(with include songs,albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artists%20\(with include songs,albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artists%20\(with include songs\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artists%20\(with include songs\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artists%20\(with include albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artists%20\(with include albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'albums')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/artists.xml)
    ampacheConnection.artists(False, False, False, offset, limit, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/catalog_action%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/catalog_action%20\(error\).xml)
    ampacheConnection.catalog_action('clean', 2)
    if os.path.isfile(docpath + "catalog_action." + api_format):
        shutil.move(docpath + "catalog_action." + api_format,
                    docpath + "catalog_action (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/flag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/flag.xml)
    ampacheConnection.flag('playlist', 2, True)
    ampacheConnection.flag('song', 93, False)
    ampacheConnection.flag('song', 93, True)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/rate.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/rate.xml)
    ampacheConnection.rate('playlist', 2, 2)
    ampacheConnection.rate('song', 93, 0)
    ampacheConnection.rate('song', 93, 5)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/record_play.xml)
    ampacheConnection.record_play(song_id, 4, 'debug')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/followers.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/followers.xml)
    ampacheConnection.followers(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/following.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/following.xml)
    ampacheConnection.following(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/friends_timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/friends_timeline.xml)
    ampacheConnection.friends_timeline(limit, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/last_shouts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/last_shouts.xml)
    ampacheConnection.last_shouts(ampache_user, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlists.xml)
    ampacheConnection.playlists(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_create.xml)
    playlist_create = ampacheConnection.playlist_create('rename', 'private')

    if api_format == 'xml':
        for child in playlist_create:
            if child.tag == 'playlist':
                tmp_playlist = child.attrib['id']
                single_playlist = tmp_playlist
    else:
        single_playlist = playlist_create['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_edit.xml)
    ampacheConnection.playlist_edit(single_playlist, 'documentation', 'public')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_add_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_add_song.xml)
    ampacheConnection.playlist_add_song(single_playlist, 71, 0)
    ampacheConnection.playlist_add_song(single_playlist, 72, 0)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 0)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 1)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_remove_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_remove_song.xml)
    ampacheConnection.playlist_remove_song(single_playlist, False, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist.xml)
    ampacheConnection.playlist(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_songs.xml)
    ampacheConnection.playlist_songs(single_playlist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_delete.xml)
    ampacheConnection.playlist_delete(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_generate%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(song\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'song', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_generate%20\(index\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_generate%20\(index\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'index', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (index)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/playlist_generate%20\(id\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/playlist_generate%20\(id\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'id', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (id)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/scrobble%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/scrobble%20\(song\).xml)
    ampacheConnection.scrobble('Hear. Life. Spoken', 'Sub Atari Knives', 'Sub Atari Knives', False, False, False,
                               int(time.time()), 'debug')
    if os.path.isfile(docpath + "scrobble." + api_format):
        shutil.move(docpath + "scrobble." + api_format,
                    docpath + "scrobble (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/scrobble.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/scrobble.xml)
    ampacheConnection.scrobble('Sensorisk Deprivation', 'IOK-1', 'Sensorisk Deprivation', False, False, False,
                               int(time.time()), 'debug')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/record_play.xml)
    ampacheConnection.record_play(93, ampache_user, 'debug')


    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/search_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/search_songs.xml)
    ampacheConnection.search_songs(song_title, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/song.xml)
    ampacheConnection.song(single_song)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/songs.xml)
    ampacheConnection.songs(False, False, False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/genres.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/genres.xml)
    genre = ''
    tags = ampacheConnection.genres('D', False, offset, limit)
    if api_format == 'xml':
        for child in tags:
            if child.tag == 'genre':
                genre = child.attrib['id']
    else:
        for tag in tags['genre']:
            tmp_genre = tag['id']
        genre = tmp_genre

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/genre.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/genre.xml)
    ampacheConnection.genre(genre)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/genre_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/genre_albums.xml)
    ampacheConnection.genre_albums(genre, 0, 2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/genre_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/genre_artists.xml)
    ampacheConnection.genre_artists(genre, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/genre_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/genre_songs.xml)
    ampacheConnection.genre_songs(genre, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/licenses.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/licenses.xml)
    ampacheConnection.licenses(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/license.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/license.xml)
    ampacheConnection.license(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/license_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/license_songs.xml)
    ampacheConnection.license_songs(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/labels.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/labels.xml)
    ampacheConnection.labels(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/label.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/label.xml)
    ampacheConnection.label(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/label_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/label_artists.xml)
    ampacheConnection.label_artists(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast%20\(include episodes\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast%20\(include episodes\).xml)
    ampacheConnection.podcast(1, 'episodes')
    if os.path.isfile(docpath + "podcast." + api_format):
        shutil.move(docpath + "podcast." + api_format,
                    docpath + "podcast (include episodes)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast.xml)
    ampacheConnection.podcast(1, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast_episodes.xml)
    ampacheConnection.podcast_episodes(1, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast_episode.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast_episode.xml)
    ampacheConnection.podcast_episode(23)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast_create.xml)
    ampacheConnection.podcast_create('https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml', 3)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast_edit.xml)
    ampacheConnection.podcast_edit(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcast_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcast_delete.xml)
    podcasts = ampacheConnection.podcasts('Trace', 1)
    podcast_id = ampacheConnection.get_id_list(podcasts, 'podcast')[0]
    ampacheConnection.podcast_delete(3)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/podcasts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/podcasts.xml)
    ampacheConnection.podcasts(False, False, 0, 4)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/update_podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/update_podcast.xml)
    ampacheConnection.update_podcast(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/shares.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/shares.xml)
    shares = ampacheConnection.shares(False, False, offset, limit)
    share_id = ampacheConnection.get_id_list(shares, 'share')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/share.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/share.xml)
    ampacheConnection.share(share_id)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/share_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/share_create.xml)
    share_create = ampacheConnection.share_create(single_song, 'song', False, 7)
    if api_format == 'xml':
        share_new = share_create[1].attrib['id']
    else:
        share_new = share_create['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/share_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/share_edit.xml)
    ampacheConnection.share_edit(share_new, 0, 0, False, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/share_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/share_delete.xml)
    ampacheConnection.share_delete(share_new)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/timeline.xml)
    ampacheConnection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # unfollow and refollow for timeline stuff
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/toggle_follow.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/toggle_follow.xml)
    ampacheConnection.toggle_follow(toggle)
    ampacheConnection.toggle_follow(toggle)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/update_from_tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/update_from_tags.xml)
    ampacheConnection.update_from_tags('album', 10)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/update_artist_info.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/update_artist_info.xml)
    ampacheConnection.update_artist_info(26)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/update_art.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/update_art.xml)
    ampacheConnection.update_art('album', 21, True)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/localplay%20\(status\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/localplay%20\(status\).xml)
    ampacheConnection.localplay('status', False, False, 0)
    if os.path.isfile(docpath + "localplay." + api_format):
        shutil.move(docpath + "localplay." + api_format,
                    docpath + "localplay (status)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/localplay.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/localplay.xml)
    ampacheConnection.localplay('stop', False, False, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/catalogs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/catalogs.xml)
    ampacheConnection.catalogs()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/catalog.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/catalog.xml)
    ampacheConnection.catalog(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/deleted_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/deleted_songs.xml)
    ampacheConnection.deleted_songs()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/deleted_podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/deleted_podcast_episodes.xml)
    ampacheConnection.deleted_podcast_episodes()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/json-responses/deleted_videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api5/docs/xml-responses/deleted_videos.xml)
    ampacheConnection.deleted_videos()

    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


def ampache6_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    #TODO
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/bookmark_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/bookmark_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/bookmark_delete)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/bookmark_delete)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/bookmark_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/bookmark_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/bookmarks.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/bookmarks.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_bookmark.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_bookmark.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_similar.xml)
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
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/democratic%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/democratic%20\(playlist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/democratic%20\(play\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/democratic%20\(play\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/democratic%20\(vote\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/democratic%20\(vote\).xml)
    #ampacheConnection.democratic()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/goodbye.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/goodbye.xml)
    #ampacheConnection.goodbye()
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog_action%20\(add_to_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog_action%20\(add_to_catalog\).xml)
    #ampacheConnection.catalog_action('clean_catalog', 2)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog_action%20\(clean_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog_action%20\(clean_catalog\).xml)
    #ampacheConnection.catalog_action('clean_catalog', 2)
    # BINARY METHOD
    #ampacheConnection.get_art(93, 'song', (os.path.join(os.getcwd(), 'get_art.jpg')))


    # send a bad ping
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/ping.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/ping.xml)
    ampacheConnection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + "ping." + api_format):
        shutil.move(docpath + "ping." + api_format,
                    docpath + "ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/handshake%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', '', 0, api_version)
    if os.path.isfile(docpath + "handshake." + api_format):
        shutil.move(docpath + "handshake." + api_format,
                    docpath + "handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/handshake.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, '', 0, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)

    # Registration should be disabled
    ampacheConnection.register('user', 'no', 'passwonord', 'no')
    if os.path.isfile(docpath + "register." + api_format):
        shutil.move(docpath + "register." + api_format,
                    docpath + "register (error)." + api_format)

    ampacheConnection.register('username' + api_format, 'fullname', 'password', 'test' + api_format + '@email.com')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/system_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/system_update.xml)
    ampacheConnection.system_update()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/live_stream.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/live_stream.xml)
    ampacheConnection.live_stream(3)

    stream_name = 'HBR1.com - Tronic Lounge'
    stream_website = 'http://www.hbr1.com/'
    stream_url = 'http://ubuntu.hbr1.com:19800/tronic.ogg'
    stream_codec = 'ogg'
    catalog_id = 1

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/live_stream_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/live_stream_create.xml)
    ampacheConnection.live_stream_create(stream_name, stream_url, stream_codec, catalog_id, stream_website)

    single_live_stream = ampacheConnection.live_streams(stream_name)
    if api_format == 'xml':
        live_stream_new = single_live_stream[1].attrib['id']
    else:
        live_stream_new = single_live_stream["live_stream"][0]['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/live_stream_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/live_stream_edit.xml)
    ampacheConnection.live_stream_edit(live_stream_new, False, False, False, False, "http://ampache.org")

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/live_stream_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/live_stream_delete.xml)
    ampacheConnection.live_stream_delete(live_stream_new)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/live_streams.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/live_streams.xml)
    ampacheConnection.live_streams(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/labels.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/labels.xml)
    ampacheConnection.labels(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/label.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/label.xml)
    ampacheConnection.label(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/label_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/label_artists.xml)
    ampacheConnection.label_artists(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/url_to_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/url_to_song.xml)
    ampacheConnection.url_to_song(song_url)


    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/browse.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/browse.xml)

    ampacheConnection.browse()
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (root)." + api_format)

    ampacheConnection.browse(2, 'podcast', 3)
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (podcast)." + api_format)

    ampacheConnection.browse(19, 'artist', 1)
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (artist)." + api_format)

    ampacheConnection.browse(12, 'album', 1)
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (album)." + api_format)

    ampacheConnection.browse(1, 'catalog')
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (music catalog)." + api_format)

    ampacheConnection.browse(2, 'catalog')
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (video catalog)." + api_format)

    ampacheConnection.browse(3, 'catalog')
    if os.path.isfile(docpath + "browse." + api_format):
        shutil.move(docpath + "browse." + api_format,
                    docpath + "browse (podcast catalog)." + api_format)

    ampacheConnection.browse()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/users.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/users.xml)
    ampacheConnection.users()

    tempusername = 'temp_user'
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user_create.xml)
    ampacheConnection.user_create(tempusername, 'supoersecretpassword', 'email@gmail.com', False, False)
    ampacheConnection.user(tempusername)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user_edit.xml)
    ampacheConnection.user_edit(tempusername, False, False, False, False, False, False, True, False)
    ampacheConnection.user(tempusername)
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (disabled)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user_delete.xml)
    ampacheConnection.user_delete(tempusername)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user%20\(error\).xml)
    ampacheConnection.user('missing_user')
    if os.path.isfile(docpath + "user." + api_format):
        shutil.move(docpath + "user." + api_format,
                    docpath + "user (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/user.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/user.xml)
    myuser = ampacheConnection.user(ampache_user)
    if api_format == 'xml':
        for child in myuser:
            if child.tag == 'user':
                myuser = child.attrib['id']
    else:
        user_id = myuser['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/list.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/list.xml)
    ampacheConnection.list('song', False, False, False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(song\).xml)
    songs = ampacheConnection.get_indexes('song', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song)." + api_format)
    single_song = ampacheConnection.get_id_list(songs, 'song')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(song with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(song with include\).xml)
    ampacheConnection.get_indexes('song', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (song with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(album\).xml)
    albums = ampacheConnection.get_indexes('album', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album)." + api_format)
    single_album = ampacheConnection.get_id_list(albums, 'album')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(album with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(album with include\).xml)
    ampacheConnection.get_indexes('album', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (album with include)." + api_format)
    single_album = ampacheConnection.get_id_list(albums, 'album')[0]
    single_album = 12

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(artist\).xml)
    artists = ampacheConnection.get_indexes('artist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist)." + api_format)
    single_artist = ampacheConnection.get_id_list(artists, 'artist')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(artist with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(artist with include\).xml)
    ampacheConnection.get_indexes('artist', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (artist with include)." + api_format)
    single_artist = ampacheConnection.get_id_list(artists, 'artist')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(playlist\).xml)
    playlists = ampacheConnection.get_indexes('playlist', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist)." + api_format)
    single_playlist = ampacheConnection.get_id_list(playlists, 'playlist')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(playlist with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(playlist with include\).xml)
    ampacheConnection.get_indexes('playlist', False, False, False, False, True, offset, 1)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (playlist with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(podcast_episode\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(podcast_episode\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast_episode)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(podcast\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(podcast\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, False, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/get_indexes%20\(podcast with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/get_indexes%20\(podcast with include\).xml)
    ampacheConnection.get_indexes('podcast', False, False, False, False, True, offset, limit)
    if os.path.isfile(docpath + "get_indexes." + api_format):
        shutil.move(docpath + "get_indexes." + api_format,
                    docpath + "get_indexes (podcast with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/videos.xml)
    videos = ampacheConnection.videos(False, False, 0, 0)
    single_video = 1

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/video.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/video.xml)
    ampacheConnection.video(single_video)

    search_rules = [['favorite', 0, '%'], ['title', 2, 'D']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/advanced_search%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/advanced_search%20\(song\).xml)]]
    search_song = ampacheConnection.advanced_search(search_rules, 'or', 'song', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (song)." + api_format)

    if api_format == 'xml':
        song_id = search_song[1].attrib['id']
    else:
        song_id = search_song['song'][0]['id']
    song_title = "Dance with the Devil"

    search_rules = [['artist', 0, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/advanced_search%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/advanced_search%20\(album\).xml)]]
    search_album = ampacheConnection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (album)." + api_format)

    if api_format == 'xml':
        for child in search_album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album['album'][0]['name']

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/advanced_search%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/advanced_search%20\(artist\).xml)]]
    search_artist = ampacheConnection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile(docpath + "advanced_search." + api_format):
        shutil.move(docpath + "advanced_search." + api_format,
                    docpath + "advanced_search (artist)." + api_format)

    if api_format == 'xml':
        for child in search_artist:
            if child.tag == 'artist':
                artist_title = child.find('name').text
    else:
        artist_title = search_artist['artist'][0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/album%20\(with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/album%20\(with include\).xml)
    ampacheConnection.album(2, True)
    if os.path.isfile(docpath + "album." + api_format):
        shutil.move(docpath + "album." + api_format,
                    docpath + "album (with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/album.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/album.xml)
    album = ampacheConnection.album(2, False)

    if api_format == 'xml':
        for child in album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album['album'][0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artist_songs.xml)
    ampacheConnection.album_songs(single_album, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/albums%20\(with include\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/albums%20\(with include\).xml)
    ampacheConnection.albums(album_title, 1, False, False, 0, 2, True)
    if os.path.isfile(docpath + "albums." + api_format):
        shutil.move(docpath + "albums." + api_format,
                    docpath + "albums (with include)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/albums.xml)
    albums = ampacheConnection.albums(album_title, 1, False, False, 0, 10, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/stats%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/stats%20\(song\).xml)
    ampacheConnection.stats('song', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/stats%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/stats%20\(artist\).xml)
    stats = ampacheConnection.stats('artist', 'random', ampache_user, False, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (artist)." + api_format)

    single_artist = 19

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/stats%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/stats%20\(album\).xml)
    stats = ampacheConnection.stats('album', 'random', ampache_user, None, 0, 2)
    if os.path.isfile(docpath + "stats." + api_format):
        shutil.move(docpath + "stats." + api_format,
                    docpath + "stats (album)." + api_format)

    if api_format == 'xml':
        for child in stats:
            if child.tag == 'album':
                single_album = child.attrib['id']
                album_title = child.find('name').text
    else:
        album_title = stats['album'][0]['name']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artist%20\(with include songs,albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artist%20\(with include songs,albums\).xml)
    ampacheConnection.artist(16, True)
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artist%20\(with include songs\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artist%20\(with include songs\).xml)
    ampacheConnection.artist(16, 'songs')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include songs)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artist%20\(with include albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artist%20\(with include albums\).xml)
    ampacheConnection.artist(16, 'albums')
    if os.path.isfile(docpath + "artist." + api_format):
        shutil.move(docpath + "artist." + api_format,
                    docpath + "artist (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artist.xml)
    ampacheConnection.artist(16, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artist_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artist_albums.xml)
    ampacheConnection.artist_albums(single_artist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/album_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/album_songs.xml)
    ampacheConnection.artist_songs(2, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artists%20\(with include songs,albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artists%20\(with include songs,albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, True)
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs,albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artists%20\(with include songs\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artists%20\(with include songs\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'songs')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include songs)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artists%20\(with include albums\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artists%20\(with include albums\).xml)
    ampacheConnection.artists(False, False, False, offset, limit, 'albums')
    if os.path.isfile(docpath + "artists." + api_format):
        shutil.move(docpath + "artists." + api_format,
                    docpath + "artists (with include albums)." + api_format)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/artists.xml)
    ampacheConnection.artists(False, False, False, offset, limit, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog_action%20\(error\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog_action%20\(error\).xml)
    ampacheConnection.catalog_action('clean', 2)
    if os.path.isfile(docpath + "catalog_action." + api_format):
        shutil.move(docpath + "catalog_action." + api_format,
                    docpath + "catalog_action (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/flag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/flag.xml)
    ampacheConnection.flag('playlist', 2, True)
    ampacheConnection.flag('song', 93, False)
    ampacheConnection.flag('song', 93, True)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/rate.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/rate.xml)
    ampacheConnection.rate('playlist', 2, 2)
    ampacheConnection.rate('song', 93, 0)
    ampacheConnection.rate('song', 93, 5)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/record_play.xml)
    ampacheConnection.record_play(song_id, 4, 'debug')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/followers.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/followers.xml)
    ampacheConnection.followers(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/following.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/following.xml)
    ampacheConnection.following(ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/friends_timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/friends_timeline.xml)
    ampacheConnection.friends_timeline(limit, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/last_shouts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/last_shouts.xml)
    ampacheConnection.last_shouts(ampache_user, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlists.xml)
    ampacheConnection.playlists(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_create.xml)
    playlist_create = ampacheConnection.playlist_create('rename', 'private')

    if api_format == 'xml':
        for child in playlist_create:
            if child.tag == 'playlist':
                tmp_playlist = child.attrib['id']
                single_playlist = tmp_playlist
    else:
        single_playlist = playlist_create['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_edit.xml)
    ampacheConnection.playlist_edit(single_playlist, 'documentation', 'public')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_add_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_add_song.xml)
    ampacheConnection.playlist_add_song(single_playlist, 71, 0)
    ampacheConnection.playlist_add_song(single_playlist, 72, 0)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 0)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 1)
    if os.path.isfile(docpath + "playlist_add_song." + api_format):
        shutil.move(docpath + "playlist_add_song." + api_format,
                    docpath + "playlist_add_song (error)." + api_format)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 1)
    ampacheConnection.playlist_add_song(single_playlist, single_song, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_remove_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_remove_song.xml)
    ampacheConnection.playlist_remove_song(single_playlist, False, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist.xml)
    ampacheConnection.playlist(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_songs.xml)
    ampacheConnection.playlist_songs(single_playlist, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_delete.xml)
    ampacheConnection.playlist_delete(single_playlist)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_generate%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_generate%20\(song\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'song', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (song)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_generate%20\(index\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_generate%20\(index\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'index', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (index)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/playlist_generate%20\(id\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/playlist_generate%20\(id\).xml)
    ampacheConnection.playlist_generate('random', False, False, False, False, 'id', offset, limit)
    if os.path.isfile(docpath + "playlist_generate." + api_format):
        shutil.move(docpath + "playlist_generate." + api_format,
                    docpath + "playlist_generate (id)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/scrobble%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/scrobble%20\(song\).xml)
    ampacheConnection.scrobble('Hear. Life. Spoken', 'Sub Atari Knives', 'Sub Atari Knives', False, False, False,
                               int(time.time()), 'debug')
    if os.path.isfile(docpath + "scrobble." + api_format):
        shutil.move(docpath + "scrobble." + api_format,
                    docpath + "scrobble (error)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/scrobble.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/scrobble.xml)
    ampacheConnection.scrobble('Sensorisk Deprivation', 'IOK-1', 'Sensorisk Deprivation', False, False, False,
                               int(time.time()), 'debug')

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/record_play.xml)
    ampacheConnection.record_play(93, ampache_user, 'debug')


    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/search_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/search_songs.xml)
    ampacheConnection.search_songs(song_title, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/song.xml)
    ampacheConnection.song(single_song)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/songs.xml)
    ampacheConnection.songs(False, False, False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/genres.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/genres.xml)
    genre = ''
    tags = ampacheConnection.genres('D', False, offset, limit)
    if api_format == 'xml':
        for child in tags:
            if child.tag == 'genre':
                genre = child.attrib['id']
    else:
        for tag in tags['genre']:
            tmp_genre = tag['id']
        genre = tmp_genre

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/genre.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/genre.xml)
    ampacheConnection.genre(genre)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/genre_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/genre_albums.xml)
    ampacheConnection.genre_albums(genre, 0, 2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/genre_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/genre_artists.xml)
    ampacheConnection.genre_artists(genre, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/genre_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/genre_songs.xml)
    ampacheConnection.genre_songs(genre, 0, 1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/licenses.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/licenses.xml)
    ampacheConnection.licenses(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/license.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/license.xml)
    ampacheConnection.license(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/license_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/license_songs.xml)
    ampacheConnection.license_songs(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/labels.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/labels.xml)
    ampacheConnection.labels(False, False, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/label.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/label.xml)
    ampacheConnection.label(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/label_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/label_artists.xml)
    ampacheConnection.label_artists(2)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast%20\(include episodes\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast%20\(include episodes\).xml)
    ampacheConnection.podcast(1, 'episodes')
    if os.path.isfile(docpath + "podcast." + api_format):
        shutil.move(docpath + "podcast." + api_format,
                    docpath + "podcast (include episodes)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast.xml)
    ampacheConnection.podcast(1, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast_episodes.xml)
    ampacheConnection.podcast_episodes(1, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast_episode.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast_episode.xml)
    ampacheConnection.podcast_episode(23)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast_create.xml)
    ampacheConnection.podcast_create('https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml', 3)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast_edit.xml)
    ampacheConnection.podcast_edit(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcast_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcast_delete.xml)
    podcasts = ampacheConnection.podcasts('Trace', 1)
    podcast_id = ampacheConnection.get_id_list(podcasts, 'podcast')[0]
    ampacheConnection.podcast_delete(3)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/podcasts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/podcasts.xml)
    ampacheConnection.podcasts(False, False, 0, 4)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/update_podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/update_podcast.xml)
    ampacheConnection.update_podcast(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/shares.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/shares.xml)
    shares = ampacheConnection.shares(False, False, offset, limit)
    share_id = ampacheConnection.get_id_list(shares, 'share')[0]

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/share.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/share.xml)
    ampacheConnection.share(share_id)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/share_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/share_create.xml)
    share_create = ampacheConnection.share_create(single_song, 'song', False, 7)
    if api_format == 'xml':
        share_new = share_create[1].attrib['id']
    else:
        share_new = share_create['id']

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/share_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/share_edit.xml)
    ampacheConnection.share_edit(share_new, 0, 0, False, False)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/share_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/share_delete.xml)
    ampacheConnection.share_delete(share_new)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/timeline.xml)
    ampacheConnection.timeline(ampache_user, 10, 0)

    toggle = 'generic'
    if ampache_user == 'generic':
        toggle = 'user'
    # unfollow and refollow for timeline stuff
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/toggle_follow.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/toggle_follow.xml)
    ampacheConnection.toggle_follow(toggle)
    ampacheConnection.toggle_follow(toggle)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/update_from_tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/update_from_tags.xml)
    ampacheConnection.update_from_tags('album', 10)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/update_artist_info.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/update_artist_info.xml)
    ampacheConnection.update_artist_info(26)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/update_art.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/update_art.xml)
    ampacheConnection.update_art('album', 21, True)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/localplay%20\(status\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/localplay%20\(status\).xml)
    ampacheConnection.localplay('status', False, False, 0)
    if os.path.isfile(docpath + "localplay." + api_format):
        shutil.move(docpath + "localplay." + api_format,
                    docpath + "localplay (status)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/localplay.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/localplay.xml)
    ampacheConnection.localplay('stop', False, False, 0)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalogs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalogs.xml)
    ampacheConnection.catalogs()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/catalog.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/catalog.xml)
    ampacheConnection.catalog(1)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/deleted_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/deleted_songs.xml)
    ampacheConnection.deleted_songs()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/deleted_podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/deleted_podcast_episodes.xml)
    ampacheConnection.deleted_podcast_episodes()

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/json-responses/deleted_videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api6/docs/xml-responses/deleted_videos.xml)
    ampacheConnection.deleted_videos()

    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


def subsonic_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    # Base subsonic url data
    base_url = ampache_url + "/rest/"
    base_parameters = ".view?u=" + ampache_user + "&p=" + ampache_api + "&v=1.16.1&c=Ampache&f=" + api_format

    # Returns an empty <subsonic-response> element on success.
    action = "ping"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getLicense"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)
    fetch_url = base_url + action + base_parameters
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getMusicFolders"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getIndexes"
    # musicFolderId (optional)
    # ifModifiedSince (optional)
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getMusicDirectory"
    # id
    params = '&id=1'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getGenres"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)


    action = "getArtists"
    # musicFolderId (optional)
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getArtist"
    # id
    params = '&id=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getAlbum"
    # id
    params = '&id=200000021'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getSong"
    # id
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getVideos"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getVideoInfo"
    # id
    params = '&id=500000001'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getArtistInfo"
    # id
    # count
    # includeNotPresent
    params = '&id=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getArtistInfo2"
    # id
    # count
    # includeNotPresent
    params = '&id=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getAlbumInfo"
    # id
    params = '&id=200000021'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getAlbumInfo2"
    # id
    params = '&id=200000021'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getSimilarSongs"
    # id
    # count
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getSimilarSongs2"
    # id
    # count
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getTopSongs"
    # artist
    # count
    params = '&artist=100000002'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getRandomSongs"
    # size
    # genre
    # fromYear
    # toYear
    # musicFolderId
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getSongsByGenre"
    # genre
    # count
    # offset
    # musicFolderId
    params = '&genre=Electronic'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getNowPlaying"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getStarred"
    # musicFolderId
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getStarred2"
    # musicFolderId
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getPlaylists"
    # username
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getPlaylist"
    # id
    params = '&id=1770'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "createPlaylist"
    # playlistId
    # name
    # songId
    params = '&name=testcreate&songId=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updatePlaylist"
    # playlistId
    # name
    # comment
    # public
    # songIdToAdd
    params = '&playlistId=4'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deletePlaylist"
    # id
    params = '&id=291770'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    # ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns binary data on success, or an XML document on error (in which case the HTTP content type will start with "text/xml").
    # action = "download"
    # #id
    # params = ''
    # fetch_url = base_url + action + base_parameters + params
    # ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "hls"
    # id
    # bitRate
    # audioTrack
    params = '&id=82'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns the raw video captions.
    # action = "getCaptions"
    # #id
    # #format
    # params = '&id=460'
    # fetch_url = base_url + action + base_parameters + params
    # ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns the cover art image in binary form.
    # action = "getCoverArt"
    # #id
    # #size
    # params = ''
    # fetch_url = base_url + action + base_parameters + params
    # ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getLyrics"
    # artist
    # title
    params = '&artist=METISSE&title=What%20to%20do'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns the avatar image in binary form.
    # action = "getAvatar"
    # #username
    # params = '&username=guest'
    # fetch_url = base_url + action + base_parameters + params
    # ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "star"
    # id
    # albumId
    # artistId
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "unstar"
    # id
    # albumId
    # artistId
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "setRating"
    # id
    # rating
    params = '&id=300000060&rating=5'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "scrobble"
    # id
    # time
    # submission
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getShares"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "createShare"
    # id
    # description
    # expires
    params = '&id=300000078'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updateShare"
    # id
    # description
    # expires
    params = '&id=300000075'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteShare"
    # id
    params = '&id=29770'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getPodcasts"
    # includeEpisodes
    # id
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getNewestPodcasts"
    # count
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getPodcasts"
    # includeEpisodes
    # id
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "refreshPodcasts"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "createPodcastChannel"
    # url
    params = '&url=https://www.abc.net.au/radio/programs/trace/feed/8597522/podcast.xml'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deletePodcastChannel"
    # id
    params = '&id=600000006'
    if (api_format == 'xml'):
        params = '&id=600000007'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "downloadPodcastEpisode"
    # id
    params = '&id=700000102'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deletePodcastEpisode"
    # id
    params = '&id=700000102'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "jukeboxControl"
    # action
    # index
    # offset
    # id
    # gain
    params = '&action=status'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)
    if os.path.isfile(docpath + "jukeboxControl." + api_format):
        shutil.move(docpath + "jukeboxControl." + api_format,
            docpath + "jukeboxControl (status)." + api_format)
    params = '&action=get'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)
    if os.path.isfile(docpath + "jukeboxControl." + api_format):
        shutil.move(docpath + "jukeboxControl." + api_format,
            docpath + "jukeboxControl (get)." + api_format)

    action = "getInternetRadioStations"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "updateInternetRadioStation"
    # id
    # streamUrl
    # name
    # homepageUrl
    params = '&id=3&streamUrl=https://iheart.4zzz.org.au/4zzz&name=4ZZZ%20Community%20Radio&homepageUrl=https://4zzzfm.org.au'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteInternetRadioStation"
    # id
    params = '&id=29864'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getChatMessages"
    # since
    params = ''
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "addChatMessage"
    # message
    params = '&message=Api%20Script%20Testing'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getUser"
    # username
    params = '&username=guest'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getUsers"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

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
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteUser"
    # username
    params = '&username=created'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "changePassword"
    # username
    # password
    params = '&username=demo&password=demodemo'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "createBookmark"
    # id
    # position
    # comment
    params = '&id=300000060&position=2000'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getBookmarks"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "deleteBookmark"
    # id
    params = '&id=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getPlayQueue"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    # Returns an empty <subsonic-response> element on success.
    action = "savePlayQueue"
    # id
    # current
    # position
    params = '&id=300000060&current=300000060'
    fetch_url = base_url + action + base_parameters + params
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "getScanStatus"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

    action = "startScan"
    fetch_url = base_url + action + base_parameters
    ampacheConnection.fetch_url(fetch_url, api_format, action)

if APIVERSION == 6:
    api_version = api6_version
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
elif APIVERSION == 5:
    api_version = api5_version
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
elif APIVERSION == 4:
    api_version = api4_version
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
elif APIVERSION == 3:
    api_version = api3_version
    build_docs(url, api, user, 'xml')
elif APIVERSION == 16:
    api_version = subsonic_api
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
else:
    api_version = api6_version
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
    api_version = api5_version
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
    api_version = api4_version
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')
    api_version = api3_version
    build_docs(url, api, user, 'xml')
    api_version = subsonic_api
    build_docs(url, api, user, 'json')
    build_docs(url, api, user, 'xml')

