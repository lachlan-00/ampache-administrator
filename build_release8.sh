#!/bin/sh

RELEASEBRANCH="patch8"
SQUASHBRANCH="squashed8"
CLIENTBRANCH="client8"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

# Ampache 8 requires PHP 8.5+ (composer.json "php": ">=8.5") so there are no 8.2/8.3/8.4 builds.
ZIPEXCLUDE="--exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./node_modules/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml"
ZIPEXCLUDEPUBLIC="--exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess"
ZIPEXCLUDESQUASHED="--exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess"

if [ ! -d $AMPACHEDIR/ampache-patch8 ]; then
  git clone -b patch8 https://github.com/ampache/ampache.git ampache-patch8
fi
if [ ! -f $AMPACHEDIR/ampache-patch8/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch8
  git clone -b patch8 https://github.com/ampache/ampache.git ampache-patch8
fi
cd $AMPACHEDIR/ampache-patch8 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch8/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

echo
echo $RELEASEVERSION
echo

if [ ! -d $AMPACHEDIR/releases ]; then
  mkdir $AMPACHEDIR/releases
fi
if [ ! -d $AMPACHEDIR/releases/8 ]; then
  mkdir $AMPACHEDIR/releases/8
fi

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi
cd $AMPACHEDIR/releases/8
if [ ! -d $AMPACHEDIR/releases/8/generic ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git generic
fi
if [ ! -d $AMPACHEDIR/releases/8/generic_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git generic_squashed
fi
if [ ! -d $AMPACHEDIR/releases/8/generic_client ]; then
  git clone -b $CLIENTBRANCH https://github.com/ampache/ampache.git generic_client
fi

if [ ! -d $AMPACHEDIR/releases/8/php85 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php85
fi
if [ ! -f $AMPACHEDIR/releases/8/php85/index.php ]; then
  rm -rf $AMPACHEDIR/releases/8/php85
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php85
fi
if [ ! -d $AMPACHEDIR/releases/8/php85_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php85_squashed
fi
if [ ! -f $AMPACHEDIR/releases/8/php85_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/8/php85_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php85_squashed
fi
if [ ! -d $AMPACHEDIR/releases/8/php85_client ]; then
  git clone -b $CLIENTBRANCH https://github.com/ampache/ampache.git php85_client
fi
if [ ! -f $AMPACHEDIR/releases/8/php85_client/index.php ]; then
  rm -rf $AMPACHEDIR/releases/8/php85_client
  git clone -b $CLIENTBRANCH https://github.com/ampache/ampache.git php85_client
fi

# force reset everything
cd $AMPACHEDIR/releases/8/generic && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/8/generic_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/8/generic_client && git fetch origin $CLIENTBRANCH && git checkout -f $CLIENTBRANCH && git reset --hard origin/$CLIENTBRANCH && git pull
cd $AMPACHEDIR/releases/8/php85 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/8/php85_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/8/php85_client && git fetch origin $CLIENTBRANCH && git checkout -f $CLIENTBRANCH && git reset --hard origin/$CLIENTBRANCH && git pull

# GENERIC (No composer packages installed)
cd $AMPACHEDIR/releases/8/generic
rm -rf vendor/* public/lib/components/*
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/8/generic_squashed
rm -rf vendor/* ./lib/components/* ./docker/
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/8/generic_client
rm -rf vendor/* public/client/lib/components/*
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

# php 8.5
cd $AMPACHEDIR/releases/8/php85
rm -rf vendor/* public/lib/components/*
php8.5 $COMPOSERPATH install --no-dev || exit 1
npm install || exit 1
npm run build || exit 1
npm run minify || exit 1
git diff --quiet -- '*jplayer*' || { echo "ERROR: committed jplayer minified files were stale in php85"; exit 1; }
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/8/php85_squashed
rm -rf vendor/* ./lib/components/* ./docker/
php8.5 $COMPOSERPATH install --no-dev || exit 1
npm install || exit 1
npm run build || exit 1
npm run minify || exit 1
git diff --quiet -- '*jplayer*' || { echo "ERROR: committed jplayer minified files were stale in php85_squashed"; exit 1; }
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/8/php85_client
rm -rf vendor/* public/client/lib/components/*
php8.5 $COMPOSERPATH install --no-dev || exit 1
npm install || exit 1
npm run build || exit 1
npm run minify || exit 1
git diff --quiet -- '*jplayer*' || { echo "ERROR: committed jplayer minified files were stale in php85_client"; exit 1; }
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

# remove possible old release files before building the new one
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_client.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_client.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_squashed.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_squashed.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_client.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_client.zip
fi

# Build Releases

## GENERIC
cd $AMPACHEDIR/releases/8/generic && zip -r -q -u -9 $ZIPEXCLUDE $ZIPEXCLUDEPUBLIC ./../../ampache-${RELEASEVERSION}_public.zip ./
cd $AMPACHEDIR/releases/8/generic_squashed && zip -r -q -u -9 $ZIPEXCLUDE $ZIPEXCLUDESQUASHED ./../../ampache-${RELEASEVERSION}_squashed.zip ./
cd $AMPACHEDIR/releases/8/generic_client && zip -r -q -u -9 $ZIPEXCLUDE $ZIPEXCLUDEPUBLIC ./../../ampache-${RELEASEVERSION}_client.zip ./

## php 8.5
cd $AMPACHEDIR/releases/8/php85 && zip -r -q -u -9 $ZIPEXCLUDE $ZIPEXCLUDEPUBLIC ./../../ampache-${RELEASEVERSION}_all_php8.5.zip ./
cd $AMPACHEDIR/releases/8/php85_squashed && zip -r -q -u -9 $ZIPEXCLUDE $ZIPEXCLUDESQUASHED ./../../ampache-${RELEASEVERSION}_all_php8.5_squashed.zip ./
cd $AMPACHEDIR/releases/8/php85_client && zip -r -q -u -9 $ZIPEXCLUDE $ZIPEXCLUDEPUBLIC ./../../ampache-${RELEASEVERSION}_all_php8.5_client.zip ./

# go back
cd $AMPACHEDIR

if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_client.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_client.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_squashed.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_squashed.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_client.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.5_client.zip
fi

cd $AMPACHEDIR/releases
# echo the version checksum
echo
echo "# ${RELEASEVERSION}"
echo
echo "php8.5"
md5sum ./ampache-${RELEASEVERSION}_all_php8.5.zip
md5sum ./ampache-${RELEASEVERSION}_all_php8.5_squashed.zip
md5sum ./ampache-${RELEASEVERSION}_all_php8.5_client.zip
echo
echo "**UNSUPPORTED** Code only release. (Requires composer and npm install)"
md5sum ./ampache-${RELEASEVERSION}_public.zip
md5sum ./ampache-${RELEASEVERSION}_squashed.zip
md5sum ./ampache-${RELEASEVERSION}_client.zip
echo
echo "## Zip Version information"
echo
echo "If you aren't familiar which the project make sure you know [which zip](https://ampache.org/docs/information/which-zip) you need to download."
echo

# go home
cd $AMPACHEDIR

