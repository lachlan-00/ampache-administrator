#!/bin/sh

RELEASEBRANCH="patch6"
SQUASHBRANCH="squashed6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -d $AMPACHEDIR/ampache-patch6 ]; then
  git clone -b patch6 https://github.com/ampache/ampache.git ampache-patch6
fi
if [ ! -f $AMPACHEDIR/ampache-patch6/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch6
  git clone -b patch6 https://github.com/ampache/ampache.git ampache-patch6
fi
cd $AMPACHEDIR/ampache-patch6 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch6/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

echo
echo $RELEASEVERSION
echo

if [ ! -d $AMPACHEDIR/releases ]; then
  mkdir $AMPACHEDIR/releases
fi
if [ ! -d $AMPACHEDIR/releases/6 ]; then
  mkdir $AMPACHEDIR/releases/6
fi

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi
cd $AMPACHEDIR/releases/6
if [ ! -d $AMPACHEDIR/releases/6/generic ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git generic
fi
if [ ! -d $AMPACHEDIR/releases/6/generic_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git generic_squashed
fi
if [ ! -d $AMPACHEDIR/releases/6/php74 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php74
fi
if [ ! -f $AMPACHEDIR/releases/6/php74/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php74
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php74
fi
if [ ! -d $AMPACHEDIR/releases/6/php74_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php74_squashed
fi
if [ ! -f $AMPACHEDIR/releases/6/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php74_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php74_squashed
fi

if [ ! -d $AMPACHEDIR/releases/6/php80 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php80
fi
if [ ! -f $AMPACHEDIR/releases/6/php80/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php80
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php80
fi
if [ ! -d $AMPACHEDIR/releases/6/php80_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php80_squashed
fi
if [ ! -f $AMPACHEDIR/releases/6/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php80_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php80_squashed
fi

if [ ! -d $AMPACHEDIR/releases/6/php81 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php81
fi
if [ ! -f $AMPACHEDIR/releases/6/php81/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php81
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php81
fi
if [ ! -d $AMPACHEDIR/releases/6/php81_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php81_squashed
fi
if [ ! -f $AMPACHEDIR/releases/6/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php81_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php81_squashed
fi

if [ ! -d $AMPACHEDIR/releases/6/php82 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -f $AMPACHEDIR/releases/6/php82/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php82
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -d $AMPACHEDIR/releases/6/php82_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi
if [ ! -f $AMPACHEDIR/releases/6/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php82_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi

if [ ! -d $AMPACHEDIR/releases/6/php83 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -f $AMPACHEDIR/releases/6/php83/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php83
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -d $AMPACHEDIR/releases/6/php83_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi
if [ ! -f $AMPACHEDIR/releases/6/php83_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/releases/6/php83_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi

# force reset everything
cd $AMPACHEDIR/releases/6/generic && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/6/generic_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/6/php74 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/6/php74_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/6/php80 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/6/php80_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/6/php81 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/6/php81_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/6/php82 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/6/php82_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cd $AMPACHEDIR/releases/6/php83 && git fetch origin $RELEASEBRANCH && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cd $AMPACHEDIR/releases/6/php83_squashed && git fetch origin $SQUASHBRANCH && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull

# GENERIC (No composer packages installed)
cd $AMPACHEDIR/releases/6/generic
rm -rf ./composer.lock vendor/* public/lib/components/*
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/6/generic_squashed
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/
find . -xtype l -exec rm {} \;
find . -name "*.map.1" -exec rm {} \;

# php 7.4
cd $AMPACHEDIR/releases/6/php74
cp -f $AMPACHEDIR/extras/composer_old.json ./composer.json
rm ./composer_old.json
rm -rf ./composer.lock vendor/* public/lib/components/* && php7.4 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/6/php74_squashed
cp -f $AMPACHEDIR/extras/composer_old_squashed.json ./composer.json
rm ./composer_old.json
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/ && php7.4 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.0
cd $AMPACHEDIR/releases/6/php80
cp -f $AMPACHEDIR/extras/composer_old.json ./composer.json
rm ./composer_old.json
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.0 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/6/php80_squashed
cp -f $AMPACHEDIR/extras/composer_old_squashed.json ./composer.json
rm ./composer_old.json
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/ && php8.0 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.1
cd $AMPACHEDIR/releases/6/php81
cp -f $AMPACHEDIR/extras/composer_old.json ./composer.json
rm ./composer_old.json
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.1 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/6/php81_squashed
cp -f $AMPACHEDIR/extras/composer_old_squashed.json ./composer.json
rm ./composer_old.json
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/ && php8.1 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.2
cd $AMPACHEDIR/releases/6/php82
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.2 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/6/php82_squashed
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/ && php8.2 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.3
cd $AMPACHEDIR/releases/6/php83
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.3 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/releases/6/php83_squashed
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/ && php8.3 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
#cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# remove possible old release files before building the new one
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip
fi
if [ -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip ]; then
  rm $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip
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
cd $AMPACHEDIR/releases/6/generic && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../../ampache-${RELEASEVERSION}_public.zip ./
cd $AMPACHEDIR/releases/6/generic_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_squashed.zip ./ ./

## php 7.4
cd $AMPACHEDIR/releases/6/php74 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_php7.4.zip ./
cd $AMPACHEDIR/releases/6/php74_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php7.4.zip ./ ./

## php 8.0
cd $AMPACHEDIR/releases/6/php80 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_php8.0.zip ./
cd $AMPACHEDIR/releases/6/php80_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php8.0.zip ./

## php 8.1
cd $AMPACHEDIR/releases/6/php81 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_php8.1.zip ./
cd $AMPACHEDIR/releases/6/php81_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php8.1.zip ./

## php 8.2
cd $AMPACHEDIR/releases/6/php82 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../..//ampache-${RELEASEVERSION}_all_php8.2.zip ./
cd $AMPACHEDIR/releases/6/php82_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php8.2.zip ./

## php 8.3
cd $AMPACHEDIR/releases/6/php83 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess ./../..//ampache-${RELEASEVERSION}_all_php8.3.zip ./
cd $AMPACHEDIR/releases/6/php83_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess ./../../ampache-${RELEASEVERSION}_all_squashed_php8.3.zip ./

# go back
cd $AMPACHEDIR

if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_public.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_squashed.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip
fi
if [ ! -f $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip ]; then
  echo "ERROR " $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip
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

# Copy back the default composer after updates
cd $AMPACHEDIR/releases/6/php74
cp -f $AMPACHEDIR/extras/composer_php8.2.json ./composer.json
cd $AMPACHEDIR/releases/6/php74_squashed
cp -f $AMPACHEDIR/extras/composer_php8.2_squashed.json ./composer.json
cd $AMPACHEDIR/releases/6/php80
cp -f $AMPACHEDIR/extras/composer_php8.2.json ./composer.json
cd $AMPACHEDIR/releases/6/php80_squashed
cp -f $AMPACHEDIR/extras/composer_php8.2_squashed.json ./composer.json
cd $AMPACHEDIR/releases/6/php81
cp -f $AMPACHEDIR/extras/composer_php8.2.json ./composer.json
cd $AMPACHEDIR/releases/6/php81_squashed
cp -f $AMPACHEDIR/extras/composer_php8.2_squashed.json ./composer.json

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
echo "php8.1"
md5sum ./ampache-${RELEASEVERSION}_all_php8.1.zip
md5sum ./ampache-${RELEASEVERSION}_all_squashed_php8.1.zip
echo
echo "php8.0"
md5sum ./ampache-${RELEASEVERSION}_all_php8.0.zip
md5sum ./ampache-${RELEASEVERSION}_all_squashed_php8.0.zip
echo
echo "**UNSUPPORTED** php7.4 (_will be built until it can't be done any more_)"
md5sum ./ampache-${RELEASEVERSION}_all_php7.4.zip
md5sum ./ampache-${RELEASEVERSION}_all_squashed_php7.4.zip
echo
echo "**UNSUPPORTED** Code only release. (Requires composer install)"
md5sum ./ampache-${RELEASEVERSION}_public.zip
md5sum ./ampache-${RELEASEVERSION}_squashed.zip
echo
echo
echo

# go home
cd $AMPACHEDIR

