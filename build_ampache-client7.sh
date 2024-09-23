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
if [ ! -d $AMPACHEDIR/ampache-client ]; then
  git clone -b client7 https://github.com/ampache/ampache.git ampache-client
fi
if [ ! -f $AMPACHEDIR/ampache-client/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-client
  git clone -b client7 https://github.com/ampache/ampache.git ampache-client
fi
if [ ! -d $AMPACHEDIR/ampache-client/public/client/captcha ]; then
  mkdir $AMPACHEDIR/ampache-client/public/client/captcha
fi
if [ ! -d $AMPACHEDIR/ampache-client/public/client/images ]; then
  mkdir $AMPACHEDIR/ampache-client/public/client/images
fi
if [ ! -d $AMPACHEDIR/ampache-client/public/client/lib ]; then
  mkdir $AMPACHEDIR/ampache-client/public/client/lib
fi
if [ ! -d $AMPACHEDIR/ampache-client/public/client/templates ]; then
  mkdir $AMPACHEDIR/ampache-client/public/client/templates
fi
if [ ! -d $AMPACHEDIR/ampache-client/public/client/themes ]; then
  mkdir $AMPACHEDIR/ampache-client/public/client/themes
fi

# force reset everything
cd $AMPACHEDIR/ampache-patch7 && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

# existing base folders
cp -rfv $AMPACHEDIR/ampache-patch7/bin/* $AMPACHEDIR/ampache-client/bin/
cp -rfv $AMPACHEDIR/ampache-patch7/config/* $AMPACHEDIR/ampache-client/config/
cp -rfv $AMPACHEDIR/ampache-patch7/docs/* $AMPACHEDIR/ampache-client/docs/
cp -rfv $AMPACHEDIR/ampache-patch7/locale/* $AMPACHEDIR/ampache-client/locale/
cp -rfv $AMPACHEDIR/ampache-patch7/resources/* $AMPACHEDIR/ampache-client/resources/
cp -rfv $AMPACHEDIR/ampache-patch7/src/* $AMPACHEDIR/ampache-client/src/
cp -rfv $AMPACHEDIR/ampache-patch7/tests/* $AMPACHEDIR/ampache-client/tests/
# copy public back over the top
cp -fv $AMPACHEDIR/ampache-patch7/public/*.php $AMPACHEDIR/ampache-client/public/client/
cp -rfv $AMPACHEDIR/ampache-patch7/public/admin/* $AMPACHEDIR/ampache-client/public/admin/
cp -rfv $AMPACHEDIR/ampache-patch7/public/daap/* $AMPACHEDIR/ampache-client/public/daap/
cp -rfv $AMPACHEDIR/ampache-patch7/public/play/* $AMPACHEDIR/ampache-client/public/play/
cp -rfv $AMPACHEDIR/ampache-patch7/public/rest/* $AMPACHEDIR/ampache-client/public/rest/
cp -rfv $AMPACHEDIR/ampache-patch7/public/server/* $AMPACHEDIR/ampache-client/public/server/
cp -rfv $AMPACHEDIR/ampache-patch7/public/upnp/* $AMPACHEDIR/ampache-client/public/upnp/
cp -rfv $AMPACHEDIR/ampache-patch7/public/webdav/* $AMPACHEDIR/ampache-client/public/webdav/
# client subfolder
cp -rfv $AMPACHEDIR/ampache-patch7/public/captcha/* $AMPACHEDIR/ampache-client/public/client/captcha/
cp -rfv $AMPACHEDIR/ampache-patch7/public/dist/* $AMPACHEDIR/ampache-client/public/client/dist/
cp -rfv $AMPACHEDIR/ampache-patch7/public/images/* $AMPACHEDIR/ampache-client/public/client/images/
cp -rfv $AMPACHEDIR/ampache-patch7/public/lib/* $AMPACHEDIR/ampache-client/public/client/lib/
cp -rfv $AMPACHEDIR/ampache-patch7/public/templates/* $AMPACHEDIR/ampache-client/public/client/templates/
cp -rfv $AMPACHEDIR/ampache-patch7/public/themes/* $AMPACHEDIR/ampache-client/public/client/themes/

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./client-ampache7.py
