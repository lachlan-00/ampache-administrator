#!/bin/sh

RELEASEBRANCH="patch7"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/ampache-patch7 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-patch7
fi
if [ ! -f $AMPACHEDIR/ampache-patch7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch7
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-patch7
fi
if [ ! -d $AMPACHEDIR/ampache-squashed7 ]; then
  git clone -b squashed7 https://github.com/ampache/ampache.git ampache-squashed7
fi
if [ ! -f $AMPACHEDIR/ampache-squashed7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed7
  git clone -b squashed7 https://github.com/ampache/ampache.git ampache-squashed7
fi

# force reset everything
cd $AMPACHEDIR/ampache-patch7 && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

rm -rf $AMPACHEDIR/ampache-squashed7/public

# existing base folders
cp -rfv $AMPACHEDIR/ampache-patch7/bin/* $AMPACHEDIR/ampache-squashed7/bin/
cp -rfv $AMPACHEDIR/ampache-patch7/config/* $AMPACHEDIR/ampache-squashed7/config/
cp -rfv $AMPACHEDIR/ampache-patch7/docs/* $AMPACHEDIR/ampache-squashed7/docs/
cp -rfv $AMPACHEDIR/ampache-patch7/locale/* $AMPACHEDIR/ampache-squashed7/locale/
cp -rfv $AMPACHEDIR/ampache-patch7/resources/* $AMPACHEDIR/ampache-squashed7/resources/
cp -rfv $AMPACHEDIR/ampache-patch7/src/* $AMPACHEDIR/ampache-squashed7/src/
cp -rfv $AMPACHEDIR/ampache-patch7/tests/* $AMPACHEDIR/ampache-squashed7/tests/
#copy public back over the top
cp -rfv $AMPACHEDIR/ampache-patch7/public/* $AMPACHEDIR/ampache-squashed7/

rm -rf $AMPACHEDIR/ampache-squashed7/channel
rm -f $AMPACHEDIR/ampache-squashed7/channel.php
rm -f $AMPACHEDIR/ampache-squashed7/docs/examples/channel*

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./squash-ampache7.py
