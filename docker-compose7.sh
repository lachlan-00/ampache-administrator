#!/bin/sh

RELEASEBRANCH="patch7"
SQUASHBRANCH="squashed7"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

# php8.2
if [ ! -d $AMPACHEDIR/php82 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -f $AMPACHEDIR/php82/index.php ]; then
  rm -rf $AMPACHEDIR/php82
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -d $AMPACHEDIR/php82_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi
if [ ! -f $AMPACHEDIR/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php82_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi

# php8.3
if [ ! -d $AMPACHEDIR/php83 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -f $AMPACHEDIR/php83/index.php ]; then
  rm -rf $AMPACHEDIR/php83
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -d $AMPACHEDIR/php83_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi
if [ ! -f $AMPACHEDIR/php83_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php83_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi

# php8.4
if [ ! -d $AMPACHEDIR/php84 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php84
fi
if [ ! -f $AMPACHEDIR/php84/index.php ]; then
  rm -rf $AMPACHEDIR/php84
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php84
fi
if [ ! -d $AMPACHEDIR/php84_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php84_squashed
fi
if [ ! -f $AMPACHEDIR/php84_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php84_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php84_squashed
fi


# Launch all the containers
docker-compose -p "ampache77" \
 -f docker/docker-compose82.yml -f docker/docker-compose82_squashed.yml -f docker/docker-compose82_client.yml \
 -f docker/docker-compose83.yml -f docker/docker-compose83_squashed.yml -f docker/docker-compose83_client.yml \
 -f docker/docker-compose84.yml -f docker/docker-compose84_squashed.yml -f docker/docker-compose84_client.yml \
 up -d --build
