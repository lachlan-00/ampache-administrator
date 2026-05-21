#!/bin/sh

RELEASEBRANCH="patch8"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/ampache-patch8 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-patch8
fi
if [ ! -f $AMPACHEDIR/ampache-patch8/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-patch8
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git ampache-patch8
fi
if [ ! -d $AMPACHEDIR/ampache-client ]; then
  git clone -b client8 https://github.com/ampache/ampache.git ampache-client
fi
if [ ! -f $AMPACHEDIR/ampache-client8/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-client
  git clone -b client8 https://github.com/ampache/ampache.git ampache-client
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/captcha ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/captcha
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/images ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/images
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/lib ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/lib
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/templates ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/templates
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/themes ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/themes
fi

# force reset everything
cd $AMPACHEDIR/ampache-patch8 && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

# existing base folders
cp -rfv $AMPACHEDIR/ampache-patch8/bin/* $AMPACHEDIR/ampache-client8/bin/
cp -rfv $AMPACHEDIR/ampache-patch8/config/* $AMPACHEDIR/ampache-client8/config/
cp -rfv $AMPACHEDIR/ampache-patch8/docs/* $AMPACHEDIR/ampache-client8/docs/
cp -rfv $AMPACHEDIR/ampache-patch8/locale/* $AMPACHEDIR/ampache-client8/locale/
cp -rfv $AMPACHEDIR/ampache-patch8/resources/* $AMPACHEDIR/ampache-client8/resources/
cp -rfv $AMPACHEDIR/ampache-patch8/src/* $AMPACHEDIR/ampache-client8/src/
cp -rfv $AMPACHEDIR/ampache-patch8/tests/* $AMPACHEDIR/ampache-client8/tests/
# copy public back over the top
cp -fv $AMPACHEDIR/ampache-patch8/public/*.php $AMPACHEDIR/ampache-client8/public/client/
cp -rfv $AMPACHEDIR/ampache-patch8/public/admin/* $AMPACHEDIR/ampache-client8/public/admin/
cp -rfv $AMPACHEDIR/ampache-patch8/public/daap/* $AMPACHEDIR/ampache-client8/public/daap/
cp -rfv $AMPACHEDIR/ampache-patch8/public/play/* $AMPACHEDIR/ampache-client8/public/play/
cp -rfv $AMPACHEDIR/ampache-patch8/public/rest/* $AMPACHEDIR/ampache-client8/public/rest/
cp -rfv $AMPACHEDIR/ampache-patch8/public/server/* $AMPACHEDIR/ampache-client8/public/server/
cp -rfv $AMPACHEDIR/ampache-patch8/public/upnp/* $AMPACHEDIR/ampache-client8/public/upnp/
cp -rfv $AMPACHEDIR/ampache-patch8/public/webdav/* $AMPACHEDIR/ampache-client8/public/webdav/
# client subfolder
cp -rfv $AMPACHEDIR/ampache-patch8/public/captcha/* $AMPACHEDIR/ampache-client8/public/client/captcha/
cp -rfv $AMPACHEDIR/ampache-patch8/public/dist/* $AMPACHEDIR/ampache-client8/public/client/dist/
cp -rfv $AMPACHEDIR/ampache-patch8/public/images/* $AMPACHEDIR/ampache-client8/public/client/images/
cp -rfv $AMPACHEDIR/ampache-patch8/public/lib/* $AMPACHEDIR/ampache-client8/public/client/lib/
cp -rfv $AMPACHEDIR/ampache-patch8/public/templates/* $AMPACHEDIR/ampache-client8/public/client/templates/
cp -rfv $AMPACHEDIR/ampache-patch8/public/themes/* $AMPACHEDIR/ampache-client8/public/client/themes/

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./client-ampache8.py
