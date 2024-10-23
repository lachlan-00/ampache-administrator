#!/bin/sh
RELEASEBRANCH="patch6"
SQUASHBRANCH="squashed6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"
LOCALIP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
DATABASE="ampachetest6"
AMPACHEPASSWORD="]@zRGb_Rs2i'XVc"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch6/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

echo "Enter your local database user:"
read DATABASEUSER
echo "Enter your local database password:"
read DATABASEPASSWORD

# Shutdown stack

docker-compose -p "release-test6" down -v

if [ ! -d $AMPACHEDIR/release-test ]; then
  mkdir $AMPACHEDIR/release-test
fi
if [ ! -d $AMPACHEDIR/release-test/6 ]; then
  mkdir $AMPACHEDIR/release-test/6
fi

# remove the old release
rm -rf $AMPACHEDIR/release-test/6/php*

# php7.4
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip -d $AMPACHEDIR/release-test/6/php74
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip -d $AMPACHEDIR/release-test/6/php74_squashed

# php8.0
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip -d $AMPACHEDIR/release-test/6/php80
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip -d $AMPACHEDIR/release-test/6/php80_squashed

# php8.1
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip -d $AMPACHEDIR/release-test/6/php81
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip -d $AMPACHEDIR/release-test/6/php81_squashed

# php8.2
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d $AMPACHEDIR/release-test/6/php82
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d $AMPACHEDIR/release-test/6/php82_squashed

# php8.3
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip -d $AMPACHEDIR/release-test/6/php83
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.3.zip -d $AMPACHEDIR/release-test/6/php83_squashed

# reset perms

