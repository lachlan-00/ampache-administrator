#!/bin/sh

RELEASEBRANCH="patch6"
SQUASHBRANCH="squashed6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

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
  rm -rf $AMPACHEDIR/release-test/php74
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip -d /$AMPACHEDIR/release-test/php74
fi
if [ ! -d $AMPACHEDIR/release-test/php74_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip -d /$AMPACHEDIR/release-test/php74_squashed
fi
if [ -f $AMPACHEDIR/release-test/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php74_squashed
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip -d /$AMPACHEDIR/release-test/php74_squashed
fi

# php8.0
if [ ! -d $AMPACHEDIR/release-test/php80 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip -d /$AMPACHEDIR/release-test/php80
fi
if [ -f $AMPACHEDIR/release-test/php80/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php80
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip -d /$AMPACHEDIR/release-test/php80
fi
if [ ! -d $AMPACHEDIR/release-test/php80_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip -d /$AMPACHEDIR/release-test/php80_squashed
fi
if [ -f $AMPACHEDIR/release-test/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php80_squashed
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip -d /$AMPACHEDIR/release-test/php80_squashed
fi

# php8.1
if [ ! -d $AMPACHEDIR/release-test/php81 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip -d /$AMPACHEDIR/release-test/php81
fi
if [ -f $AMPACHEDIR/release-test/php81/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php81
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip -d /$AMPACHEDIR/release-test/php81
fi
if [ ! -d $AMPACHEDIR/release-test/php81_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip -d /$AMPACHEDIR/release-test/php81_squashed
fi
if [ -f $AMPACHEDIR/release-test/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php81_squashed
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip -d /$AMPACHEDIR/release-test/php81_squashed
fi

# php8.2
if [ ! -d $AMPACHEDIR/release-test/php82 ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d /$AMPACHEDIR/release-test/php82
fi
if [ -f $AMPACHEDIR/release-test/php82/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php82
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d /$AMPACHEDIR/release-test/php82
fi
if [ ! -d $AMPACHEDIR/release-test/php82_squashed ]; then
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d /$AMPACHEDIR/release-test/php82_squashed
fi
if [ -f $AMPACHEDIR/release-test/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/release-test/php82_squashed
  unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d /$AMPACHEDIR/release-test/php82_squashed
fi

# Launch all the containers
docker-compose -p "release-test" -f docker/test-docker-compose74.yml -f docker/test-docker-compose74_squashed.yml -f docker/test-docker-compose80.yml -f docker/test-docker-compose80_squashed.yml -f docker/test-docker-compose81.yml -f docker/test-docker-compose81_squashed.yml -f docker/test-docker-compose82.yml -f docker/test-docker-compose82_squashed.yml up -d --build

echo "Testing $RELEASEVERSION"

