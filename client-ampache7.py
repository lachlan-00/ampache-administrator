#!/usr/bin/env python3

"""Rewrite ampache-patch7 paths for the 'client7' layout.

build_ampache-client7.sh keeps the server endpoints where they are and pushes
the whole web UI down into public/client/, so anything under there gains one
directory level:

    public/admin|daap|rest|server|upnp|webdav/   unchanged
    public/index.php|opensearch.php              unchanged
    public/client/*.php                          was public/*.php
    public/client/images|lib|templates|themes/
    public/play/                                 sibling of public/client, but
                                                  still reached through the
                                                  /client/play/ web path

play/ is physically copied next to public/client (not nested under it) so an
existing Apache Alias for /play keeps working, but the URLs the app builds for
it still go through get_web_path('/client') - see the ROOT_ENTRIES/ROOT_URLS
split below: play/ is a ROOT_ENTRY for __DIR__ paths (it stays put on disk),
but is excluded from ROOT_URLS so its get_web_path() calls keep the /client
suffix like everything else under the web UI.

Every rewrite below is idempotent: it targets the final value instead of
nudging the current one, so re-running this on a tree that was not refreshed
from ampache-patch7 is safe. The old relative rewrites ("add one ../") did
corrupt the tree when they ran twice.

The list of files to touch is derived from ampache-patch7/public rather than
hard-coded, so new pages are picked up automatically and removed ones
(channel.php, captcha/, ...) simply stop being processed.

Usage: client-ampache7.py [source-public-dir] [target-repo]

Both default to the working copies next to this script.
"""

import codecs
import os
import re
import subprocess
import sys

SOURCE = sys.argv[1] if len(sys.argv) > 1 else "./ampache-patch7/public"
TARGET = sys.argv[2] if len(sys.argv) > 2 else "./ampache-client7"

# entries of ampache-patch7/public that stay at the web root (physically and
# in every __DIR__ path); everything else is served from public/client/.
ROOT_ENTRIES = ("admin", "daap", "play", "rest", "server", "upnp", "webdav")

# "$dic = require __DIR__ . '/../src/Config/Init.php';" and friends. The number
# of ../ is matched loosely so the correct depth can be written back over it.
INIT_FIND = r"__DIR__ \. '(?:/\.\.)*/src/Config/"

# collapse /public/, /public/client/ and the /public/client/client/ left behind
# by earlier double runs onto a single canonical value
CLIENT_FIND = r"/public/(?:client/)*"

# ...except the endpoints that stayed at the web root
ROOT_RESTORE = r"/public/client/(" + "|".join(ROOT_ENTRIES) + r")/"

# URL paths that are not served from /client/: the endpoints above (except
# play/, whose files sit next to public/client/ but whose URLs still resolve
# through the client web path - see the /play/art/ links in Art.php), plus the
# analytics plugins, which point at a separate install and never lived in the
# tree at all.
ROOT_URLS = tuple(entry for entry in ROOT_ENTRIES if entry != "play") + ("matomo", "piwik")

# undo the blanket web path suffix for those, e.g. the sse.server.php URL
ROOT_URL_RESTORE = (r"(get_web_path|getWebPath)\('/client'\) \. ([\"'])/("
                    + "|".join(ROOT_URLS) + r")/")

# the view classes in src/Gui declare their own zero-argument getWebPath(), so
# the suffix must only be added to calls - suffixing the declaration is a parse
# error that takes the whole install down.
DECLARATION_SKIP = r"(?<!function )"

# the STRUCTURE constant, matched on its final value so a re-run is a no-op
STRUCTURE_FIND = r"(const (?:string )?STRUCTURE\s*=\s*)'(?:public|client|squashed)'"

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
                if extension == ".php" or extension == ".phtml" or extension == ".json" or extension == ".sh":
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


