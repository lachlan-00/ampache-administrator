#!/bin/sh

AMPACHEDIR=$PWD

if [ ! -d $AMPACHEDIR/ampache-develop ]; then
  git clone -b develop https://github.com/ampache/ampache.git ampache-develop
fi
if [ ! -f $AMPACHEDIR/ampache-develop/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-develop
  git clone -b develop https://github.com/ampache/ampache.git ampache-develop
fi
#if [ ! -d $AMPACHEDIR/ampache-master ]; then
#  git clone -b master https://github.com/ampache/ampache.git ampache-master
#fi
#if [ ! -f $AMPACHEDIR/ampache-master/index.php ]; then
#  rm -rf $AMPACHEDIR/ampache-master
#  git clone -b master https://github.com/ampache/ampache.git ampache-master
#fi
if [ ! -d $AMPACHEDIR/docker/ampache-docker ]; then
  cd $AMPACHEDIR/docker && git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
fi

if [ ! -d $AMPACHEDIR/www ]; then
  mkdir $AMPACHEDIR/www
fi
#if [ ! -d $AMPACHEDIR/www/ampache.org-api ]; then
#  cd $AMPACHEDIR/www && git clone https://github.com/ampache/ampache.org-api.git ampache.org-api
#fi
#if [ ! -d $AMPACHEDIR/www/ampache.org-api ]; then
#  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.org-api.git ampache.org-api
#fi
if [ ! -d $AMPACHEDIR/www/ampache.org-docs ]; then
  cd $AMPACHEDIR/www && git clone https://github.com/ampache/ampache.org-docs.git ampache.org-docs
fi
if [ ! -d $AMPACHEDIR/www/ampache.org-docs ]; then
  cd $AMPACHEDIR/www && git clone -b main https://github.com/ampache/ampache.org-docs.git ampache.org-docs
fi
if [ ! -d $AMPACHEDIR/www/ampache.github.io ]; then
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi
if [ ! -f $AMPACHEDIR/www/ampache.github.io/index.html ] && [ ! -f $AMPACHEDIR/www/ampache.github.io/old/index.html ]; then
  rm -rf $AMPACHEDIR/www/ampache.github.io
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi
if [ ! -f $AMPACHEDIR/www/ampache.github.io/index.html ] && [ ! -f $AMPACHEDIR/www/ampache.github.io/old/index.html ]; then
  rm -rf $AMPACHEDIR/www/ampache.github.io
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi

#cd $AMPACHEDIR/ampache-master && git pull
cd $AMPACHEDIR/ampache-develop && git pull

cd $AMPACHEDIR/www/ampache.github.io && git pull
#cd $AMPACHEDIR/www/ampache.org-api && git pull
cd $AMPACHEDIR/www/ampache.org-docs && git pull

#if [ -d $AMPACHEDIR/www/ampache.github.io ] && [ ! -d $AMPACHEDIR/www/ampache.github.io/api ]; then
#  mkdir $AMPACHEDIR/www/ampache.github.io/api
#fi
#if [ -d $AMPACHEDIR/www/ampache.github.io ] && [ ! -d $AMPACHEDIR/www/ampache.github.io/docs ]; then
#  mkdir $AMPACHEDIR/www/ampache.github.io/docs
#fi

DOCSCHANGED=0
SIDEBARS=$AMPACHEDIR/www/ampache.org-docs/sidebars.js

# Copy a document owned by ampache-develop into the docs site, keeping the docusaurus frontmatter the site page has.
# $1 path in ampache-develop, $2 path in ampache.org-docs, $3 what to do with the leading "# Title": demote|drop
copy_doc() {
  src="$AMPACHEDIR/ampache-develop/$1"
  dest="$AMPACHEDIR/www/ampache.org-docs/$2"

  if [ ! -f "$src" ]; then
    echo "SKIPPED $2 (ampache-develop has no $1)"
    return
  fi
  if [ ! -f "$dest" ]; then
    echo "SKIPPED $2 (no page to take the frontmatter from, create it first)"
    return
  fi
  if [ "$(head -n 1 "$dest")" != "---" ]; then
    echo "SKIPPED $2 (no docusaurus frontmatter)"
    return
  fi

  awk '{ print } /^---$/ { if (++dashes == 2) exit }' "$dest" > "$dest.new"
  printf '\n' >> "$dest.new"
  awk -v mode="$3" '
    NR == 1 && /^# / {
      if (mode == "demote") { printf "#%s\n\n", $0 }
      skipblank = 1
      next
    }
    skipblank == 1 && $0 == "" { skipblank = 0; next }
    { skipblank = 0; print }
  ' "$src" >> "$dest.new"

  # links between repo documents have to become site links or docusaurus fails the build on them
  sed -i'' \
    -e 's|](API\.md#|](/api/#|g' \
    -e 's|](API\.md)|](/api/)|g' \
    -e 's|](AGENTS\.md)|](https://github.com/ampache/ampache/blob/develop/AGENTS.md)|g' \
    "$dest.new"

  if grep -qE '\]\([^):/]*\.md[)#]' "$dest.new"; then
    echo "CHECK $2 (still links to a repo file, add the rewrite to copy_doc before you build)"
  fi

  if cmp -s "$dest.new" "$dest"; then
    rm -f "$dest.new"
  else
    mv "$dest.new" "$dest"
    echo "UPDATED $2"
    DOCSCHANGED=1
  fi
}

