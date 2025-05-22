#!/usr/bin/env python3
import ampache
import os
import re
import shutil
import sys

# Update using the API
def update_ampache(api, api_format, version):
    # load up previous config
    if not api.get_config():
        # Set your details manually if we can't get anything
        api.set_url('https://music.server')
        api.set_key('mysuperapikey')
        api.set_user('myusername')

    api.set_version(version)
    api.set_format(api_format)
    if api_format == 'json':
        api.set_debug_path('python3-ampache' + version[0] + '/docs/json-responses/')
    else:
        api.set_debug_path('python3-ampache' + version[0] + '/docs/xml-responses/')

    """ Get a session key using the handshake

        * ampache_url = (string) Full Ampache URL e.g. 'https://music.com.au'
        * ampache_api = (string) encrypted apikey OR password if using password auth
        * user        = (string) username //optional
        * timestamp   = (integer) UNIXTIME() //optional
        * version     = (string) API Version //optional
    """
    ampache_session = api.execute('handshake')

    # Fail if you didn't connect
    if not ampache_session:
        sys.exit(api.AMPACHE_VERSION + ' ERROR Failed to connect to ' + api.AMPACHE_URL)
    api.execute('lost_password', {"email": 'demo@ampache.dev', "user": 'demo' })
    api.execute('ping')
    api.execute('advanced_search', {"rules": '', "operator": '', "object_type": '', "offset": '', "limit": '', "random": ''})
    api.execute('search', {"rules": '', "operator": '', "object_type": '', "offset": '', "limit": '', "random": ''})
    api.execute('search_group', {"filter_id": '', "operator": '', "object_type": '', "offset": '', "limit": '', "random": ''})
    api.execute('album', {"filter_id": '', "include": ''})
    api.execute('albums', {"filter_str": '', "exact": '', "add": '', "update": '', "offset": '', "limit": '', "include": '', "sort": '', "cond": ''})
    api.execute('album_songs', {"filter_id": '', "offset": '', "limit": '', "exact": '', "sort": '', "cond": ''})
    api.execute('artist', {"filter_id": '', "include": ''})
    api.execute('artist_albums', {"filter_id": '', "offset": '', "limit": '', "album_artist": '', "sort": '', "cond": ''})
    api.execute('artists', {"filter_str": '', "add": '', "update": '', "offset": '', "limit": '', "include": '', "album_artist": '', "sort": '', "cond": ''})
    api.execute('artist_songs', {"filter_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('bookmark', {"filter_id": '', "include": ''})
    api.execute('bookmark_create', {"filter_id": '', "object_type": '', "position": '', "client": '', "date": '', "include": ''})
    api.execute('bookmark_delete', {"filter_id": '', "object_type": ''})
    api.execute('bookmark_edit', {"filter_id": '', "object_type": '', "position": '', "client": '', "date": '', "include": ''})
    api.execute('bookmarks', {"client": '', "include": ''})
    api.execute('browse', {"filter_str": '', "object_type": '', "catalog": '', "add": '', "update": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('catalog', {"filter_id": '', "offset": '', "limit": ''})
    api.execute('catalog_action', {"task": '', "catalog_id": ''})
    api.execute('catalog_add', {"cat_name": '', "cat_path": '', "cat_type": '', "media_type": '', "file_pattern": '', "folder_pattern": '', "username": '', "password": ''})
    api.execute('catalog_delete', {"filter_id": ''})
    api.execute('catalog_file', {"file": '', "task": '', "catalog_id": ''})
    api.execute('catalog_folder', {"folder": '', "task": '', "catalog_id": ''})
    api.execute('catalogs', {"filter_str": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('deleted_podcast_episodes', {"offset": '', "limit": ''})
    api.execute('deleted_songs', {"offset": '', "limit": ''})
    api.execute('deleted_videos', {"offset": '', "limit": ''})
    api.execute('democratic', {"method": 'playlist', "oid": '1'})
    api.execute('download', {"object_id": '', "object_type": '', "destination": './download', "stats": ''})
    api.execute('flag', {"object_type": '', "object_id": '', "flagbool": '', "date": ''})
    api.execute('followers', {"username": '', "sort": '', "cond": ''})
    api.execute('following', {"username": ''})
    api.execute('friends_timeline', {"limit": '', "since": ''})
    api.execute('genre', {"filter_id": ''})
    api.execute('genre_albums', {"filter_id": '', "sort": '', "cond": ''})
    api.execute('genre_artists', {"username": '', "sort": '', "cond": ''})
    api.execute('genres', {"username": '', "sort": '', "cond": ''})
    api.execute('genre_songs', {"filter_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('get_art', {"object_id": '', "object_type": '', "destination": ''})
    api.execute('get_bookmark', {"filter_id": '', "object_type": '', "include": '', "show_all": ''})
    api.execute('get_external_metadata', {"filter_id": '', "object_type": ''})
    api.execute('get_indexes', {"object_type": '', "filter_str": '', "exact": '', "add": '', "update": '', "include": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('get_similar', {"object_type": '', "filter_id": '', "offset": '', "limit": ''})
    api.execute('index', {"object_type": '', "filter_str": '', "exact": '', "add": '', "update": '', "include": '', "offset": '', "limit": '', "hide_search": '', "sort": '', "cond": ''})
    api.execute('label', {"filter_id": ''})
    api.execute('label_artists', {"filter_id": '', "sort": '', "cond": ''})
    api.execute('labels', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('last_shouts', {"username": '', "limit": ''})
    api.execute('license', {"filter_id": ''})
    api.execute('licenses', {"filter_str": '', "exact": '', "add": '', "update": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('license_songs', {"filter_id": '', "sort": '', "cond": ''})
    api.execute('list', {"object_type": '', "filter_str": '', "exact": '', "add": '', "update": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('live_stream', {"filter_id": ''})
    api.execute('live_stream_create', {"name": '', "stream_url": '', "codec": '', "catalog_id": '', "site_url": ''})
    api.execute('live_stream_delete', {"filter_id": ''})
    api.execute('live_stream_edit', {"filter_id": '', "name": '', "stream_url": '', "codec": '', "catalog_id": '', "site_url": ''})
    api.execute('live_streams', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('localplay', {"command": ''})
    api.execute('localplay_songs')
    api.execute('now_playing')
    api.execute('player', {"filter_str": '', "object_type": '', "state": '', "play_time": '', "client": ''})
    api.execute('playlist', {"filter_id": ''})
    api.execute('playlist_add', {"filter_id": '', "object_id": '', "object_type": ''})
    api.execute('playlist_add_song', {"filter_id": '', "song_id": '', "check": ''})
    api.execute('playlist_create', {"playlist_name": '', "playlist_type": ''})
    api.execute('playlist_delete', {"filter_id": ''})
    api.execute('playlist_edit', {"filter_id": '', "playlist_name": '', "playlist_type": '', "owner": '', "items": '', "tracks": ''})
    api.execute('playlist_generate', {"mode": '', "filter_str": '', "album_id": '', "artist_id": '', "flagged": '', "list_format": '', "offset": '', "limit": ''})
    api.execute('playlist_hash', {"filter_id": ''})
    api.execute('playlist_remove_song', {"filter_id": ''})
    api.execute('playlists', {"filter_str": '', "exact": '', "offset": '', "limit": '', "hide_search": '', "show_dupes": '', "include": '', "sort": '', "cond": ''})
    api.execute('playlist_songs', {"filter_id": '', "random": '', "offset": '', "limit": ''})
    api.execute('podcast', {"filter_id": '', "include": ''})
    api.execute('podcast_create', {"url": '', "catalog_id": ''})
    api.execute('podcast_delete', {"filter_id": ''})
    api.execute('podcast_edit', {"filter_id": '', "feed": '', "title": '', "website": '', "description": '', "generator": '', "copyright_str": ''})
    api.execute('podcast_episode', {"filter_id": ''})
    api.execute('podcast_episode_delete', {"filter_id": ''})
    api.execute('podcast_episodes', {"filter_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('podcasts', {"filter_id": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('preference_create', {"filter_str": '', "type_str": '', "category": '', "description": '', "subcategory": '', "level": ''})
    api.execute('preference_delete', {"filter_str": ''})
    api.execute('preference_edit', {"filter_str": '', "value": '', "apply_all": ''})
    api.execute('rate', {"object_type": '', "object_id": '', "rating": ''})
    api.execute('record_play', {"object_id": '', "user_id": '', "client": '', "date": ''})
    api.execute('register', {"username": '', "fullname": '', "password": '', "email": ''})
    api.execute('scrobble', {"title": '', "artist_name": '', "album_name": '', "mbtitle": '', "mbartist": '', "mbalbum": '', "stime": '', "client": ''})
    api.execute('search_songs', {"filter_str": '', "offset": '', "limit": ''})
    api.execute('share', {"filter_id": ''})
    api.execute('share_create', {"filter_id": '', "object_type": '', "description": '', "expires": ''})
    api.execute('share_delete', {"filter_id": ''})
    api.execute('share_edit', {"filter_id": '', "can_stream": '', "can_download": '', "expires": '', "description": ''})
    api.execute('shares', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('song', {"filter_id": ''})
    api.execute('song_delete', {"filter_id": ''})
    api.execute('song_tags', {"filter_id": ''})
    api.execute('songs', {"filter_str": '', "exact": '', "add": '', "update": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('stats', {"object_type": '', "filter_str": '', "username": '', "user_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('stream', {"object_id": '', "object_type": '', "destination": '', "stats": ''})
    api.execute('system_preference', {"filter_str": ''})
    api.execute('system_preferences')
    api.execute('system_update')
    api.execute('tag', {"filter_id": ''})
    api.execute('tag_albums', {"filter_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('tag_artists', {"filter_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('tags', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('tag_songs', {"filter_id": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('timeline', {"username": '', "limit": '', "since": ''})
    api.execute('toggle_follow', {"username": ''})
    api.execute('update_art', {"object_type": '', "object_id": '', "overwrite": ''})
    api.execute('update_artist_info', {"filter_id": ''})
    api.execute('update_from_tags', {"object_type": '', "object_id": ''})
    api.execute('update_podcast', {"filter_id": ''})
    api.execute('url_to_song', {"url": ''})
    api.execute('user', {"username": ''})
    api.execute('user_create', {"username": '', "password": '', "email": '', "fullname": '', "disable": ''})
    api.execute('user_delete', {"username": ''})
    api.execute('user_edit', {"username": '', "password": '', "fullname": '', "email": '', "website": '', "state": '', "city": '', "disable": '', "maxbitrate": '', "fullname_public": '', "reset_apikey": '', "reset_streamtoken": '', "clear_stats": ''})
    api.execute('user_playlists', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('user_preference', {"filter_str": ''})
    api.execute('user_preferences')
    api.execute('users', {"sort": '', "cond": ''})
    api.execute('user_smartlists', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    api.execute('user_update', {"username": '', "password": '', "fullname": '', "email": '', "website": '', "state": '', "city": '', "disable": '', "maxbitrate": '', "fullname_public": '', "reset_apikey": '', "reset_streamtoken": '', "clear_stats": ''})
    api.execute('video', {"filter_id": ''})
    api.execute('videos', {"filter_str": '', "exact": '', "offset": '', "limit": '', "sort": '', "cond": ''})
    
    api.execute('goodbye')

    self_check(api.AMPACHE_URL, api.AMPACHE_KEY, api.AMPACHE_SESSION, api.DOCS_PATH)

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


def main():
    # Open Ampache library
    ampache_connection = ampache.API()

    ampache_connection.set_debug(True)

    for version in ['6.7.0', '5.5.6', '443000', '390001']:
        update_ampache(ampache_connection, 'json', version)
        update_ampache(ampache_connection, 'xml', version)

if __name__ == "__main__":
    main()
