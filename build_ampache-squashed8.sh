#!/bin/sh

RELEASEBRANCH="develop"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/ampache-$RELEASEBRANCH ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-$RELEASEBRANCH
fi
if [ ! -f $AMPACHEDIR/ampache-$RELEASEBRANCH/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-$RELEASEBRANCH
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-$RELEASEBRANCH
fi
if [ ! -d $AMPACHEDIR/ampache-squashed8 ]; then
  git clone -b squashed8 https://github.com/ampache/ampache.git ampache-squashed8
fi
if [ ! -f $AMPACHEDIR/ampache-squashed8/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed8
  git clone -b squashed8 https://github.com/ampache/ampache.git ampache-squashed8
fi

# force reset everything
cd $AMPACHEDIR/ampache-$RELEASEBRANCH && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

rm -rf $AMPACHEDIR/ampache-squashed8/public

# existing base folders
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/bin/* $AMPACHEDIR/ampache-squashed8/bin/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/config/* $AMPACHEDIR/ampache-squashed8/config/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/docs/* $AMPACHEDIR/ampache-squashed8/docs/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/locale/* $AMPACHEDIR/ampache-squashed8/locale/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/resources/* $AMPACHEDIR/ampache-squashed8/resources/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/src/* $AMPACHEDIR/ampache-squashed8/src/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/tests/* $AMPACHEDIR/ampache-squashed8/tests/
#copy public back over the top
# "public/." rather than "public/*" so the .htaccess files come across too -
# the glob skips dotfiles, which is why they used to drift from the patch branch
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/. $AMPACHEDIR/ampache-squashed8/

rm -rf $AMPACHEDIR/ampache-squashed8/channel
rm -f $AMPACHEDIR/ampache-squashed8/channel.php
rm -f $AMPACHEDIR/ampache-squashed8/docs/examples/channel*

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./squash-ampache8.py
