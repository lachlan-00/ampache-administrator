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
if [ ! -d $AMPACHEDIR/ampache-client7 ]; then
  git clone -b client7 https://github.com/ampache/ampache.git ampache-client7
fi
if [ ! -f $AMPACHEDIR/ampache-client7/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-client7
  git clone -b client7 https://github.com/ampache/ampache.git ampache-client7
fi
if [ ! -d $AMPACHEDIR/ampache-client7/public/client/dist ]; then
  mkdir $AMPACHEDIR/ampache-client7/public/client/dist
fi
if [ ! -d $AMPACHEDIR/ampache-client7/public/client/images ]; then
  mkdir $AMPACHEDIR/ampache-client7/public/client/images
fi
if [ ! -d $AMPACHEDIR/ampache-client7/public/client/lib ]; then
  mkdir $AMPACHEDIR/ampache-client7/public/client/lib
fi
if [ ! -d $AMPACHEDIR/ampache-client7/public/client/templates ]; then
  mkdir $AMPACHEDIR/ampache-client7/public/client/templates
fi
if [ ! -d $AMPACHEDIR/ampache-client7/public/client/themes ]; then
  mkdir $AMPACHEDIR/ampache-client7/public/client/themes
fi

# force reset everything
cd $AMPACHEDIR/ampache-patch7 && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

# existing base folders
cp -rfv $AMPACHEDIR/ampache-patch7/bin/* $AMPACHEDIR/ampache-client7/bin/
cp -rfv $AMPACHEDIR/ampache-patch7/config/* $AMPACHEDIR/ampache-client7/config/
cp -rfv $AMPACHEDIR/ampache-patch7/docs/* $AMPACHEDIR/ampache-client7/docs/
cp -rfv $AMPACHEDIR/ampache-patch7/locale/* $AMPACHEDIR/ampache-client7/locale/
cp -rfv $AMPACHEDIR/ampache-patch7/resources/* $AMPACHEDIR/ampache-client7/resources/
cp -rfv $AMPACHEDIR/ampache-patch7/src/* $AMPACHEDIR/ampache-client7/src/
cp -rfv $AMPACHEDIR/ampache-patch7/tests/* $AMPACHEDIR/ampache-client7/tests/
# copy public back over the top
# "dir/." rather than "dir/*" so the .htaccess files come across too - the
# glob skips dotfiles, which is why they used to drift from the patch branch
cp -fv $AMPACHEDIR/ampache-patch7/public/*.php $AMPACHEDIR/ampache-client7/public/client/
cp -fv $AMPACHEDIR/ampache-patch7/public/.htaccess.dist $AMPACHEDIR/ampache-client7/public/
cp -rfv $AMPACHEDIR/ampache-patch7/public/admin/. $AMPACHEDIR/ampache-client7/public/admin/
cp -rfv $AMPACHEDIR/ampache-patch7/public/daap/. $AMPACHEDIR/ampache-client7/public/daap/
cp -rfv $AMPACHEDIR/ampache-patch7/public/play/. $AMPACHEDIR/ampache-client7/public/play/
cp -rfv $AMPACHEDIR/ampache-patch7/public/rest/. $AMPACHEDIR/ampache-client7/public/rest/
cp -rfv $AMPACHEDIR/ampache-patch7/public/server/. $AMPACHEDIR/ampache-client7/public/server/
cp -rfv $AMPACHEDIR/ampache-patch7/public/upnp/. $AMPACHEDIR/ampache-client7/public/upnp/
cp -rfv $AMPACHEDIR/ampache-patch7/public/webdav/. $AMPACHEDIR/ampache-client7/public/webdav/
# client subfolder
cp -rfv $AMPACHEDIR/ampache-patch7/public/dist/. $AMPACHEDIR/ampache-client7/public/client/dist/
cp -rfv $AMPACHEDIR/ampache-patch7/public/images/. $AMPACHEDIR/ampache-client7/public/client/images/
cp -rfv $AMPACHEDIR/ampache-patch7/public/lib/. $AMPACHEDIR/ampache-client7/public/client/lib/
cp -rfv $AMPACHEDIR/ampache-patch7/public/templates/. $AMPACHEDIR/ampache-client7/public/client/templates/
cp -rfv $AMPACHEDIR/ampache-patch7/public/themes/. $AMPACHEDIR/ampache-client7/public/client/themes/

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./client-ampache7.py
