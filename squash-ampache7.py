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

self_check("./ampache-squashed7/lib/javascript/search-data.php", "\$dic = require __DIR__ \. '/\.\./\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../../src/Config/Init.php';")

self_check("./ampache-squashed7/src", "/public/", "/")
self_check("./ampache-squashed7/templates", "/public/", "/")
self_check("./ampache-squashed7/templates", "/\.\./\.\./", "/../")

self_check("./ampache-squashed7/albums.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/logout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/show_get.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/artists.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/lostpassword.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/smartplaylist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/arts.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/mashup.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/song.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/batch.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/now_playing.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/stats.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/broadcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/phpinfo.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/stream.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/browse.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/playlist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/test.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/channel.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/podcast_episode.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/tvshow_seasons.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/cookie_disclaimer.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/podcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/tvshows.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/democratic.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/preferences.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/update.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/error.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/pvmsg.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/upload.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/graph.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/radio.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/util.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/image.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/random.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/video.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/index.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/register.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/waveform.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/install.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/rss.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/web_player_embedded.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/labels.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/search.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/web_player.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/localplay.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/share.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/login.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed7/shout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")

self_check("./ampache-squashed7/composer.json", "public/lib", "lib")
self_check("./ampache-squashed7/package.json", "public/lib", "lib")
self_check("./ampache-squashed7/locale/base/gather-messages.sh", "public/lib", "lib")

self_check("./ampache-squashed7/admin", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/captcha", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/daap", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/play", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/rest", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/server", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/upnp", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed7/webdav", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")

