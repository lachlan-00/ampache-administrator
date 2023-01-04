#!/bin/sh

AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

# php7.4
if [ ! -d $AMPACHEDIR/php74 ]; then
  git clone -b master https://github.com/ampache/ampache.git php74
fi
if [ ! -f $AMPACHEDIR/php74/index.php ]; then
  rm -rf $AMPACHEDIR/php74
  git clone -b master https://github.com/ampache/ampache.git php74
fi
if [ ! -d $AMPACHEDIR/php74_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php74_squashed
fi
if [ ! -f $AMPACHEDIR/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php74_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php74_squashed
fi

# php8.0
if [ ! -d $AMPACHEDIR/php80 ]; then
  git clone -b master https://github.com/ampache/ampache.git php80
fi
if [ ! -f $AMPACHEDIR/php80/index.php ]; then
  rm -rf $AMPACHEDIR/php80
  git clone -b master https://github.com/ampache/ampache.git php80
fi
if [ ! -d $AMPACHEDIR/php80_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php80_squashed
fi
if [ ! -f $AMPACHEDIR/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php80_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php80_squashed
fi

# php8.1
if [ ! -d $AMPACHEDIR/php81 ]; then
  git clone -b master https://github.com/ampache/ampache.git php81
fi
if [ ! -f $AMPACHEDIR/php81/index.php ]; then
  rm -rf $AMPACHEDIR/php81
  git clone -b master https://github.com/ampache/ampache.git php81
fi
if [ ! -d $AMPACHEDIR/php81_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php81_squashed
fi
if [ ! -f $AMPACHEDIR/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php81_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php81_squashed
fi

# php8.2
if [ ! -d $AMPACHEDIR/php82 ]; then
  git clone -b master https://github.com/ampache/ampache.git php82
fi
if [ ! -f $AMPACHEDIR/php82/index.php ]; then
  rm -rf $AMPACHEDIR/php82
  git clone -b master https://github.com/ampache/ampache.git php82
fi
if [ ! -d $AMPACHEDIR/php82_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php82_squashed
fi
if [ ! -f $AMPACHEDIR/php82_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php82_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php82_squashed
fi

# php7.4
cd $AMPACHEDIR/php74 && git reset --hard origin/master && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php7.4 $COMPOSERPATH install
php7.4 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php74_squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php7.4 $COMPOSERPATH install
php7.4 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;

# php8.0
cd $AMPACHEDIR/php80 && git reset --hard origin/master && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.0 $COMPOSERPATH install
php8.0 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php80_squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.0 $COMPOSERPATH install
php8.0 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;

# php8.1
cd $AMPACHEDIR/php81 && git reset --hard origin/master && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.1 $COMPOSERPATH install
php8.1 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;

cd $AMPACHEDIR/php81_squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.1 $COMPOSERPATH install
php8.1 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;

# php8.2
cd $AMPACHEDIR/php82 && git reset --hard origin/master && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.2 $COMPOSERPATH install
php8.2 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.2" -exec rm {} \;

cd $AMPACHEDIR/php82_squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.2 $COMPOSERPATH install
php8.2 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.2" -exec rm {} \;

# create the htaccess files

# php7.4
if [ ! -f $AMPACHEDIR/php74/public/channel/.htaccess ]; then
  cp $AMPACHEDIR/php74/public/channel/.htaccess.dist $AMPACHEDIR/php74/public/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php74/public/play/.htaccess.dist $AMPACHEDIR/php74/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php74/public/rest/.htaccess.dist $AMPACHEDIR/php74/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74_squashed/channel/.htaccess ]; then
  cp $AMPACHEDIR/php74_squashed/channel/.htaccess.dist $AMPACHEDIR/php74_squashed/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php74_squashed/play/.htaccess.dist $AMPACHEDIR/php74_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php74_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php74_squashed/rest/.htaccess.dist $AMPACHEDIR/php74_squashed/rest/.htaccess
fi

# php8.0
if [ ! -f $AMPACHEDIR/php80/public/channel/.htaccess ]; then
  cp $AMPACHEDIR/php80/public/channel/.htaccess.dist $AMPACHEDIR/php80/public/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php80/public/play/.htaccess.dist $AMPACHEDIR/php80/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php80/public/rest/.htaccess.dist $AMPACHEDIR/php80/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80_squashed/channel/.htaccess ]; then
  cp $AMPACHEDIR/php80_squashed/channel/.htaccess.dist $AMPACHEDIR/php80_squashed/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php80_squashed/play/.htaccess.dist $AMPACHEDIR/php80_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php80_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php80_squashed/rest/.htaccess.dist $AMPACHEDIR/php80_squashed/rest/.htaccess
fi

# php8.1
if [ ! -f $AMPACHEDIR/php81/public/channel/.htaccess ]; then
  cp $AMPACHEDIR/php81/public/channel/.htaccess.dist $AMPACHEDIR/php81/public/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php81/public/play/.htaccess.dist $AMPACHEDIR/php81/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php81/public/rest/.htaccess.dist $AMPACHEDIR/php81/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81_squashed/channel/.htaccess ]; then
  cp $AMPACHEDIR/php81_squashed/channel/.htaccess.dist $AMPACHEDIR/php81_squashed/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php81_squashed/play/.htaccess.dist $AMPACHEDIR/php81_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php81_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php81_squashed/rest/.htaccess.dist $AMPACHEDIR/php81_squashed/rest/.htaccess
fi

# php8.2
if [ ! -f $AMPACHEDIR/php82/public/channel/.htaccess ]; then
  cp $AMPACHEDIR/php82/public/channel/.htaccess.dist $AMPACHEDIR/php82/public/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82/public/play/.htaccess ]; then
  cp $AMPACHEDIR/php82/public/play/.htaccess.dist $AMPACHEDIR/php82/public/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82/public/rest/.htaccess ]; then
  cp $AMPACHEDIR/php82/public/rest/.htaccess.dist $AMPACHEDIR/php82/public/rest/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82_squashed/channel/.htaccess ]; then
  cp $AMPACHEDIR/php82_squashed/channel/.htaccess.dist $AMPACHEDIR/php82_squashed/channel/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82_squashed/play/.htaccess ]; then
  cp $AMPACHEDIR/php82_squashed/play/.htaccess.dist $AMPACHEDIR/php82_squashed/play/.htaccess
fi
if [ ! -f $AMPACHEDIR/php82_squashed/rest/.htaccess ]; then
  cp $AMPACHEDIR/php82_squashed/rest/.htaccess.dist $AMPACHEDIR/php82_squashed/rest/.htaccess
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
cd $AMPACHEDIR/php82 && php8.1 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php82_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php82_squashed/composer.lock
fi
cd $AMPACHEDIR/php82 && php8.1 $COMPOSERPATH install && cd $AMPACHEDIR

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
