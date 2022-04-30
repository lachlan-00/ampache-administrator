#!/bin/sh

AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

# create the htaccess files
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

# create the docker volume folders
if [ ! -d $AMPACHEDIR/docker/log ]; then
  mkdir $AMPACHEDIR/docker/log
fi
if [ ! -d $AMPACHEDIR/docker/media ]; then
  mkdir $AMPACHEDIR/docker/media
fi

# reset perms
chown $UID:33 $AMPACHEDIR/docker/log
chmod 775 $AMPACHEDIR/docker/log

chown $UID:33 $AMPACHEDIR/docker/media
chmod 775 $AMPACHEDIR/docker/media

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

# remove the lock and install composer packages
if [ -f $AMPACHEDIR/php74/composer.lock ]; then
  rm $AMPACHEDIR/php74/composer.lock
fi
cd $AMPACHEDIR/php74 && php7.4 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php74_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php74_squashed/composer.lock
fi
cd $AMPACHEDIR/php74_squashed && php7.4 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php80/composer.lock ]; then
  rm $AMPACHEDIR/php80/composer.lock
fi
cd $AMPACHEDIR/php80 && php8.0 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php80_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php80_squashed/composer.lock
fi
cd $AMPACHEDIR/php80 && php8.0 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php81/composer.lock ]; then
  rm $AMPACHEDIR/php81/composer.lock
fi
cd $AMPACHEDIR/php80 && php8.1 $COMPOSERPATH install && cd $AMPACHEDIR
if [ -f $AMPACHEDIR/php81_squashed/composer.lock ]; then
  rm $AMPACHEDIR/php81_squashed/composer.lock
fi
cd $AMPACHEDIR/php80 && php8.1 $COMPOSERPATH install && cd $AMPACHEDIR


chown $UID:33 $AMPACHEDIR/docker/log
chmod 775 $AMPACHEDIR/docker/log
chown $UID:33 $AMPACHEDIR/docker/media
chmod 775 $AMPACHEDIR/docker/media

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
