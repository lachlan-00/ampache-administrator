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

self_check("./ampache-squashed/lib/javascript/search-data.php", "\$dic = require __DIR__ \. '/\.\./\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../../src/Config/Init.php';")

self_check("./ampache-squashed/src", "/public/", "/")
self_check("./ampache-squashed/templates", "/public/", "/")

self_check("./ampache-squashed/albums.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/logout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/show_get.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/artists.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/lostpassword.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/smartplaylist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/arts.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/mashup.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/song.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/batch.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/now_playing.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/stats.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/broadcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/phpinfo.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/stream.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/browse.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/playlist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/test.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/channel.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/podcast_episode.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/tvshow_seasons.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/cookie_disclaimer.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/podcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/tvshows.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/democratic.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/preferences.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/update.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/error.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/pvmsg.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/upload.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/graph.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/radio.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/util.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/image.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/random.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/video.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/index.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/register.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/waveform.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/install.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/rss.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/web_player_embedded.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/labels.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/search.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/web_player.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/localplay.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/share.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/login.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")
self_check("./ampache-squashed/shout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/")

self_check("./ampache-squashed/composer.json", "public/lib", "lib")
self_check("./ampache-squashed/locale/base/gather-messages.sh", "public/lib", "lib")

self_check("./ampache-squashed/admin", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/channel", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/daap", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/play", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/rest", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/server", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/upnp", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")
self_check("./ampache-squashed/webdav", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../src/Config/Init.php';")

