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

self_check("./ampache-client8/public/client/lib/javascript/search-data.php", "\$dic = require __DIR__ \. '/\.\./\.\./\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../../../src/Config/Init.php';")

self_check("./ampache-client8/src", "/public/", "/public/client/")
self_check("./ampache-client8/src", "AmpConfig::get_web_path\(\)", "AmpConfig::get_web_path('/client')")
self_check("./ampache-client8/src", "getWebPath\(\)", "getWebPath('/client')")

self_check("./ampache-client8/public/client/templates", "\<img src\=\"\.\/images\/", "<img src=\"./client/images/")
self_check("./ampache-client8/public/client/templates", "AmpConfig::get_web_path\(\)", "AmpConfig::get_web_path('/client')")
self_check("./ampache-client8/public/client/templates", "getWebPath\(\)", "getWebPath('/client')")
self_check("./ampache-client8/public/client/templates", "/public/", "/public/client/")
self_check("./ampache-client8/public/client/templates", "/\.\./\.\./", "/../../../")

self_check("./ampache-client8/public/client/albums.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/logout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/show_get.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/artists.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/lostpassword.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/smartplaylist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/arts.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/mashup.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/song.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/batch.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/now_playing.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/stats.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/broadcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/phpinfo.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/stream.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/browse.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/playlist.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/test.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/channel.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/podcast_episode.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/tvshow_seasons.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/cookie_disclaimer.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/podcast.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/tvshows.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/democratic.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/preferences.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/update.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/error.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/pvmsg.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/upload.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/graph.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/radio.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/util.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/image.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/random.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/video.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/index.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/register.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/waveform.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/install.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/rss.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/web_player_embedded.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/labels.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/search.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/web_player.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/localplay.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/share.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/login.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")
self_check("./ampache-client8/public/client/shout.php", "__DIR__ \. '/\.\./", "__DIR__ . '/../../")

self_check("./ampache-client8/composer.json", "public/lib", "public/client/lib")
self_check("./ampache-client8/package.json", "public/lib", "public/client/lib")
self_check("./ampache-client8/locale/base/gather-messages.sh", "public/lib", "public/client/lib")

self_check("./ampache-client8/public/client/captcha", "\$dic = require __DIR__ \. '/\.\./\.\./src/Config/Init\.php';", "$dic = require __DIR__ . '/../../../src/Config/Init.php';")

