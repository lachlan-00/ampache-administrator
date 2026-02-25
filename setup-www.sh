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

