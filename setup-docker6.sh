#!/bin/sh

RELEASEBRANCH="patch6"
SQUASHBRANCH="squashed6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

# php7.4
if [ ! -d $AMPACHEDIR/php74 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php74
fi
if [ ! -f $AMPACHEDIR/php74/index.php ]; then
  rm -rf $AMPACHEDIR/php74
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php74
fi
if [ ! -d $AMPACHEDIR/php74_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php74_squashed
fi
if [ ! -f $AMPACHEDIR/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php74_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php74_squashed
fi

# php8.0
if [ ! -d $AMPACHEDIR/php80 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php80
fi
if [ ! -f $AMPACHEDIR/php80/index.php ]; then
  rm -rf $AMPACHEDIR/php80
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php80
fi
if [ ! -d $AMPACHEDIR/php80_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php80_squashed
fi
if [ ! -f $AMPACHEDIR/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php80_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php80_squashed
fi

# php8.1
if [ ! -d $AMPACHEDIR/php81 ]; then
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php81
fi
if [ ! -f $AMPACHEDIR/php81/index.php ]; then
  rm -rf $AMPACHEDIR/php81
  git clone -b $RELEASEBRANCH https://github.com/ampache/ampache.git php81
fi
if [ ! -d $AMPACHEDIR/php81_squashed ]; then
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php81_squashed
fi
if [ ! -f $AMPACHEDIR/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php81_squashed
  git clone -b $SQUASHBRANCH https://github.com/ampache/ampache.git php81_squashed
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


# php 7.4
cd $AMPACHEDIR/php74 && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cp -f $AMPACHEDIR/extras/composer_old.json ./composer.json
rm -rf ./composer.lock vendor/* public/lib/components/*
php7.4 $COMPOSERPATH update

find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php74_squashed && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cp -f $AMPACHEDIR/extras/composer_old_squashed.json ./composer.json
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/
php7.4 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.0
cd $AMPACHEDIR/php80 && git checkout -f $RELEASEBRANCH && git reset --hard origin/$RELEASEBRANCH && git pull
cp -f $AMPACHEDIR/extras/composer_old.json ./composer.json
rm -rf ./composer.lock vendor/* public/lib/components/*
php8.0 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php80_squashed && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cp -f $AMPACHEDIR/extras/composer_old_squashed.json ./composer.json
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/
php8.0 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

# php 8.1
cd $AMPACHEDIR/php81 && git checkout -f $RELEASEBRANCH &&  git reset --hard origin/$RELEASEBRANCH && git pull
cp -f $AMPACHEDIR/extras/composer_old.json ./composer.json
rm -rf ./composer.lock vendor/* public/lib/components/*
php8.1 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./public/lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./public/lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php81_squashed && git checkout -f $SQUASHBRANCH && git reset --hard origin/$SQUASHBRANCH && git pull
cp -f $AMPACHEDIR/extras/composer_old_squashed.json ./composer.json
rm -rf ./composer.lock vendor/* ./lib/components/* ./docker/
php8.1 $COMPOSERPATH update
find . -xtype l -exec rm {} \;
cp $AMPACHEDIR/extras/jquery.contextMenu.min.js.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/jquery.contextMenu.min.css.map ./lib/components/jquery-contextmenu/dist/
cp $AMPACHEDIR/extras/StringReader.php ./vendor/gettext/gettext/src/Utils/
cp -rf $AMPACHEDIR/extras/prettyphoto/* ./lib/components/prettyphoto
find . -name "*.map.1" -exec rm {} \;

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

# php7.4
if [ ! -f $AMPACHEDIR/php74/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php74/public/play/.htaccess.dist $AMPACHEDIR/php74/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php74/public/rest/.htaccess.dist $AMPACHEDIR/php74/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php74_squashed/play/.htaccess.dist $AMPACHEDIR/php74_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php74_squashed/rest/.htaccess.dist $AMPACHEDIR/php74_squashed/rest/.htaccess
fi

# php8.0
if [ ! -f $AMPACHEDIR/php80/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php80/public/play/.htaccess.dist $AMPACHEDIR/php80/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php80/public/rest/.htaccess.dist $AMPACHEDIR/php80/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php80_squashed/play/.htaccess.dist $AMPACHEDIR/php80_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php80_squashed/rest/.htaccess.dist $AMPACHEDIR/php80_squashed/rest/.htaccess
fi

# php8.1
if [ ! -f $AMPACHEDIR/php81/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php81/public/play/.htaccess.dist $AMPACHEDIR/php81/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php81/public/rest/.htaccess.dist $AMPACHEDIR/php81/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php81_squashed/play/.htaccess.dist $AMPACHEDIR/php81_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php81_squashed/rest/.htaccess.dist $AMPACHEDIR/php81_squashed/rest/.htaccess
fi

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

# php7.4
chown $UID:33 $AMPACHEDIR/php74/composer.json 
chmod 775 $AMPACHEDIR/php74/composer.json
chown -R $UID:33 $AMPACHEDIR/php74/config
chmod -R 775 $AMPACHEDIR/php74/config
chown -R $UID:33 $AMPACHEDIR/php74/vendor/
chmod -R 775 $AMPACHEDIR/php74/vendor/
chown -R $UID:33 $AMPACHEDIR/php74/public/
chmod -R 775 $AMPACHEDIR/php74/public/

chown $UID:33 $AMPACHEDIR/php74_squashed/composer.json 
chmod 775 $AMPACHEDIR/php74_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/php74_squashed/config
chmod -R 775 $AMPACHEDIR/php74_squashed/config
chown -R $UID:33 $AMPACHEDIR/php74_squashed/vendor/
chmod -R 775 $AMPACHEDIR/php74_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/php74_squashed/
chmod -R 775 $AMPACHEDIR/php74_squashed/

# php8.0
chown $UID:33 $AMPACHEDIR/php80/composer.json 
chmod 775 $AMPACHEDIR/php80/composer.json
chown -R $UID:33 $AMPACHEDIR/php80/config
chmod -R 775 $AMPACHEDIR/php80/config
chown -R $UID:33 $AMPACHEDIR/php80/vendor/
chmod -R 775 $AMPACHEDIR/php80/vendor/
chown -R $UID:33 $AMPACHEDIR/php80/public/
chmod -R 775 $AMPACHEDIR/php80/public/

chown $UID:33 $AMPACHEDIR/php80_squashed/composer.json 
chmod 775 $AMPACHEDIR/php80_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/php80_squashed/config
chmod -R 775 $AMPACHEDIR/php80_squashed/config
chown -R $UID:33 $AMPACHEDIR/php80_squashed/vendor/
chmod -R 775 $AMPACHEDIR/php80_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/php80_squashed/
chmod -R 775 $AMPACHEDIR/php80_squashed/

# php8.1
chown $UID:33 $AMPACHEDIR/php81/composer.json 
chmod 775 $AMPACHEDIR/php81/composer.json
chown -R $UID:33 $AMPACHEDIR/php81/config
chmod -R 775 $AMPACHEDIR/php81/config
chown -R $UID:33 $AMPACHEDIR/php81/vendor/
chmod -R 775 $AMPACHEDIR/php81/vendor/
chown -R $UID:33 $AMPACHEDIR/php81/public/
chmod -R 775 $AMPACHEDIR/php81/public/

chown $UID:33 $AMPACHEDIR/php81_squashed/composer.json 
chmod 775 $AMPACHEDIR/php81_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/php81_squashed/config
chmod -R 775 $AMPACHEDIR/php81_squashed/config
chown -R $UID:33 $AMPACHEDIR/php81_squashed/vendor/
chmod -R 775 $AMPACHEDIR/php81_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/php81_squashed/
chmod -R 775 $AMPACHEDIR/php81_squashed/

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

# php7.4
if [ -f $AMPACHEDIR/php74/composer.lock ]; then
  rm $AMPACHEDIR/php74/composer.lock
fi
cd $AMPACHEDIR/php74 && php7.4 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php74_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php74_squashed/composer.lock
fi
cd $AMPACHEDIR/php74_squashed && php7.4 $COMPOSERPATH install && cd $AMPACHEDIR

# php8.0
if [ -f $AMPACHEDIR/php80/composer.lock ]; then
  rm $AMPACHEDIR/php80/composer.lock
fi
cd $AMPACHEDIR/php80 && php8.0 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php80_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php80_squashed/composer.lock
fi
cd $AMPACHEDIR/php80 && php8.0 $COMPOSERPATH install && cd $AMPACHEDIR

# php8.1
if [ -f $AMPACHEDIR/php81/composer.lock ]; then
  rm $AMPACHEDIR/php81/composer.lock
fi
cd $AMPACHEDIR/php81 && php8.1 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php81_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php81_squashed/composer.lock
fi
cd $AMPACHEDIR/php81 && php8.1 $COMPOSERPATH install && cd $AMPACHEDIR

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

chown $UID:33 $AMPACHEDIR/php74
chmod 775 $AMPACHEDIR/php74
chown $UID:33 $AMPACHEDIR/php74_squashed
chmod 775 $AMPACHEDIR/php74_squashed
chown $UID:33 $AMPACHEDIR/php80
chmod 775 $AMPACHEDIR/php80
chown $UID:33 $AMPACHEDIR/php80_squashed
chmod 775 $AMPACHEDIR/php80_squashed
chown $UID:33 $AMPACHEDIR/php81
chmod 775 $AMPACHEDIR/php81
chown $UID:33 $AMPACHEDIR/php81_squashed
chmod 775 $AMPACHEDIR/php81_squashed
chown $UID:33 $AMPACHEDIR/php82
chmod 775 $AMPACHEDIR/php82
chown $UID:33 $AMPACHEDIR/php82_squashed
chmod 775 $AMPACHEDIR/php82_squashed
