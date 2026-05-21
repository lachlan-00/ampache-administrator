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

self_check("./ampache-squashed8/lib/javascript/search-data.php", "\$dic = require __DIR__ \. '/\.\./\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../../src/Config/Init.php';")

self_check("./ampache-squashed8/src", "/public/", "/")
self_check("./ampache-squashed8/templates", "/public/", "/")
self_check("./ampache-squashed8/templates", "/\.\./\.\./", "/../")

self_check("./ampache-squashed8/albums.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/logout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/show_get.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/artists.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/lostpassword.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/smartplaylist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/arts.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/mashup.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/song.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/batch.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/now_playing.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/stats.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/broadcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/phpinfo.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/stream.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/browse.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/playlist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/test.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/channel.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/podcast_episode.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/tvshow_seasons.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/cookie_disclaimer.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/podcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/tvshows.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/democratic.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/preferences.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/update.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/error.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/pvmsg.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/upload.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/graph.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/radio.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/util.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/image.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/random.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/video.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/index.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/register.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/waveform.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/install.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/rss.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/web_player_embedded.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/labels.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/search.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/web_player.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/localplay.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/share.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/login.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed8/shout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")

self_check("./ampache-squashed8/composer.json", "public/lib", "lib")
self_check("./ampache-squashed8/package.json", "public/lib", "lib")
self_check("./ampache-squashed8/locale/base/gather-messages.sh", "public/lib", "lib")

self_check("./ampache-squashed8/admin", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/captcha", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/daap", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/play", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/rest", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/server", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/upnp", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed8/webdav", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")