def tracked_files(path):
    """Every path git tracks in the checkout at path, or None when it is not one."""
    try:
        result = subprocess.run(["git", "-C", path, "ls-files", "-z"],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None

    return {name for name in result.stdout.decode("utf-8").split("\0") if name}


def destination(name):
    """Where ampache-patch7/public/<name> ends up in the client layout."""
    if name in ROOT_ENTRIES:
        return os.path.join("public", name)
    if name == "play":
        return os.path.join("public", "play")
    return os.path.join("public", "client", name)


def fix_init_depth(repo, relpath):
    """Point src/Config/ requires at the real depth of the file below the repo.

    src/ always sits at the repository root, so the correct number of ../ is
    simply how deep the file ended up: two for public/admin/index.php, three
    for public/client/song.php, four for public/client/lib/javascript/
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

    report_stale_tracked(repo, source)


def upstream_path(name):
    """Where a client-layout file is expected to live in the upstream branch."""
    if name.startswith("public/client/"):
        return "public/" + name[len("public/client/"):]
    return name


def report_stale_tracked(repo, source):
    """Warn about anything else git still tracks here that upstream has dropped.

    The page sweep above only looks at .php under the web root, so images,
    javascript, dotfiles and src/ classes that were deleted upstream survive
    every rebuild unnoticed - the build only ever copies, it never deletes.
    Comparing the two indexes rather than the two working trees keeps a
    part-rebuilt tree quiet: files copied in but not committed are untracked,
    so a new upstream file is never mistaken for a stale local one.
    """
    upstream = tracked_files(os.path.dirname(os.path.abspath(source)))
    downstream = tracked_files(repo)
    if upstream is None or downstream is None:
        print("NOTE: not a git checkout, skipped the tracked-file comparison")

        return

    for name in sorted(downstream):
        if upstream_path(name) not in upstream:
            print("STALE: " + os.path.join(repo, name) + " no longer exists in " + source)


# src/ always sits at the repository root, so every page under public/ wants a
# ../ for each level it is nested, whichever side of the split it landed on.
fix_init_depth(TARGET, "public")

# AmpConfig::get('structure') is read at runtime to pick the release zip and the
# web root, and the copy from ampache-patch7 always brings 'public' with it, so
# the constant has to be written back on every rebuild.
self_check(TARGET + "/src/Config/Init/InitializationHandlerConfig.php",
           STRUCTURE_FIND,
           "\\1'client'")

self_check(TARGET + "/src", CLIENT_FIND, "/public/client/")
self_check(TARGET + "/src", ROOT_RESTORE, "/public/\\1/")
self_check(TARGET + "/src", "AmpConfig::get_web_path\\(\\)", "AmpConfig::get_web_path('/client')")
self_check(TARGET + "/src", DECLARATION_SKIP + "getWebPath\\(\\)", "getWebPath('/client')")

self_check(TARGET + "/src", ROOT_URL_RESTORE, "\\1() . \\2/\\3/")

# install_rewrite_rules() is handed the bare web root and prepends it to every
# RewriteRule target it writes. The targets in the .htaccess.dist files are
# already written relative to that root, so suffixing the argument here would
# double the /client segment on every rule.
self_check(TARGET + "/src/Module/Cli/HtaccessCommand.php",
           r"(install_rewrite_rules\([^,]+, \$this->configContainer->getWebPath)\('/client'\)",
           "\\1()")

# image.php answers from public/client/ now, but public/play/.htaccess.dist is
# a raw copy from ampache-patch7 and still targets the bare web root. The
# other rewrite targets in this file (play/...) are left alone: play/ is
# itself a sibling of public/client, so they already point at the right place.
self_check(TARGET + "/public/play/.htaccess.dist",
           r"(RewriteRule\s+\S+\s+)/(?:client/)*(image\.php)",
           "\\1/client/\\2")

# public/client/templates gained a level. Fix the repo-root paths before
# rewriting "public/", otherwise '/../../public/client/' gets counted twice.
self_check(TARGET + "/public/client/templates", ROOT_FIND, "__DIR__ . '/../../../\\1")
self_check(TARGET + "/public/client/templates", CLIENT_FIND, "/public/client/")
self_check(TARGET + "/public/client/templates", ROOT_RESTORE, "/public/\\1/")
self_check(TARGET + "/public/client/templates", "\\<img src\\=\"\\./(client/)*images/", "<img src=\"./client/images/")
self_check(TARGET + "/public/client/templates", "AmpConfig::get_web_path\\(\\)", "AmpConfig::get_web_path('/client')")
self_check(TARGET + "/public/client/templates", DECLARATION_SKIP + "getWebPath\\(\\)", "getWebPath('/client')")

self_check(TARGET + "/composer.json", "public/(client/)*lib", "public/client/lib")
self_check(TARGET + "/package.json", "public/(client/)*lib", "public/client/lib")
self_check(TARGET + "/locale/base/gather-messages.sh", "public/(client/)*lib", "public/client/lib")

report_stale(TARGET, SOURCE)
