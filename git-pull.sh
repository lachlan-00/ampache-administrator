#!/bin/sh

AMPACHEDIR=$PWD

# Ampache
if [ -d $AMPACHEDIR/ampache-develop ]; then
  cd $AMPACHEDIR/ampache-develop && git pull
fi
if [ -d $AMPACHEDIR/ampache-master ]; then
  cd $AMPACHEDIR/ampache-master && git pull
fi
if [ -d $AMPACHEDIR/ampache-squashed ]; then
  cd $AMPACHEDIR/ampache-squashed && git pull
fi

# ampache test
if [ -d $AMPACHEDIR/ampache-test/ampache ]; then
  cd $AMPACHEDIR/ampache-test/ampache && git pull
fi

# php7.4
if [ -d $AMPACHEDIR/php74 ]; then
  cd $AMPACHEDIR/php74 && git pull
fi
if [ -d $AMPACHEDIR/php74_squashed ]; then
  cd $AMPACHEDIR/php74_squashed && git pull
fi

# php8.0
if [ -d $AMPACHEDIR/php80 ]; then
  cd $AMPACHEDIR/php80 && git pull
fi
if [ -d $AMPACHEDIR/php80_squashed ]; then
  cd $AMPACHEDIR/php80_squashed && git pull
fi

# php8.1
if [ -d $AMPACHEDIR/php81 ]; then
  cd $AMPACHEDIR/php81 && git pull
fi
if [ -d $AMPACHEDIR/php81_squashed ]; then
  cd $AMPACHEDIR/php81_squashed && git pull
fi

# php8.2
if [ -d $AMPACHEDIR/php82 ]; then
  cd $AMPACHEDIR/php82 && git pull
fi
if [ -d $AMPACHEDIR/php82_squashed ]; then
  cd $AMPACHEDIR/php82_squashed && git pull
fi

cd $AMPACHEDIR

