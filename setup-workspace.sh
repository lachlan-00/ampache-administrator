#!/bin/sh

AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

# DEVELOPMENT BRANCHES
if [ ! -d $AMPACHEDIR/ampache-develop ]; then
  cd $AMPACHEDIR && git clone -b develop https://github.com/ampache/ampache.git ampache-develop
fi
if [ ! -f $AMPACHEDIR/ampache-develop/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-develop
  cd $AMPACHEDIR && git clone -b develop https://github.com/ampache/ampache.git ampache-develop
fi
if [ ! -d $AMPACHEDIR/ampache-master ]; then
  cd $AMPACHEDIR && git clone -b master https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -f $AMPACHEDIR/ampache-master/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-master
  cd $AMPACHEDIR && git clone -b master https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -d $AMPACHEDIR/ampache-patch7 ]; then
  cd $AMPACHEDIR && git clone -b patch7 https://github.com/ampache/ampache.git ampache-patch7
fi
if [ ! -f $AMPACHEDIR/ampache-patch7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch7
  cd $AMPACHEDIR && git clone -b patch7 https://github.com/ampache/ampache.git ampache-patch7
fi
if [ ! -d $AMPACHEDIR/ampache-squashed7 ]; then
  cd $AMPACHEDIR && git clone -b squashed7 https://github.com/ampache/ampache.git ampache-squashed7
fi
if [ ! -f $AMPACHEDIR/ampache-squashed7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed7
  cd $AMPACHEDIR && git clone -b squashed7 https://github.com/ampache/ampache.git ampache-squashed7
fi
if [ ! -d $AMPACHEDIR/ampache-client7 ]; then
  cd $AMPACHEDIR && git clone -b client7 https://github.com/ampache/ampache.git ampache-client7
fi
if [ ! -f $AMPACHEDIR/ampache-client7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-client7
  cd $AMPACHEDIR && git clone -b client7 https://github.com/ampache/ampache.git ampache-client7
fi
if [ -f $AMPACHEDIR/ampache-develop/composer.lock ]; then
  rm $AMPACHEDIR/ampache-develop/composer.lock
fi
cd $AMPACHEDIR/ampache-develop && php $COMPOSERPATH install && cd $AMPACHEDIR

if [ -f $AMPACHEDIR/ampache-master/composer.lock ]; then
  rm $AMPACHEDIR/ampache-master/composer.lock
fi
cd $AMPACHEDIR/ampache-master && php $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/ampache-patch7/composer.lock ]; then
  rm $AMPACHEDIR/ampache-patch7/composer.lock
fi
cd $AMPACHEDIR/ampache-patch7 && php $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/ampache-squashed7/composer.lock ]; then
  rm $AMPACHEDIR/ampache-squashed7/composer.lock
fi
cd $AMPACHEDIR/ampache-squashed7 && php $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/ampache-client7/composer.lock ]; then
  rm $AMPACHEDIR/ampache-client7/composer.lock
fi
cd $AMPACHEDIR/ampache-client7 && php $COMPOSERPATH install && cd $AMPACHEDIR

# AMPACHE 5
if [ ! -d $AMPACHEDIR/ampache-patch5 ]; then
  cd $AMPACHEDIR && git clone -b patch5 https://github.com/ampache/ampache.git ampache-patch5
fi
if [ ! -f $AMPACHEDIR/ampache-patch5/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch5
  cd $AMPACHEDIR && git clone -b patch5 https://github.com/ampache/ampache.git ampache-patch5
fi
if [ ! -d $AMPACHEDIR/ampache-squashed5 ]; then
  cd $AMPACHEDIR && git clone -b squashed https://github.com/ampache/ampache.git ampache-squashed5
fi
if [ ! -f $AMPACHEDIR/ampache-squashed5/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed5
  cd $AMPACHEDIR && git clone -b squashed https://github.com/ampache/ampache.git ampache-squashed5
fi
if [ -f $AMPACHEDIR/ampache-patch5/composer.lock ]; then
  rm $AMPACHEDIR/ampache-patch5/composer.lock
fi
cd $AMPACHEDIR/ampache-patch5 && php $COMPOSERPATH install && cd $AMPACHEDIR

if [ -f $AMPACHEDIR/ampache-squashed5/composer.lock ]; then
  rm $AMPACHEDIR/ampache-squashed5/composer.lock
fi
cd $AMPACHEDIR/ampache-squashed5 && php $COMPOSERPATH install && cd $AMPACHEDIR

# AMPACHE 6
if [ ! -d $AMPACHEDIR/ampache-patch6 ]; then
  cd $AMPACHEDIR && git clone -b patch6 https://github.com/ampache/ampache.git ampache-patch6
fi
if [ ! -f $AMPACHEDIR/ampache-patch6/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch6
  cd $AMPACHEDIR && git clone -b patch6 https://github.com/ampache/ampache.git ampache-patch6
fi
if [ ! -d $AMPACHEDIR/ampache-squashed6 ]; then
  cd $AMPACHEDIR && git clone -b squashed6 https://github.com/ampache/ampache.git ampache-squashed6
fi
if [ ! -f $AMPACHEDIR/ampache-squashed6/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed6
  cd $AMPACHEDIR && git clone -b squashed6 https://github.com/ampache/ampache.git ampache-squashed6
fi

if [ -f $AMPACHEDIR/ampache-patch6/composer.lock ]; then
  rm $AMPACHEDIR/ampache-patch6/composer.lock
fi
cd $AMPACHEDIR/ampache-patch6 && php $COMPOSERPATH install && cd $AMPACHEDIR

if [ -f $AMPACHEDIR/ampache-squashed6/composer.lock ]; then
  rm $AMPACHEDIR/ampache-squashed6/composer.lock
fi
cd $AMPACHEDIR/ampache-squashed6 && php $COMPOSERPATH install && cd $AMPACHEDIR

