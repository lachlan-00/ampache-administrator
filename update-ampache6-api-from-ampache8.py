#!/usr/bin/env python3

import codecs
import os
import re
import shutil

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

# The directory name is not the branch name, so both ends are named once here rather than inline.
# Before the develop8 -> develop rename these read ampache-develop8 (source) and ampache-develop
# (target); ampache-develop is now the Ampache8 tree itself, so the old target would downgrade
# Ampache8's own API to API6.
SRC = './ampache-develop'    # Ampache8, branch develop
DEST = './ampache-patch7'    # Ampache7 staging, branch patch7

if not os.path.isdir(SRC) or not os.path.isdir(DEST):
    raise SystemExit('expected %s (Ampache8) and %s (Ampache7); check the branch each is on' % (SRC, DEST))

shutil.copytree(SRC + '/src/Module/Api', DEST + '/src/Module/Api', dirs_exist_ok=True)

os.remove(DEST + "/src/Module/Api/Method/Api8/Folder8Method.php")
os.remove(DEST + "/src/Module/Api/Method/Api8/Folders8Method.php")

self_check(DEST + "/src/Module/Api","public const array ", "public const ")
self_check(DEST + "/src/Module/Api","public const int ", "public const ")
self_check(DEST + "/src/Module/Api","public const string ", "public const ")
self_check(DEST + "/src/Module/Api","public const false ", "public const ")
self_check(DEST + "/src/Module/Api","public const DEFAULT_VERSION = 8", "public const DEFAULT_VERSION = 6")
self_check(DEST + "/src/Module/Api","\(\$api_version == 8 && !Preference::get_by_user\(\$userId, 'api_enable_8'\)\)", "$api_version == 8 //|| ($api_version == 8 && !Preference::get_by_user($userId, 'api_enable_8'))")

