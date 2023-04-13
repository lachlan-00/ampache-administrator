#!/bin/sh

RELEASEBRANCH="patch5"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/ampache-master ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -f $AMPACHEDIR/ampache-master/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-master
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -d $AMPACHEDIR/ampache-squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git ampache-squashed
fi
if [ ! -f $AMPACHEDIR/ampache-squashed/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed
  git clone -b squashed https://github.com/ampache/ampache.git ampache-squashed
fi

# force reset everything
cd $AMPACHEDIR/ampache-master && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

rm -rf $AMPACHEDIR/ampache-squashed/public

# existing base folders
cp -rfv $AMPACHEDIR/ampache-master/bin/* $AMPACHEDIR/ampache-squashed/bin/
cp -rfv $AMPACHEDIR/ampache-master/config/* $AMPACHEDIR/ampache-squashed/config/
cp -rfv $AMPACHEDIR/ampache-master/docs/* $AMPACHEDIR/ampache-squashed/docs/
cp -rfv $AMPACHEDIR/ampache-master/locale/* $AMPACHEDIR/ampache-squashed/locale/
cp -rfv $AMPACHEDIR/ampache-master/resources/* $AMPACHEDIR/ampache-squashed/resources/
cp -rfv $AMPACHEDIR/ampache-master/src/* $AMPACHEDIR/ampache-squashed/src/
cp -rfv $AMPACHEDIR/ampache-master/tests/* $AMPACHEDIR/ampache-squashed/tests/
#copy public back over the top
cp -rfv $AMPACHEDIR/ampache-master/public/* $AMPACHEDIR/ampache-squashed/

rm -rf $AMPACHEDIR/ampache-squashed/channel
rm -f $AMPACHEDIR/ampache-squashed/channel.php
rm -f $AMPACHEDIR/ampache-squashed/docs/examples/channel*

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./squash-ampache.py