# Copy a generated file (the openapi specs) into the docs site as-is
copy_file() {
  src="$AMPACHEDIR/ampache-develop/$1"
  dest="$AMPACHEDIR/www/ampache.org-docs/$2"

  if [ ! -f "$src" ]; then
    echo "SKIPPED $2 (ampache-develop has no $1)"
    return
  fi
  if cmp -s "$src" "$dest"; then
    return
  fi

  cp "$src" "$dest"
  echo "UPDATED $2"
  DOCSCHANGED=1
}

# Put a doc id into the "Browse Methods" category in sidebars.js, or docusaurus warns the page is orphaned.
# $1 the doc id, e.g. api/browse/song-browse
add_browse_sidebar() {
  if grep -q "'$1'" "$SIDEBARS"; then
    return
  fi

  awk -v entry="$1" -v q="'" '
    $0 ~ /id: .api\/api-browse.\}/ { inbrowse = 1 }
    inbrowse == 1 && /^ *\],$/ {
      printf "            %s%s%s,\n", q, entry, q
      inbrowse = 2
    }
    { print }
  ' "$SIDEBARS" > "$SIDEBARS.new"

  mv "$SIDEBARS.new" "$SIDEBARS"
  echo "ADDED $1 to sidebars.js"
  DOCSCHANGED=1
}

# ampache-develop owns these documents; the site gets a copy before it builds, never the other way around.
# docs/API-JSON-methods.md, docs/API-XML-methods.md and the openapi specs come from `composer api:docs`.
copy_doc docs/API.md docs/api/index.md demote
copy_doc docs/API-JSON-methods.md docs/api/api-json-methods.md demote
copy_doc docs/API-XML-methods.md docs/api/api-xml-methods.md demote
copy_doc docs/API-advanced-search.md docs/api/api-advanced-search.md demote
copy_doc docs/API-Errors.md docs/api/api-errors.md drop
copy_doc docs/API-subsonic.md docs/api/subsonic.md demote
copy_doc docs/CHANGELOG-API.md docs/api/api-changelog.md drop
copy_doc docs/API-acls.md docs/docs/configuration/acl.md demote
copy_doc docs/OIDC.md docs/docs/configuration/oidc.md drop
#copy_doc CONTRIBUTING.md docs/docs/development/CONTRIBUTING.md demote
copy_doc locale/base/TRANSLATIONS.md docs/docs/development/TRANSLATIONS.md demote

