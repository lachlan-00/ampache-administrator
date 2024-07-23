#!/bin/sh

RELEASEBRANCH="patch7"
SQUASHBRANCH="squashed7"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -d $AMPACHEDIR/ampache-patch7 ]; then
  git clone -b patch7 https://github.com/ampache/ampache.git ampache-patch7
fi
if [ ! -f $AMPACHEDIR/ampache-patch7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch7
  git clone -b patch7 https://github.com/ampache/ampache.git ampache-patch7
fi
cd $AMPACHEDIR/ampache-patch7 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch7/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

echo
echo $RELEASEVERSION
echo

if [ ! -d $AMPACHEDIR/releases ]; then
  mkdir $AMPACHEDIR/releases
fi
if [ ! -d $AMPACHEDIR/releases/7 ]; then
  mkdir $AMPACHEDIR/releases/7
fi

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi
cd $AMPACHEDIR/releases/7
if [ ! -d $AMPACHEDIR/releases/7/generic ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git generic
fi
if [ ! -d $AMPACHEDIR/releases/7/generic_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git generic_squashed
fi

if [ ! -d $AMPACHEDIR/releases/7/php82 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -f $AMPACHEDIR/releases/7/php82/index.php ]; then
  rm -rf $AMPACHEDIR/releases/7/php82
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -d $AMPACHEDIR/releases/7/php82_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi
if [ ! -f $AMPACHEDIR/releases/7/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/7/php82_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi

if [ ! -d $AMPACHEDIR/releases/7/php83 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -f $AMPACHEDIR/releases/7/php83/index.php ]; then
  rm -rf $AMPACHEDIR/releases/7/php83
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -d $AMPACHEDIR/releases/7/php83_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi
if [ ! -f $AMPACHEDIR/releases/7/php83_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/7/php83_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi

# force reset everything
cd $AMPACHEDIR/releases/7/generic && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/7/generic_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/7/php82 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/7/php82_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/7/php83 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/7/php83_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull

# GENERIC (No composer packages installed)
cd $AMPACHEDIR/releases/7/generic
rm -rf ./composer.lock ./package-lock.json vendor/* public/lib/components/*
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/7/generic_squashed
rm -rf ./composer.lock ./package-lock.json vendor/* ./lib/components/* ./docker/
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

# php 8.2
cd $AMPACHEDIR/releases/7/php82
rm -rf ./composer.lock ./package-lock.json vendor/* public/lib/components/* && php8.2 $COMPOSERPATH install
npm install
npm run build
find . -xtype l -exec rm {} \;
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
#cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/7/php82_squashed
rm -rf ./composer.lock ./package-lock.json vendor/* ./lib/components/* ./docker/ && php8.2 $COMPOSERPATH install
npm install
npm run build
find . -xtype l -exec rm {} \;
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
#cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.3
cd $AMPACHEDIR/releases/7/php83
rm -rf ./composer.lock ./package-lock.json vendor/* public/lib/components/* && php8.3 $COMPOSERPATH install
php8.3 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
#cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/7/php83_squashed
rm -rf ./composer.lock ./package-lock.json vendor/* ./lib/components/* ./docker/ && php8.3 $COMPOSERPATH install
php8.3 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
#cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# remove possible old release files before building the new one
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.3.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.3.zip
fi

# Build Releases

## GENERIC
cd $AMPACHEDIR/releases/7/generic && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../../ampache-${RELEASEVERSION}_public.zip ./
cd $AMPACHEDIR/releases/7/generic_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_squashed.zip ./ ./

## php 8.2
cd $AMPACHEDIR/releases/7/php82 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../..//ampache-${RELEASEVERSION}_all_php8.2.zip ./
cd $AMPACHEDIR/releases/7/php82_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php8.2.zip ./

## php 8.3
cd $AMPACHEDIR/releases/7/php83 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../..//ampache-${RELEASEVERSION}_all_php8.3.zip ./
cd $AMPACHEDIR/releases/7/php83_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php8.3.zip ./

# go back
cd $AMPACHEDIR

if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.3.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.3.zip
fi


cd $AMPACHEDIR/releases
# echo the version checksum
echo
echo "# ${RELEASEVERSION}"
echo
echo "php8.3"
md5sum ./ampache-${RELEASEVERSION}_all_php8.3.zip
md5sum ./ampache-${RELEASEVERSION}_all_squashed_php8.3.zip
echo
echo "php8.2"
md5sum ./ampache-${RELEASEVERSION}_all_php8.2.zip
md5sum ./ampache-${RELEASEVERSION}_all_squashed_php8.2.zip
echo
echo "**UNSUPPORTED** Code only release. (Requires composer install)"
md5sum ./ampache-${RELEASEVERSION}_public.zip
md5sum ./ampache-${RELEASEVERSION}_squashed.zip
echo
echo
echo

# go home
cd $AMPACHEDIR

