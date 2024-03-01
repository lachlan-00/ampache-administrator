#!/bin/sh

RELEASEBRANCH="patch7"
SQUASHBRANCH="squashed7"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

# php8.2
if [ ! -d $AMPACHEDIR/php82 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -f $AMPACHEDIR/php82/index.php ]; then
  rm -rf $AMPACHEDIR/php82
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php82
fi
if [ ! -d $AMPACHEDIR/php82_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi
if [ ! -f $AMPACHEDIR/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php82_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php82_squashed
fi

# php8.3
if [ ! -d $AMPACHEDIR/php83 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -f $AMPACHEDIR/php83/index.php ]; then
  rm -rf $AMPACHEDIR/php83
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php83
fi
if [ ! -d $AMPACHEDIR/php83_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi
if [ ! -f $AMPACHEDIR/php83_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php83_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php83_squashed
fi

# php 8.2
cd $AMPACHEDIR/php82 && git checkout -f $RELEASEBRANCH &&  git reset --hard origin/$RELEASEBRANCH && git pull
rm -rf ./composer.lock vendor/* public/lib/components/*
php8.2 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php82_squashed && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/
php8.2 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.3
cd $AMPACHEDIR/php83 && git checkout -f $RELEASEBRANCH &&  git reset --hard origin/$RELEASEBRANCH && git pull
rm -rf ./composer.lock vendor/* public/lib/components/*
php8.3 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php83_squashed && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/
php8.3 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# create the htaccess files

# php8.2
if [ ! -f $AMPACHEDIR/php82/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php82/public/play/.htaccess.dist $AMPACHEDIR/php82/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php82/public/rest/.htaccess.dist $AMPACHEDIR/php82/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php82_squashed/play/.htaccess.dist $AMPACHEDIR/php82_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php82_squashed/rest/.htaccess.dist $AMPACHEDIR/php82_squashed/rest/.htaccess
fi

# php8.3
if [ ! -f $AMPACHEDIR/php83/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php83/public/play/.htaccess.dist $AMPACHEDIR/php83/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php83/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php83/public/rest/.htaccess.dist $AMPACHEDIR/php83/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php83_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php83_squashed/play/.htaccess.dist $AMPACHEDIR/php83_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php83_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php83_squashed/rest/.htaccess.dist $AMPACHEDIR/php83_squashed/rest/.htaccess
fi

# create the docker volume folders
if [ ! -d $AMPACHEDIR/docker/log ]; then
  mkdir $AMPACHEDIR/docker/log
fi
if [ ! -d $AMPACHEDIR/docker/media ]; then
  mkdir $AMPACHEDIR/docker/media
fi
if [ ! -d $AMPACHEDIR/docker/mysql ]; then
  mkdir $AMPACHEDIR/docker/mysql
fi

# reset perms
chown $UID:33 $AMPACHEDIR/docker/log
chmod 775 $AMPACHEDIR/docker/log

chown $UID:33 $AMPACHEDIR/docker/media
chmod 775 $AMPACHEDIR/docker/media

# php8.2
chown $UID:33 $AMPACHEDIR/php82/composer.json 
chmod 775 $AMPACHEDIR/php82/composer.json
chown -R $UID:33 $AMPACHEDIR/php82/config
chmod -R 775 $AMPACHEDIR/php82/config
chown -R $UID:33 $AMPACHEDIR/php82/vendor/
chmod -R 775 $AMPACHEDIR/php82/vendor/
chown -R $UID:33 $AMPACHEDIR/php82/public/
chmod -R 775 $AMPACHEDIR/php82/public/

chown $UID:33 $AMPACHEDIR/php82_squashed/composer.json 
chmod 775 $AMPACHEDIR/php82_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/php82_squashed/config
chmod -R 775 $AMPACHEDIR/php82_squashed/config
chown -R $UID:33 $AMPACHEDIR/php82_squashed/vendor/
chmod -R 775 $AMPACHEDIR/php82_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/php82_squashed/
chmod -R 775 $AMPACHEDIR/php82_squashed/

# php8.3
chown $UID:33 $AMPACHEDIR/php83/composer.json 
chmod 775 $AMPACHEDIR/php83/composer.json
chown -R $UID:33 $AMPACHEDIR/php83/config
chmod -R 775 $AMPACHEDIR/php83/config
chown -R $UID:33 $AMPACHEDIR/php83/vendor/
chmod -R 775 $AMPACHEDIR/php83/vendor/
chown -R $UID:33 $AMPACHEDIR/php83/public/
chmod -R 775 $AMPACHEDIR/php83/public/

chown $UID:33 $AMPACHEDIR/php83_squashed/composer.json 
chmod 775 $AMPACHEDIR/php83_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/php83_squashed/config
chmod -R 775 $AMPACHEDIR/php83_squashed/config
chown -R $UID:33 $AMPACHEDIR/php83_squashed/vendor/
chmod -R 775 $AMPACHEDIR/php83_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/php83_squashed/
chmod -R 775 $AMPACHEDIR/php83_squashed/

# remove the lock and install composer packages

# php8.2
if [ -f $AMPACHEDIR/php82/composer.lock ]; then
  rm $AMPACHEDIR/php82/composer.lock
fi
cd $AMPACHEDIR/php82 && php8.2 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php82_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php82_squashed/composer.lock
fi
cd $AMPACHEDIR/php82 && php8.2 $COMPOSERPATH install && cd $AMPACHEDIR

# php8.3
if [ -f $AMPACHEDIR/php83/composer.lock ]; then
  rm $AMPACHEDIR/php83/composer.lock
fi
cd $AMPACHEDIR/php83 && php8.3 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php83_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php83_squashed/composer.lock
fi
cd $AMPACHEDIR/php83 && php8.3 $COMPOSERPATH install && cd $AMPACHEDIR

chown $UID:33 $AMPACHEDIR/docker/log
chmod 775 $AMPACHEDIR/docker/log
chown $UID:33 $AMPACHEDIR/docker/media
chmod 775 $AMPACHEDIR/docker/media
chown $UID:112 $AMPACHEDIR/docker/mysql
chmod 775 $AMPACHEDIR/docker/mysql

chown $UID:33 $AMPACHEDIR/php82
chmod 775 $AMPACHEDIR/php82
chown $UID:33 $AMPACHEDIR/php82_squashed
chmod 775 $AMPACHEDIR/php82_squashed
