#!/usr/bin/env python3

"""Rewrite ampache-patch8 paths for the 'client8' layout.

build_ampache-client8.sh keeps the server endpoints where they are and pushes
the whole web UI down into public/client/, so anything under there gains one
directory level:

    public/admin|daap|oidc|rest|server|upnp|webdav/   unchanged
    public/folders.php|index.php|opensearch.php       unchanged
    public/client/*.php                               was public/*.php
    public/client/dist|images|lib|m|play|templates|themes/

oidc/ stays at the web root so the redirect URI registered with the identity
provider does not move; play/ follows the UI so that the /play/ URLs built
from get_web_path('/client') resolve.

Every rewrite below is idempotent: it targets the final value instead of
nudging the current one, so re-running this on a tree that was not refreshed
from ampache-patch8 is safe. The old relative rewrites ("add one ../") did
corrupt the tree when they ran twice.

The list of files to touch is derived from ampache-patch8/public rather than
hard-coded, so new pages (folders.php, opensearch.php, m/, oidc/, ...) are
picked up automatically and removed ones (channel.php, captcha/, ...) simply
stop being processed.

Usage: client-ampache8.py [source-public-dir] [target-repo]

Both default to the working copies next to this script. build_release8.sh
passes a release tree instead, so it can assert that re-running this changes
nothing - if it does, the branch is not what the transform produces.
"""

import codecs
import os
import re
import sys

SOURCE = sys.argv[1] if len(sys.argv) > 1 else "./ampache-patch8/public"
TARGET = sys.argv[2] if len(sys.argv) > 2 else "./ampache-client8"

# entries of ampache-patch8/public that stay at the web root; everything else
# is served from public/client/
ROOT_ENTRIES = ("admin", "daap", "oidc", "rest", "server", "upnp", "webdav")

# "$dic = require __DIR__ . '/../src/Config/Init.php';" and friends. The number
# of ../ is matched loosely so the correct depth can be written back over it.
INIT_FIND = r"__DIR__ \. '(?:/\.\.)*/src/Config/"

# collapse /public/, /public/client/ and the /public/client/client/ left behind
# by earlier double runs onto a single canonical value
CLIENT_FIND = r"/public/(?:client/)*"

# ...except the endpoints that stayed at the web root
ROOT_RESTORE = r"/public/client/(" + "|".join(ROOT_ENTRIES) + r")/"

# URL paths that are not served from /client/ either: the endpoints above, plus
# the analytics plugins, which point at a separate install and never lived in
# the tree at all. play/ and m/ are deliberately absent - they did move.
ROOT_URLS = ROOT_ENTRIES + ("matomo", "piwik")

# undo the blanket web path suffix for those, e.g. the sse.server.php URL
ROOT_URL_RESTORE = (r"(get_web_path|getWebPath)\('/client'\) \. ([\"'])/("
                    + "|".join(ROOT_URLS) + r")/")

# __DIR__ paths that reach out of the web root into the repository root.
# public/client/templates is three levels below the root. Sibling references
# such as '/../dist/' and '/../lib/' are deliberately not matched: they still
# resolve inside public/client/ after the move.
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


def destination(name):
    """Where ampache-patch8/public/<name> ends up in the client layout."""
    if name in ROOT_ENTRIES:
        return os.path.join("public", name)
    return os.path.join("public", "client", name)


def fix_init_depth(repo, relpath):
    """Point src/Config/ requires at the real depth of the file below the repo.

    src/ always sits at the repository root, so the correct number of ../ is
    simply how deep the file ended up: two for public/client/song.php, three
    for public/client/m/index.php, four for public/client/lib/javascript/
    search-data.php. That makes this self-correcting no matter what the file
    currently says.
    """
    for filename in php_files(os.path.join(repo, relpath)):
        parent = os.path.relpath(os.path.dirname(filename), repo)
        depth = 0 if parent == os.curdir else len(parent.split(os.sep))
        self_check(filename, INIT_FIND, "__DIR__ . '" + ("/.." * depth) + "/src/Config/")


