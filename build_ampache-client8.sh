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
if [ ! -d $AMPACHEDIR/ampache-client8 ]; then
  git clone -b client8 https://github.com/ampache/ampache.git ampache-client8
fi
if [ ! -f $AMPACHEDIR/ampache-client8/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-client8
  git clone -b client8 https://github.com/ampache/ampache.git ampache-client8
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/dist ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/dist
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/m ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/m
fi
if [ ! -d $AMPACHEDIR/ampache-client8/public/client/play ]; then
  mkdir $AMPACHEDIR/ampache-client8/public/client/play
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
cd $AMPACHEDIR/ampache-$RELEASEBRANCH && git fetch origin $RELEASEBRANCH && git checkout $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull

# existing base folders
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/bin/* $AMPACHEDIR/ampache-client8/bin/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/config/* $AMPACHEDIR/ampache-client8/config/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/docs/* $AMPACHEDIR/ampache-client8/docs/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/locale/* $AMPACHEDIR/ampache-client8/locale/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/resources/* $AMPACHEDIR/ampache-client8/resources/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/src/* $AMPACHEDIR/ampache-client8/src/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/tests/* $AMPACHEDIR/ampache-client8/tests/
# copy public back over the top
# "dir/." rather than "dir/*" so the .htaccess files come across too - the
# glob skips dotfiles, which is why they used to drift from the patch branch
cp -fv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/*.php $AMPACHEDIR/ampache-client8/public/client/
cp -fv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/.htaccess.dist $AMPACHEDIR/ampache-client8/public/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/admin/. $AMPACHEDIR/ampache-client8/public/admin/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/daap/. $AMPACHEDIR/ampache-client8/public/daap/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/oidc/. $AMPACHEDIR/ampache-client8/public/oidc/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/rest/. $AMPACHEDIR/ampache-client8/public/rest/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/server/. $AMPACHEDIR/ampache-client8/public/server/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/upnp/. $AMPACHEDIR/ampache-client8/public/upnp/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/webdav/. $AMPACHEDIR/ampache-client8/public/webdav/
# client subfolder
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/dist/. $AMPACHEDIR/ampache-client8/public/client/dist/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/images/. $AMPACHEDIR/ampache-client8/public/client/images/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/lib/. $AMPACHEDIR/ampache-client8/public/client/lib/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/m/. $AMPACHEDIR/ampache-client8/public/client/m/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/play/. $AMPACHEDIR/ampache-client8/public/client/play/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/templates/. $AMPACHEDIR/ampache-client8/public/client/templates/
cp -rfv $AMPACHEDIR/ampache-$RELEASEBRANCH/public/themes/. $AMPACHEDIR/ampache-client8/public/client/themes/

cd $AMPACHEDIR

# regex the old strings from the public branch to the squashed branch
python3 ./client-ampache8.py
