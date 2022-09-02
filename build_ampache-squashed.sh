#!/bin/sh

AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/ampache-master ]; then
  git clone -b master https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -f $AMPACHEDIR/ampache-master/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-master
  git clone -b master https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -d $AMPACHEDIR/ampache-squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git ampache-squashed
fi
if [ ! -f $AMPACHEDIR/ampache-squashed/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-squashed
  git clone -b squashed https://github.com/ampache/ampache.git ampache-squashed
fi

rm -rf ./ampache-squashed/public

# existing base folders
cp -rfv ./ampache-master/bin/* ./ampache-squashed/bin/
cp -rfv ./ampache-master/config/* ./ampache-squashed/config/
cp -rfv ./ampache-master/docs/* ./ampache-squashed/docs/
cp -rfv ./ampache-master/locale/* ./ampache-squashed/locale/
cp -rfv ./ampache-master/resources/* ./ampache-squashed/resources/
cp -rfv ./ampache-master/src/* ./ampache-squashed/src/
cp -rfv ./ampache-master/tests/* ./ampache-squashed/tests/
#copy public back over the top
cp -rfv ./ampache-master/public/* ./ampache-squashed/

# regex the old strings from the public branch to the squashed branch
python3 ./squash-ampache.py
