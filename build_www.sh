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

# remove the builds each time
#rm -rf $AMPACHEDIR/www/ampache.org-api/build/*
rm -rf $AMPACHEDIR/www/ampache.org-docs/build/*
rm -rf $AMPACHEDIR/www/ampache.github.io/*

# rebuild and copy to the site
#cd $AMPACHEDIR/www/ampache.org-api && npm run build && cp -rfv ./build/* $AMPACHEDIR/www/ampache.github.io/api/
cd $AMPACHEDIR/www/ampache.org-docs && npm run build && cp -rfv ./build/* $AMPACHEDIR/www/ampache.github.io/

cp $AMPACHEDIR/www/ampache.org-docs/docs/api/index.md $AMPACHEDIR/ampache-develop/docs/API.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/api/api-json-methods.md $AMPACHEDIR/ampache-develop/docs/API-JSON-methods.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/api/api-xml-methods.md $AMPACHEDIR/ampache-develop/docs/API-XML-methods.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/api/api-advanced-search.md $AMPACHEDIR/ampache-develop/docs/API-advanced-search.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/api/api-errors.md $AMPACHEDIR/ampache-develop/docs/API-Errors.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/docs/configuration/acl.md $AMPACHEDIR/ampache-develop/docs/API-acls.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/api/subsonic.md $AMPACHEDIR/ampache-develop/docs/API-subsonic.md

cp $AMPACHEDIR/www/ampache.org-docs/docs/docs/development/CONTRIBUTING.md $AMPACHEDIR/ampache-develop/CONTRIBUTING.md
cp $AMPACHEDIR/www/ampache.org-docs/docs/docs/development/TRANSLATIONS.md $AMPACHEDIR/ampache-develop/locale/base/TRANSLATIONS.md

cp $AMPACHEDIR/www/ampache.org-docs/docs/docker.md $AMPACHEDIR/docker/ampache-docker/README.md

# Fix up the weirdness
sed -i'' '/^---$/,/^#/c\
# Contributing to Ampache' "$AMPACHEDIR/ampache-develop/CONTRIBUTING.md"
sed -i'' '/^---$/,/^#/c\
# API Errors' "$AMPACHEDIR/ampache-develop/docs/API-Errors.md"
sed -i'' '/^---$/,/^#/c\
# API JSON Methods' "$AMPACHEDIR/ampache-develop/docs/API-JSON-methods.md"
sed -i'' '/^---$/,/^#/c\
# API XML Methods' "$AMPACHEDIR/ampache-develop/docs/API-XML-methods.md"
sed -i'' '/^---$/,/^#/c\
# Ampache Translation Guide' "$AMPACHEDIR/ampache-develop/locale/base/TRANSLATIONS.md"
sed -i'' '/^---$/,/^#/c\
# Ampache API' "$AMPACHEDIR/ampache-develop/docs/API.md"
sed -i'' '/^---$/,/^#/c\
# Ampache Access Control Lists' "$AMPACHEDIR/ampache-develop/docs/API-acls.md"
sed -i'' '/^---$/,/^#/c\
# API Advanced Search' "$AMPACHEDIR/ampache-develop/docs/API-advanced-search.md"
sed -i'' '/^---$/,/^<\/div>$/c\
# ampache-docker\
\
Docker image for Ampache, a web based audio/video streaming application and file manager allowing you to access your music & videos from anywhere, using almost any internet enabled device.' "$AMPACHEDIR/docker/ampache-docker/README.md"
sed -i'' '/^---$/,/^#/c\
# Subsonic API Support' "$AMPACHEDIR/ampache-develop/docs/API-subsonic.md"

#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-5.md $AMPACHEDIR/ampache-master/docs/API.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-json-methods.md $AMPACHEDIR/ampache-master/docs/API-JSON-methods.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-xml-methods.md $AMPACHEDIR/ampache-master/docs/API-XML-methods.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-advanced-search.md $AMPACHEDIR/ampache-master/docs/API-advanced-search.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-5/api-errors.md $AMPACHEDIR/ampache-master/docs/API-Errors.md
#cp $AMPACHEDIR/www/ampache.org-docs/docs/api-acls.md $AMPACHEDIR/ampache-master/docs/API-acls.md
