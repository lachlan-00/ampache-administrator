#!/bin/sh

RELEASEBRANCH="patch6"
SQUASHBRANCH="squashed6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"
LOCALIP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch6/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

# php7.4
if [ ! -d $AMPACHEDIR/release-test/php74 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip -d /$AMPACHEDIR/release-test/php74
fi
if [ -f $AMPACHEDIR/release-test/php74/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php74/*
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip -d /$AMPACHEDIR/release-test/php74
fi
if [ ! -d $AMPACHEDIR/release-test/php74_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip -d /$AMPACHEDIR/release-test/php74_squashed
fi
if [ -f $AMPACHEDIR/release-test/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php74_squashed/*
  rm $AMPACHEDIR/release-test/php74_squashed/.maintenance.example
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip -d /$AMPACHEDIR/release-test/php74_squashed
fi

# php8.0
if [ ! -d $AMPACHEDIR/release-test/php80 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip -d /$AMPACHEDIR/release-test/php80
fi
if [ -f $AMPACHEDIR/release-test/php80/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php80/*
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip -d /$AMPACHEDIR/release-test/php80
fi
if [ ! -d $AMPACHEDIR/release-test/php80_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip -d /$AMPACHEDIR/release-test/php80_squashed
fi
if [ -f $AMPACHEDIR/release-test/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php80_squashed/*
  rm $AMPACHEDIR/release-test/php80_squashed/.maintenance.example
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip -d /$AMPACHEDIR/release-test/php80_squashed
fi

# php8.1
if [ ! -d $AMPACHEDIR/release-test/php81 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip -d /$AMPACHEDIR/release-test/php81
fi
if [ -f $AMPACHEDIR/release-test/php81/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php81/*
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip -d /$AMPACHEDIR/release-test/php81
fi
if [ ! -d $AMPACHEDIR/release-test/php81_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip -d /$AMPACHEDIR/release-test/php81_squashed
fi
if [ -f $AMPACHEDIR/release-test/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php81_squashed/*
  rm $AMPACHEDIR/release-test/php81_squashed/.maintenance.example
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip -d /$AMPACHEDIR/release-test/php81_squashed
fi

# php8.2
if [ ! -d $AMPACHEDIR/release-test/php82 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d /$AMPACHEDIR/release-test/php82
fi
if [ -f $AMPACHEDIR/release-test/php82/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php82/*
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d /$AMPACHEDIR/release-test/php82
fi
if [ ! -d $AMPACHEDIR/release-test/php82_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d /$AMPACHEDIR/release-test/php82_squashed
fi
if [ -f $AMPACHEDIR/release-test/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php82_squashed/*
  rm $AMPACHEDIR/release-test/php82_squashed/.maintenance.example
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d /$AMPACHEDIR/release-test/php82_squashed
fi

# reset perms

# php7.4
chown $UID:33 $AMPACHEDIR/release-test/php74/composer.json 
chmod 775 $AMPACHEDIR/release-test/php74/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php74/config
chmod -R 775 $AMPACHEDIR/release-test/php74/config
chown -R $UID:33 $AMPACHEDIR/release-test/php74/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php74/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php74/public/
chmod -R 775 $AMPACHEDIR/release-test/php74/public/

chown $UID:33 $AMPACHEDIR/release-test/php74_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php74_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php74_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php74_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php74_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php74_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php74_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php74_squashed/

# php8.0
chown $UID:33 $AMPACHEDIR/release-test/php80/composer.json 
chmod 775 $AMPACHEDIR/release-test/php80/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php80/config
chmod -R 775 $AMPACHEDIR/release-test/php80/config
chown -R $UID:33 $AMPACHEDIR/release-test/php80/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php80/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php80/public/
chmod -R 775 $AMPACHEDIR/release-test/php80/public/

chown $UID:33 $AMPACHEDIR/release-test/php80_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php80_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php80_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php80_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php80_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php80_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php80_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php80_squashed/

# php8.1
chown $UID:33 $AMPACHEDIR/release-test/php81/composer.json 
chmod 775 $AMPACHEDIR/release-test/php81/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php81/config
chmod -R 775 $AMPACHEDIR/release-test/php81/config
chown -R $UID:33 $AMPACHEDIR/release-test/php81/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php81/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php81/public/
chmod -R 775 $AMPACHEDIR/release-test/php81/public/

chown $UID:33 $AMPACHEDIR/release-test/php81_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php81_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php81_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php81_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php81_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php81_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php81_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php81_squashed/

# php8.2
chown $UID:33 $AMPACHEDIR/release-test/php82/composer.json 
chmod 775 $AMPACHEDIR/release-test/php82/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php82/config
chmod -R 775 $AMPACHEDIR/release-test/php82/config
chown -R $UID:33 $AMPACHEDIR/release-test/php82/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php82/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php82/public/
chmod -R 775 $AMPACHEDIR/release-test/php82/public/

chown $UID:33 $AMPACHEDIR/release-test/php82_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php82_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/

chown $UID:33 $AMPACHEDIR/release-test/php74
chmod 775 $AMPACHEDIR/release-test/php74
chown $UID:33 $AMPACHEDIR/release-test/php74_squashed
chmod 775 $AMPACHEDIR/release-test/php74_squashed
chown $UID:33 $AMPACHEDIR/release-test/php80
chmod 775 $AMPACHEDIR/release-test/php80
chown $UID:33 $AMPACHEDIR/release-test/php80_squashed
chmod 775 $AMPACHEDIR/release-test/php80_squashed
chown $UID:33 $AMPACHEDIR/release-test/php81
chmod 775 $AMPACHEDIR/release-test/php81
chown $UID:33 $AMPACHEDIR/release-test/php81_squashed
chmod 775 $AMPACHEDIR/release-test/php81_squashed
chown $UID:33 $AMPACHEDIR/release-test/php82
chmod 775 $AMPACHEDIR/release-test/php82
chown $UID:33 $AMPACHEDIR/release-test/php82_squashed
chmod 775 $AMPACHEDIR/release-test/php82_squashed

# copy test config back
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php74/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php74_squashed/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php80/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php80_squashed/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php81/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php81_squashed/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php82/config/
cp $AMPACHEDIR/release-test/ampache.cfg.php $AMPACHEDIR/release-test/php82_squashed/config/

sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php74/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php74_squashed/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php80/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php80_squashed/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php81/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php81_squashed/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/database_hostname = \"localhost\"/database_hostname = \"$LOCALIP\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php

# ReLaunch all the containers

docker-compose down -V
docker-compose -p "release-test" -f docker/test-docker-compose74.yml -f docker/test-docker-compose74_squashed.yml -f docker/test-docker-compose80.yml -f docker/test-docker-compose80_squashed.yml -f docker/test-docker-compose81.yml -f docker/test-docker-compose81_squashed.yml -f docker/test-docker-compose82.yml -f docker/test-docker-compose82_squashed.yml up -d --build

echo "Testing $RELEASEVERSION"