copy_doc docs/API-browse.md docs/api/api-browse.md demote

# The per-type browse pages are generated by `composer api:docs` (generate_browse_docs.py), so a new
# browse type arrives here on its own. Give it a page and a sidebar entry so the build picks it up
# without any hand work on the site side.
for browsedoc in $AMPACHEDIR/ampache-develop/docs/browse/*-browse.md; do
  [ -f "$browsedoc" ] || continue
  browsename=`basename "$browsedoc"`
  dest="$AMPACHEDIR/www/ampache.org-docs/docs/api/browse/$browsename"

  if [ ! -f "$dest" ]; then
    # the generator writes "# Album Disk Browse" as line 1, which is the title the site wants too
    browsetitle=`sed -n '1s/^# //p' "$browsedoc"`
    [ -n "$browsetitle" ] || browsetitle="Browse"
    mkdir -p "$AMPACHEDIR/www/ampache.org-docs/docs/api/browse"
    printf -- '---\ntitle: "%s"\nmetaTitle: "%s"\ndescription: "API documentation"\n---\n' \
      "$browsetitle" "$browsetitle" > "$dest"
    echo "CREATED docs/api/browse/$browsename"
    DOCSCHANGED=1
  fi

  add_browse_sidebar "api/browse/${browsename%.md}"
  copy_doc "docs/browse/$browsename" "docs/api/browse/$browsename" demote
done

# a browse type that ampache-develop drops has to come off the site by hand, deleting a published
# page is not something a build should do on its own
for sitedoc in $AMPACHEDIR/www/ampache.org-docs/docs/api/browse/*-browse.md; do
  [ -f "$sitedoc" ] || continue
  browsename=`basename "$sitedoc"`
  if [ ! -f "$AMPACHEDIR/ampache-develop/docs/browse/$browsename" ]; then
    echo "CHECK docs/api/browse/$browsename (ampache-develop no longer has this browse, remove the page and its sidebars.js entry)"
  fi
done

copy_file docs/openapi.json static/openapi.json
copy_file docs/openapi-6.json static/openapi-6.json

if [ "$DOCSCHANGED" = "1" ]; then
  echo "ampache.org-docs has uncommitted changes from ampache-develop, commit them so the deployed site keeps them"
fi

# remove the builds each time
#rm -rf $AMPACHEDIR/www/ampache.org-api/build/*
rm -rf $AMPACHEDIR/www/ampache.org-docs/build/*
rm -rf $AMPACHEDIR/www/ampache.github.io/*

# rebuild and copy to the site
#cd $AMPACHEDIR/www/ampache.org-api && npm run build && cp -rfv ./build/* $AMPACHEDIR/www/ampache.github.io/api/
cd $AMPACHEDIR/www/ampache.org-docs && npm run build && cp -rfv ./build/* $AMPACHEDIR/www/ampache.github.io/

# the docker readme is the one document the site owns, so it still goes out from here
cp $AMPACHEDIR/www/ampache.org-docs/docs/docker.md $AMPACHEDIR/docker/ampache-docker/README.md

sed -i'' '/^---$/,/^<\/div>$/c\
# ampache-docker\
\
Docker image for Ampache, a web based audio/video streaming application and file manager allowing you to access your music & videos from anywhere, using almost any internet enabled device.' "$AMPACHEDIR/docker/ampache-docker/README.md"

#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-5.md $AMPACHEDIR/ampache-master/docs/API.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-json-methods.md $AMPACHEDIR/ampache-master/docs/API-JSON-methods.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-xml-methods.md $AMPACHEDIR/ampache-master/docs/API-XML-methods.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-advanced-search.md $AMPACHEDIR/ampache-master/docs/API-advanced-search.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-errors.md $AMPACHEDIR/ampache-master/docs/API-Errors.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-acls.md $AMPACHEDIR/ampache-master/docs/API-acls.md
