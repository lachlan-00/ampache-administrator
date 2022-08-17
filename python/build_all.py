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
api5_version = '5.5.0'
docpath = "docs/"
song_url = 'https://music.com.au/play/index.php?ssid=eeb9f1b6056246a7d563f479f518bb34&type=song&oid=60&uid=4&player=api&name=Synthetic%20-%20BrownSmoke.wma'
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


def build_docs(ampache_url, ampache_api, ampache_user, api_format):
    ampacheConnection = ampache.API()
    """TODO
    def stream(id, type, destination, api_format = 'xml'):
    def download(id, type, destination, format = 'raw', api_format = 'xml'):
    get_similar: send artist or song id to get related objects from last.fm
    podcast_episode_delete: delete an existing podcast_episode
    catalogs: get all the catalogs
    catalog: get a catalog by id
    catalog_file: clean, add, verify using the file path (good for scripting)
    """

    """ def set_debug(boolean):
        This function can be used to enable/disable debugging messages
    """
    ampacheConnection.set_debug(False)
    ampacheConnection.set_format(api_format)
    print(ampacheConnection.AMPACHE_API)

    if (api_version == api3_version):
        ampacheConnection.set_debug_path("python3-ampache3/docs/")
        docpath = "python3-ampache3/docs/" + api_format + "-responses/"
        ampache3_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)
    if (api_version == api4_version):
        ampacheConnection.set_debug_path("python3-ampache4/docs/")
        docpath = "python3-ampache4/docs/" + api_format + "-responses/"
        ampache4_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)
    if (api_version == api5_version):
        ampacheConnection.set_debug_path("python3-ampache5/docs/")
        docpath = "python3-ampache5/docs/" + api_format + "-responses/"
        ampache5_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath)


