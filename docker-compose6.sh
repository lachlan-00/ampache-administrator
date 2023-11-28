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

# php7.4
if [ ! -d $AMPACHEDIR/php74 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php74
  cp -f $AMPACHEDIR/extras/composer_old.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -f $AMPACHEDIR/php74/index.php ]; then
  rm -rf $AMPACHEDIR/php74
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php74
  cp -f $AMPACHEDIR/extras/composer_old.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -d $AMPACHEDIR/php74_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php74_squashed
  cp -f $AMPACHEDIR/extras/composer_old_squashed.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -f $AMPACHEDIR/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php74_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php74_squashed
  cp -f $AMPACHEDIR/extras/composer_old_squashed.json $AMPACHEDIR/php81/composer.json
fi

# php8.0
if [ ! -d $AMPACHEDIR/php80 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php80
  cp -f $AMPACHEDIR/extras/composer_old.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -f $AMPACHEDIR/php80/index.php ]; then
  rm -rf $AMPACHEDIR/php80
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php80
  cp -f $AMPACHEDIR/extras/composer_old.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -d $AMPACHEDIR/php80_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php80_squashed
  cp -f $AMPACHEDIR/extras/composer_old_squashed.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -f $AMPACHEDIR/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php80_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php80_squashed
  cp -f $AMPACHEDIR/extras/composer_old_squashed.json $AMPACHEDIR/php81/composer.json
fi

# php8.1
if [ ! -d $AMPACHEDIR/php81 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php81
  cp -f $AMPACHEDIR/extras/composer_old.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -f $AMPACHEDIR/php81/index.php ]; then
  rm -rf $AMPACHEDIR/php81
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php81
  cp -f $AMPACHEDIR/extras/composer_old.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -d $AMPACHEDIR/php81_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php81_squashed
  cp -f $AMPACHEDIR/extras/composer_old_squashed.json $AMPACHEDIR/php81/composer.json
fi
if [ ! -f $AMPACHEDIR/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php81_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php81_squashed
  cp -f $AMPACHEDIR/extras/composer_old_squashed.json $AMPACHEDIR/php81/composer.json
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

# Launch all the containers
docker-compose -f docker/docker-compose74.yml -f docker/docker-compose74_squashed.yml -f docker/docker-compose80.yml -f docker/docker-compose80_squashed.yml -f docker/docker-compose81.yml -f docker/docker-compose81_squashed.yml -f docker/docker-compose82.yml -f docker/docker-compose82_squashed.yml  -f docker/docker-compose83.yml -f docker/docker-compose83_squashed.yml up -d --build