def report_stale(repo, source):
    """Warn about web-root pages the upstream branch no longer ships.

    These are never refreshed by the build, so they keep whatever paths they
    had and quietly rot. Left for a human to delete rather than removed here.
    """
    expected = set()
    for name in sorted(os.listdir(source)):
        entry = os.path.join(source, name)
        if os.path.isfile(entry):
            if name.endswith(".php"):
                # the build copies public/*.php into public/client/, and the
                # web root keeps its own hand-maintained copy of some of them
                expected.add(destination(name))
                expected.add(os.path.join("public", name))
        else:
            for filename in php_files(entry):
                expected.add(os.path.join(destination(name), os.path.relpath(filename, entry)))

    for filename in php_files(os.path.join(repo, "public")):
        if os.path.relpath(filename, repo) not in expected:
            print("STALE: " + filename + " no longer exists in " + source)


# src/ always sits at the repository root, so every page under public/ wants a
# ../ for each level it is nested, whichever side of the split it landed on.
fix_init_depth(TARGET, "public")

self_check(TARGET + "/src", CLIENT_FIND, "/public/client/")
self_check(TARGET + "/src", ROOT_RESTORE, "/public/\\1/")
self_check(TARGET + "/src", "AmpConfig::get_web_path\\(\\)", "AmpConfig::get_web_path('/client')")
self_check(TARGET + "/src", "getWebPath\\(\\)", "getWebPath('/client')")

self_check(TARGET + "/src", ROOT_URL_RESTORE, "\\1() . \\2/\\3/")

# install_rewrite_rules() is handed the bare web root and prepends it to every
# RewriteRule target it writes. The targets in the .htaccess.dist files are
# already written relative to that root, so suffixing the argument here would
# double the /client segment on every rule.
self_check(TARGET + "/src/Module/Cli/HtaccessCommand.php",
           r"(install_rewrite_rules\([^,]+, \$this->configContainer->getWebPath)\('/client'\)",
           "\\1()")

# the OIDC callback answers from public/oidc/, not public/client/oidc/, so it
# must keep the bare web path or the redirect URI stops matching the one
# registered with the identity provider. Not covered by ROOT_URL_RESTORE
# because the path comes from a constant rather than a literal.
self_check(TARGET + "/src/Module/Authentication/Oidc/OidcClientFactory.php",
           "getWebPath\\('/client'\\) \\. self::CALLBACK_PATH",
           "getWebPath() . self::CALLBACK_PATH")

# public/client/templates gained a level. Fix the repo-root paths before
# rewriting "public/", otherwise '/../../public/client/' gets counted twice.
self_check(TARGET + "/public/client/templates", ROOT_FIND, "__DIR__ . '/../../../\\1")
self_check(TARGET + "/public/client/templates", CLIENT_FIND, "/public/client/")
self_check(TARGET + "/public/client/templates", ROOT_RESTORE, "/public/\\1/")
self_check(TARGET + "/public/client/templates", "\\<img src\\=\"\\./(client/)*images/", "<img src=\"./client/images/")
self_check(TARGET + "/public/client/templates", "AmpConfig::get_web_path\\(\\)", "AmpConfig::get_web_path('/client')")
self_check(TARGET + "/public/client/templates", "getWebPath\\(\\)", "getWebPath('/client')")

# mod_rewrite targets in the play/ and rest/ .htaccess. image.php and play/
# answer from /client/ now; /server/ and rest's own index.php did not move.
# ("cp public/play/*" skips dotfiles, so nothing else maintains these.)
for htaccess in ("/public/client/play/.htaccess.dist", "/public/rest/.htaccess.dist"):
    self_check(TARGET + htaccess,
               r"(RewriteRule\s+\S+\s+)/(?:client/)*(image\.php|play/)",
               "\\1/client/\\2")

self_check(TARGET + "/composer.json", "public/(client/)*lib", "public/client/lib")
self_check(TARGET + "/package.json", "public/(client/)*lib", "public/client/lib")
self_check(TARGET + "/locale/base/gather-messages.sh", "public/(client/)*lib", "public/client/lib")

report_stale(TARGET, SOURCE)