sudo chown -R $UID:33 $AMPACHEDIR/docker/media
sudo chmod -R 775 $AMPACHEDIR/docker/media
sudo chown $UID:33 $AMPACHEDIR/docker/log/*
sudo chmod 775 $AMPACHEDIR/docker/log/*

# php7.4
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php74/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php74/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php74/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php74/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php74/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php74/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php74/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php74/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/6/php74_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php74_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php74_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php74_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php74_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php74_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php74_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php74_squashed/

# php8.0
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php80/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php80/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php80/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php80/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php80/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php80/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php80/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php80/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/6/php80_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php80_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php80_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php80_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php80_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php80_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php80_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php80_squashed/

# php8.1
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php81/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php81/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php81/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php81/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php81/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php81/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php81/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php81/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/6/php81_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php81_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php81_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php81_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php81_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php81_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php81_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php81_squashed/

# php8.2
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php82/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php82/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php82/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php82/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php82/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php82/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php82/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php82/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/6/php82_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php82_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php82_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php82_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php82_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php82_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php82_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php82_squashed/

# php8.3
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php83/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php83/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php83/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php83/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php83/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php83/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php83/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php83/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/6/php83_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/6/php83_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php83_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php83_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php83_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php83_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/6/php83_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/6/php83_squashed/

sudo chown $UID:33 $AMPACHEDIR/release-test/6/php74
sudo sudo chmod 775 $AMPACHEDIR/release-test/6/php74
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php74_squashed
sudo chmod 775 $AMPACHEDIR/release-test/6/php74_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php80
sudo chmod 775 $AMPACHEDIR/release-test/6/php80
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php80_squashed
sudo chmod 775 $AMPACHEDIR/release-test/6/php80_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php81
sudo chmod 775 $AMPACHEDIR/release-test/6/php81
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php81_squashed
sudo chmod 775 $AMPACHEDIR/release-test/6/php81_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php82
sudo chmod 775 $AMPACHEDIR/release-test/6/php82
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php82_squashed
sudo chmod 775 $AMPACHEDIR/release-test/6/php82_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php83
sudo chmod 775 $AMPACHEDIR/release-test/6/php83
sudo chown $UID:33 $AMPACHEDIR/release-test/6/php83_squashed
sudo chmod 775 $AMPACHEDIR/release-test/6/php83_squashed

# ReLaunch all the containers

docker-compose -p "release-test6" \
 -f docker/test-docker-compose74.yml -f docker/test-docker-compose74_squashed.yml \
 -f docker/test-docker-compose80.yml -f docker/test-docker-compose80_squashed.yml \
 -f docker/test-docker-compose81.yml -f docker/test-docker-compose81_squashed.yml \
 -f docker/test-docker-compose82.yml -f docker/test-docker-compose82_squashed.yml \
 -f docker/test-docker-compose83.yml -f docker/test-docker-compose83_squashed.yml \
 up -d --build

# Install DB and add the admin user

USERCOMMAND="php /var/www/html/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/bin/cli admin:updateDatabase -e"

echo "INSTALLING AMPACHE on PHP7.4"

# php7.4
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}74 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache74-1 ${INSTALLCOMMAND}74
docker exec -u root -it release-test6-testampache74-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache74-1 ${UPDATEDBCOMMAND}


echo "INSTALLING AMPACHE on PHP8.0"

# php8.0
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}80 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache80-1 ${INSTALLCOMMAND}80
docker exec -u root -it release-test6-testampache80-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache80-1 ${UPDATEDBCOMMAND}

echo "INSTALLING AMPACHE on PHP8.1"

# php8.1
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}81 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache81-1 ${INSTALLCOMMAND}81
docker exec -u root -it release-test6-testampache81-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache81-1 ${UPDATEDBCOMMAND}

echo "INSTALLING AMPACHE on PHP8.2"

# php8.2
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache82-1 ${INSTALLCOMMAND}82
docker exec -u root -it release-test6-testampache82-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache82-1 ${UPDATEDBCOMMAND}

echo "INSTALLING AMPACHE on PHP8.3"

# php8.3
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache83-1 ${INSTALLCOMMAND}83
docker exec -u root -it release-test6-testampache83-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache83-1 ${UPDATEDBCOMMAND}

USERCOMMAND="php /var/www/html/public/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/public/bin/cli admin:updateDatabase -e"

echo "INSTALLING SQUASHED AMPACHE on PHP7.4"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}74s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache74_squashed-1 ${INSTALLCOMMAND}74s
docker exec -u root -it release-test6-testampache74_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache74_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.0"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}80s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache80_squashed-1 ${INSTALLCOMMAND}80s
docker exec -u root -it release-test6-testampache80_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache80_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.1"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}81s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache81_squashed-1 ${INSTALLCOMMAND}81s
docker exec -u root -it release-test6-testampache81_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache81_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.2"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache82_squashed-1 ${INSTALLCOMMAND}82s
docker exec -u root -it release-test6-testampache82_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache82_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.3"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test6-testampache83_squashed-1 ${INSTALLCOMMAND}83s
docker exec -u root -it release-test6-testampache83_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test6-testampache83_squashed-1 ${UPDATEDBCOMMAND}

sed -i "s/session_name = \"ampache\"/session_name = \"6php74\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php74_squashed\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php80\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php80_squashed\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php81\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php81_squashed\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php82\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php82_squashed\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php83\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"6php83_squashed\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php


sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php74.log\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php74s.log\"/g"   $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php80.log\"/g"   $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php80s.log\"/g"   $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php81.log\"/g"   $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php81s.log\"/g"   $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php82.log\"/g"   $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php82s.log\"/g"   $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php83.log\"/g"   $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"6php83s.log\"/g"   $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php

sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php74/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php74_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php80/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php80_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php81/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php81_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php82/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php82_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php83/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/6/php83_squashed/config/ampache.cfg.php
echo
echo "Testing $RELEASEVERSION ampache74"
#release-test6-testampache74
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:17480 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:17480 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache74_squashed"
#release-test6-testampache74_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:17481 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:17481 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache80"
#release-test6-testampache80
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18080 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18080 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache80_squashed"
#release-test6-testampache80_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18081 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18081 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache81"
#release-test6-testampache81
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18180 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18180 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache81_squashed"
#release-test6-testampache81_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18181 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18181 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache82"
#release-test6-testampache82
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18280 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18280 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache82_squashed"
#release-test6-testampache82_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18281 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18281 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache83"
#release-test6-testampache83
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18380 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18380 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache83_squashed"
#release-test6-testampache83_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18381 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18381 $DEMOPASSWORD admin 1 $RELEASEVERSION