def self_check(api_format, ampache_url, ampache_api, ampache_session, docpath):
    print("Checking files in " + docpath + " for private strings")
    for files in os.listdir("./" + docpath):
        f = open("./" + docpath + files, 'r', encoding="utf-8")
        filedata = f.read()
        f.close()

        url_text = ampache_url.replace("https://", "")
        url_text = ampache_url.replace("http://", "")
        url_json = url_text.replace("/", "\\/")
        newdata = re.sub(url_text, "music.com.au", filedata)
        newdata = re.sub(url_text.replace("/", "\\/"), "music.com.au", newdata)
        newdata = re.sub("http://music.com.au", "https://music.com.au", newdata)
        newdata = re.sub("http:\\/\\/music.com.au", "https:\\/\\/music.com.au", newdata)
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
    if os.path.isfile(docpath + api_format + "-responses/ping." + api_format):
        shutil.move(docpath + api_format + "-responses/ping." + api_format,
                    docpath + api_format + "-responses/ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', False, False, api_version)
    if os.path.isfile(docpath + api_format + "-responses/handshake." + api_format):
        shutil.move(docpath + api_format + "-responses/handshake." + api_format,
                    docpath + api_format + "-responses/handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, False, False, api_version)
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
    if os.path.isfile("docs/" + api_format + "-responses/advanced_search." + api_format):
        shutil.move("docs/" + api_format + "-responses/advanced_search." + api_format,
                    "docs/" + api_format + "-responses/advanced_search (song)." + api_format)

    if api_format == 'xml':
        song_id = search_song[1].attrib['id']
    else:
        print(search_song['song'][0]['title'])
        song_id = search_song['song'][0]['id']
    song_title = "Fasten Your Seatbelt"

    search_rules = [['artist', 0, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(album\).xml)
    search_album = ampacheConnection.advanced_search(search_rules, 'or', 'album', offset, limit, 0)
    if os.path.isfile("docs/" + api_format + "-responses/advanced_search." + api_format):
        shutil.move("docs/" + api_format + "-responses/advanced_search." + api_format,
                    "docs/" + api_format + "-responses/advanced_search (album)." + api_format)

    if api_format == 'xml':
        for child in search_album:
            if child.tag == 'album':
                album_title = child.find('name').text
    else:
        album_title = search_album['album'][0]['name']

    search_rules = [['artist', 2, 'CARN'], ['artist', 2, 'Synthetic']]
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/advanced_search%20\(artist\).xml)
    search_artist = ampacheConnection.advanced_search(search_rules, 'or', 'artist', offset, limit, 0)
    if os.path.isfile("docs/" + api_format + "-responses/advanced_search." + api_format):
        shutil.move("docs/" + api_format + "-responses/advanced_search." + api_format,
                    "docs/" + api_format + "-responses/advanced_search (artist)." + api_format)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/album_songs.xml)
    ampacheConnection.album_songs(110, offset, limit)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/album.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist_albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/artist.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/followers.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/following.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/friends_timeline.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/last_shouts.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/localplay.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_add_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_remove_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/playlist.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/rate.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/search_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/stats%20\(album\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/stats%20\(artist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/stats%20\(song\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tags.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/tag.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/timeline.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/toggle_follow.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/url_to_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/user.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/videos.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/video.xml)
    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


def ampache4_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    # send a bad ping
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/ping.xml)
    ampacheConnection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + api_format + "-responses/ping." + api_format):
        shutil.move(docpath + api_format + "-responses/ping." + api_format,
                    docpath + api_format + "-responses/ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', False, False, api_version)
    if os.path.isfile(docpath + api_format + "-responses/handshake." + api_format):
        shutil.move(docpath + api_format + "-responses/handshake." + api_format,
                    docpath + api_format + "-responses/handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, False, False, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/advanced_search%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/advanced_search%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/advanced_search%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/album.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/album_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/artist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_action%20\(clean_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalog.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/catalogs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/democratic%20\(play\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/democratic%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/democratic%20\(vote\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/flag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/followers.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/following.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/friends_timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_indexes%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/goodbye.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/handshake.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/json-responses/handshake%20\(error\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/last_shouts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/license.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/licenses.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/license_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/localplay%20\(status\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/localplay.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/ping.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_add_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_generate%20\(id\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_generate%20\(index\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_generate%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_remove_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/playlist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_episode_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_episode.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/podcasts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/rate.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/scrobble.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/search_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/share.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/shares.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/stats%20\(album\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/stats%20\(artist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/stats%20\(song\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/tag_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/toggle_follow.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_artist_info.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_art.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_from_tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/update_podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/url_to_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/user_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/video.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/json-responses/videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/advanced_search%20\(album\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/advanced_search%20\(artist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/advanced_search%20\(song\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/album_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/album.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist_albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/artist.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_action%20\(add_to_catalog.xml))
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_action%20\(clean_catalog.xml))
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalogs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/catalog.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/flag.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/followers.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/following.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/friends_timeline.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(album\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(artist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(playlist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_indexes%20\(song\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/get_similar.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/goodbye.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/handshake.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/handshake%20\(error\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/last_shouts.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/license_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/licenses.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/license.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/localplay%20\(status\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/localplay.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/ping.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(id\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(index\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_generate%20\(song\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_remove_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/playlist.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_episode_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_episodes.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast_episode.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcasts.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/podcast.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/rate.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/record_play.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/scrobble.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/search_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/shares.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/share.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/stats%20\(album\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/stats%20\(artist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/stats%20\(song\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag_albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag_artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tags.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/tag.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/timeline.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/toggle_follow.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_artist_info.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_art.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_from_tags.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/update_podcast.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/url_to_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user_update.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/user.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/videos.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/video.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api4/docs/xml-responses/.xml)
    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


def ampache5_methods(ampacheConnection, ampache_url, ampache_api, ampache_user, api_format, docpath):
    # send a bad ping
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/ping.xml)
    ampacheConnection.ping(ampache_url, False, api_version)
    if os.path.isfile(docpath + api_format + "-responses/ping." + api_format):
        shutil.move(docpath + api_format + "-responses/ping." + api_format,
                    docpath + api_format + "-responses/ping (no auth)." + api_format)

    encrypted_key = ampacheConnection.encrypt_string(ampache_api, ampache_user)

    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake%20\(error\).xml)
    ampacheConnection.handshake(ampache_url, 'badkey', False, False, api_version)
    if os.path.isfile(docpath + api_format + "-responses/handshake." + api_format):
        shutil.move(docpath + api_format + "-responses/handshake." + api_format,
                    docpath + api_format + "-responses/handshake (error)." + api_format)
    # use correct details
    # (https://raw.githubusercontent.com/ampache/python3-ampache/api3/docs/xml-responses/handshake.xml)
    ampache_session = ampacheConnection.handshake(ampache_url, encrypted_key, False, False, api_version)
    if not ampache_session:
        print(encrypted_key)
        sys.exit('ERROR: Failed to connect to ' + ampache_url)

    my_ping = ampacheConnection.ping(ampache_url, ampache_session, api_version)
    if not my_ping:
        print()
        sys.exit('ERROR: Failed to ping ' + ampache_url)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/album.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/album_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/artist_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/artist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/artist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/bookmark_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/bookmark_delete)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/bookmark_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/bookmarks.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/catalog_action%20\(clean_catalog\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/catalog_file.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/catalog.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/catalogs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/deleted_podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/deleted_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/deleted_videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/democratic%20\(play\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/democratic%20\(playlist\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/democratic%20\(vote\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/flag.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/followers.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/following.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/friends_timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/genre_albums.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/genre_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/genre.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/genres.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/genre_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/get_bookmark.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/get_similar.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/goodbye.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/handshake.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/handshake%20\(error\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/label_artists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/label.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/labels.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/last_shouts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/license.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/licenses.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/license_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/live_stream.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/live_streams.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/localplay%20\(status\).json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/localplay.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/ping.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist_add_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist_remove_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlists.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/playlist_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast_episode_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast_episode.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast_episodes.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/podcasts.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/preference_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/preference_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/preference_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/rate.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/record_play.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/scrobble.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/search_songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/share_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/share_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/share_edit.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/share.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/shares.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/song_delete.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/songs.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/system_preferences.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/system_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/timeline.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/toggle_follow.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/update_artist_info.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/update_art.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/update_from_tags.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/update_podcast.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/url_to_song.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/user_create.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/user.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/user_preference.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/user_preferences.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/users.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/user_update.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/video.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/json-responses/videos.json)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/album_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/album.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/artist_albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/artist_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/artist.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/bookmark_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/bookmark_delete)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/bookmark_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/bookmarks.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/catalog_action%20\(add_to_catalog\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/catalog_action%20\(clean_catalog\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/catalog_file.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/catalogs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/catalog.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/deleted_podcast_episodes.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/deleted_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/deleted_videos.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/democratic%20\(playlist\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/democratic%20\(play\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/democratic%20\(vote\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/flag.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/followers.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/following.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/friends_timeline.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/genre_albums.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/genre_artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/genre_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/genres.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/genre.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/get_bookmark.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/get_similar.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/goodbye.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/handshake.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/handshake%20\(error\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/label_artists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/labels.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/label.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/last_shouts.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/license_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/licenses.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/license.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/live_streams.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/live_stream.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/localplay%20\(status\).xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/localplay.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/ping.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist_add_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist_remove_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlists.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/playlist.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast_episode_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast_episodes.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast_episode.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcasts.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/podcast.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/preference_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/preference_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/preference_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/rate.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/record_play.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/scrobble.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/search_songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/share_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/share_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/share_edit.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/shares.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/share.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/song_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/songs.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/system_preferences.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/system_update.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/timeline.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/toggle_follow.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/update_artist_info.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/update_art.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/update_from_tags.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/update_podcast.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/url_to_song.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/user_create.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/user_delete.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/user_preferences.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/user_preference.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/users.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/user_update.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/user.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/videos.xml)
    # (https://raw.githubusercontent.com/ampache/python3-ampache/master/docs/xml-responses/video.xml)
    # Clean the files
    self_check(api_format, ampache_url, ampache_api, ampache_session, docpath)


api_version = api3_version
build_docs(url, api, user, 'xml')

api_version = api4_version
build_docs(url, api, user, 'json')
build_docs(url, api, user, 'xml')

api_version = api5_version
build_docs(url, api, user, 'json')
build_docs(url, api, user, 'xml')
