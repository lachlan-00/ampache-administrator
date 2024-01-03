#!/usr/bin/env python3

import codecs
import os
import re

def self_check(folder, find, replace):
    if os.path.isfile(folder):
        print("Reading " + folder)
        f = codecs.open(folder, 'r', encoding="utf-8")
        filedata = f.read()
        f.close()

        newdata = re.sub(find, replace, filedata)

        f = codecs.open(folder, 'w', encoding="utf-8")
        f.write(newdata)
        f.close()
    elif os.path.isdir(folder):
        print("DIR " + folder)
        for files in os.listdir(folder):
            filename = os.path.join(folder, files)
            if os.path.isdir(filename):
                self_check(filename, find, replace)
            elif os.path.isfile(filename):
                extension = os.path.splitext(filename)[-1]
                if extension == ".php" or extension == ".json" or extension == ".sh":
                    print("Reading " + extension + ": " + filename)
                    f = codecs.open(filename, 'r', encoding="utf-8")
                    filedata = f.read()
                    f.close()

                    newdata = re.sub(find, replace, filedata)

                    f = codecs.open(filename, 'w', encoding="utf-8")
                    f.write(newdata)
                    f.close()

self_check("./ampache-squashed6/lib/javascript/search-data.php", "\$dic = require __DIR__ \. '/\.\./\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../../src/Config/Init.php';")

self_check("./ampache-squashed6/src", "/public/", "/")
self_check("./ampache-squashed6/templates", "/public/", "/")
self_check("./ampache-squashed6/templates", "/\.\./\.\./", "/../")

self_check("./ampache-squashed6/albums.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/logout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/show_get.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/artists.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/lostpassword.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/smartplaylist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/arts.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/mashup.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/song.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/batch.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/now_playing.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/stats.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/broadcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/phpinfo.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/stream.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/browse.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/playlist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/test.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/channel.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/podcast_episode.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/tvshow_seasons.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/cookie_disclaimer.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/podcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/tvshows.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/democratic.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/preferences.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/update.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/error.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/pvmsg.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/upload.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/graph.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/radio.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/util.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/image.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/random.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/video.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/index.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/register.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/waveform.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/install.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/rss.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/web_player_embedded.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/labels.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/search.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/web_player.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/localplay.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/share.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/login.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed6/shout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")

self_check("./ampache-squashed6/composer.json", "public/lib", "lib")
self_check("./ampache-squashed6/locale/base/gather-messages.sh", "public/lib", "lib")

self_check("./ampache-squashed6/admin", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/captcha", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/daap", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/play", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/rest", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/server", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/upnp", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed6/webdav", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")

