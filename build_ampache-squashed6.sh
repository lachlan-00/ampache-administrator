#!/bin/sh

RELEASEBRANCH="patch6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/ampache-patch6 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-patch6
fi
if [ ! -f $AMPACHEDIR/ampache-patch6/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch6
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-patch6
fi
if [ ! -d $AMPACHEDIR/ampache-squashed6 ]; then
  git clone -b squashed6 https://github.com/ampache/ampache.git ampache-squashed6
fi
if [ ! -f $AMPACHEDIR/ampache-squashed6/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed6
  git clone -b squashed6 https://github.com/ampache/ampache.git ampache-squashed6
fi

# force reset everything
cd $AMPACHEDIR/ampache-patch6 && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

rm -rf $AMPACHEDIR/ampache-squashed6/public

# existing base folders
cp -rfv $AMPACHEDIR/ampache-patch6/bin/* $AMPACHEDIR/ampache-squashed6/bin/
cp -rfv $AMPACHEDIR/ampache-patch6/config/* $AMPACHEDIR/ampache-squashed6/config/
cp -rfv $AMPACHEDIR/ampache-patch6/docs/* $AMPACHEDIR/ampache-squashed6/docs/
cp -rfv $AMPACHEDIR/ampache-patch6/locale/* $AMPACHEDIR/ampache-squashed6/locale/
cp -rfv $AMPACHEDIR/ampache-patch6/resources/* $AMPACHEDIR/ampache-squashed6/resources/
cp -rfv $AMPACHEDIR/ampache-patch6/src/* $AMPACHEDIR/ampache-squashed6/src/
cp -rfv $AMPACHEDIR/ampache-patch6/tests/* $AMPACHEDIR/ampache-squashed6/tests/
#copy public back over the top
cp -rfv $AMPACHEDIR/ampache-patch6/public/* $AMPACHEDIR/ampache-squashed6/

rm -rf $AMPACHEDIR/ampache-squashed6/channel
rm -f $AMPACHEDIR/ampache-squashed6/channel.php
rm -f $AMPACHEDIR/ampache-squashed6/docs/examples/channel*

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./squash-ampache6.py
