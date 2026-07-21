#!/usr/bin/env python3

"""Rewrite ampache-patch8 paths for the flattened 'squashed8' layout.

build_ampache-squashed8.sh copies ampache-patch8/public/* to the repository
root, so everything that assumed a public/ web root loses one directory level.

Every rewrite below is idempotent: it targets the final value instead of
nudging the current one, so re-running this on a tree that was not refreshed
from ampache-patch8 is safe.  The old relative rewrites ("add one ../") did
corrupt the tree when they ran twice.

The list of files to touch is derived from ampache-patch8/public rather than
hard-coded, so new pages (folders.php, opensearch.php, m/, oidc/, ...) are
picked up automatically and removed ones (channel.php, captcha/, ...) simply
stop being processed.

Usage: squash-ampache8.py [source-public-dir] [target-repo]

Both default to the working copies next to this script. build_release8.sh
passes a release tree instead, so it can assert that re-running this changes
nothing - if it does, the branch is not what the transform produces.
"""

import codecs
import os
import re
import sys

SOURCE = sys.argv[1] if len(sys.argv) > 1 else "./ampache-patch8/public"
TARGET = sys.argv[2] if len(sys.argv) > 2 else "./ampache-squashed8"

# "$dic = require __DIR__ . '/../src/Config/Init.php';" and friends. The number
# of ../ is matched loosely so the correct depth can be written back over it.
INIT_FIND = r"__DIR__ \. '(?:/\.\.)*/src/Config/"

# __DIR__ paths that reach out of the web root into the repository root.
# ./templates is one level below the root, so they all collapse to '/../'.
# Sibling references such as '/../dist/' and '/../lib/' are deliberately not
# matched: templates/../dist is still correct after the move.
ROOT_FIND = r"__DIR__ \. '(?:/\.\.)+/(vendor|config|resources|public)(?=[/'])"


def self_check(folder, find, replace):
    if os.path.isfile(folder):
        print("Reading " + folder)
        f = codecs.open(folder, 'r', encoding="utf-8")
        filedata = f.read()
        f.close()

        newdata = re.sub(find, replace, filedata)

        if newdata != filedata:
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

                    if newdata != filedata:
                        f = codecs.open(filename, 'w', encoding="utf-8")
                        f.write(newdata)
                        f.close()


def php_files(path):
    """Every .php file at or below path."""
    if os.path.isfile(path):
        return [path] if path.endswith(".php") else []
    if not os.path.isdir(path):
        return []
    found = []
    for dirpath, dirnames, filenames in os.walk(path):
        for name in sorted(filenames):
            if name.endswith(".php"):
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def fix_init_depth(repo, relpath):
    """Point src/Config/ requires at the real depth of the file below the repo.

    src/ always sits at the repository root, so the correct number of ../ is
    simply how deep the file ended up. That makes this self-correcting no
    matter what the file currently says.
    """
    for filename in php_files(os.path.join(repo, relpath)):
        parent = os.path.relpath(os.path.dirname(filename), repo)
        depth = 0 if parent == os.curdir else len(parent.split(os.sep))
        self_check(filename, INIT_FIND, "__DIR__ . '" + ("/.." * depth) + "/src/Config/")


def is_page(filename):
    """A web-root page bootstraps the container; rector.php and friends do not."""
    f = codecs.open(filename, 'r', encoding="utf-8")
    filedata = f.read()
    f.close()

    return "src/Config/Init.php" in filedata or "src/Config/Bootstrap.php" in filedata


def report_stale(repo, source):
    """Warn about web-root pages the upstream branch no longer ships.

    These are never refreshed by the build, so they keep whatever paths they
    had and quietly rot. Left for a human to delete rather than removed here.
    """
    for name in sorted(os.listdir(repo)):
        target = os.path.join(repo, name)
        if os.path.exists(os.path.join(source, name)):
            for filename in php_files(target):
                mirror = os.path.join(source, os.path.relpath(filename, repo))
                if not os.path.exists(mirror):
                    print("STALE: " + filename + " no longer exists in " + source)
        elif name.endswith(".php") and os.path.isfile(target) and is_page(target):
            print("STALE: " + target + " no longer exists in " + source)


# public/<anything> is copied to the repository root, so rewrite the requires
# in every page that came across to match where it landed.
for entry in sorted(os.listdir(SOURCE)):
    fix_init_depth(TARGET, entry)

# ./lib/javascript/search-data.php, ./admin/*, ./m/index.php, ./oidc/index.php
# and the root pages are all handled by the loop above.

self_check(TARGET + "/src", "/public/", "/")

# ./templates lost a level too. Fix the repo-root paths before dropping
# "public/", otherwise '/../../public/' has nothing left to match on.
self_check(TARGET + "/templates", ROOT_FIND, "__DIR__ . '/../\\1")
self_check(TARGET + "/templates", "/public/", "/")

self_check(TARGET + "/composer.json", "public/lib", "lib")
self_check(TARGET + "/package.json", "public/lib", "lib")
self_check(TARGET + "/locale/base/gather-messages.sh", "public/lib", "lib")

report_stale(TARGET, SOURCE)
