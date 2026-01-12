#!/bin/sh
RELEASEBRANCH="patch7"
SQUASHBRANCH="squashed7"
CLIENTBRANCH="client7"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"
LOCALIP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
DATABASE="ampachetest7"
AMPACHEPASSWORD="]@zRGb_Rs2i'XVc"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch7/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

APIVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch7/src/Module/Api/Api.php`
if [ ! $# -eq 0 ]; then
  APIVERSION=$1
fi

cat /dev/null > $AMPACHEDIR/docker/log/7php82.log
cat /dev/null > $AMPACHEDIR/docker/log/7php82s.log
cat /dev/null > $AMPACHEDIR/docker/log/7php82c.log
cat /dev/null > $AMPACHEDIR/docker/log/7php83.log
cat /dev/null > $AMPACHEDIR/docker/log/7php83s.log
cat /dev/null > $AMPACHEDIR/docker/log/7php83c.log
cat /dev/null > $AMPACHEDIR/docker/log/7php84.log
cat /dev/null > $AMPACHEDIR/docker/log/7php84s.log
cat /dev/null > $AMPACHEDIR/docker/log/7php84c.log
#cat /dev/null > $AMPACHEDIR/docker/log/7php85.log
#cat /dev/null > $AMPACHEDIR/docker/log/7php85s.log
#cat /dev/null > $AMPACHEDIR/docker/log/7php85c.log

echo "Enter your local database user:"
read DATABASEUSER
echo "Enter your local database password:"
read DATABASEPASSWORD

# Shutdown stack

docker-compose -p "release-test7" down -v

if [ ! -d $AMPACHEDIR/release-test ]; then
  mkdir $AMPACHEDIR/release-test
fi
if [ ! -d $AMPACHEDIR/release-test/7 ]; then
  mkdir $AMPACHEDIR/release-test/7
fi

# remove the old release
sudo rm -rf $AMPACHEDIR/release-test/7/php*

# php8.2
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d $AMPACHEDIR/release-test/7/php82
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2_squashed.zip -d $AMPACHEDIR/release-test/7/php82_squashed
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2_client.zip -d $AMPACHEDIR/release-test/7/php82_client

# php8.3
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip -d $AMPACHEDIR/release-test/7/php83
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3_squashed.zip -d $AMPACHEDIR/release-test/7/php83_squashed
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3_client.zip -d $AMPACHEDIR/release-test/7/php83_client

# php8.4
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.4.zip -d $AMPACHEDIR/release-test/7/php84
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.4_squashed.zip -d $AMPACHEDIR/release-test/7/php84_squashed
unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.4_client.zip -d $AMPACHEDIR/release-test/7/php84_client

# php8.5
#unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.4.zip -d $AMPACHEDIR/release-test/7/php85
#unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.4_squashed.zip -d $AMPACHEDIR/release-test/7/php85_squashed
#unzip -oq $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.4_client.zip -d $AMPACHEDIR/release-test/7/php85_client

# reset perms

sudo chown -R $UID:33 $AMPACHEDIR/docker/media
sudo chmod -R 775 $AMPACHEDIR/docker/media

# php8.2
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php82/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php82/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php82_squashed/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php82_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82_squashed/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php82_client/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php82_client/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82_client/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82_client/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82_client/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82_client/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php82_client/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php82_client/

# php8.3
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php83/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83_squashed/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php83_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83_squashed/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83_client/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php83_client/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83_client/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83_client/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83_client/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83_client/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php83_client/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php83_client/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83
sudo chmod 775 $AMPACHEDIR/release-test/7/php83
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83_squashed
sudo chmod 775 $AMPACHEDIR/release-test/7/php83_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83_client
sudo chmod 775 $AMPACHEDIR/release-test/7/php83_client
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83
sudo chmod 775 $AMPACHEDIR/release-test/7/php83
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83_squashed
sudo chmod 775 $AMPACHEDIR/release-test/7/php83_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php83_client
sudo chmod 775 $AMPACHEDIR/release-test/7/php83_client

# php8.4
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php84/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84_squashed/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php84_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84_squashed/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84_client/composer.json
sudo chmod 775 $AMPACHEDIR/release-test/7/php84_client/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84_client/config
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84_client/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84_client/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84_client/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php84_client/
sudo chmod -R 775 $AMPACHEDIR/release-test/7/php84_client/

sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84
sudo chmod 775 $AMPACHEDIR/release-test/7/php84
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84_squashed
sudo chmod 775 $AMPACHEDIR/release-test/7/php84_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84_client
sudo chmod 775 $AMPACHEDIR/release-test/7/php84_client
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84
sudo chmod 775 $AMPACHEDIR/release-test/7/php84
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84_squashed
sudo chmod 775 $AMPACHEDIR/release-test/7/php84_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/7/php84_client
sudo chmod 775 $AMPACHEDIR/release-test/7/php84_client

# php8.5
#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85/composer.json
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85/composer.json
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85/config
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85/config
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85/vendor/
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85/vendor/
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85/public/
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85/public/

#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85_squashed/composer.json
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85_squashed/composer.json
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85_squashed/config
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85_squashed/config
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85_squashed/vendor/
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85_squashed/vendor/
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85_squashed/
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85_squashed/

#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85_client/composer.json
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85_client/composer.json
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85_client/config
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85_client/config
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85_client/vendor/
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85_client/vendor/
#sudo chown -R $UID:33 $AMPACHEDIR/release-test/7/php85_client/
#sudo chmod -R 775 $AMPACHEDIR/release-test/7/php85_client/

#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85
#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85_squashed
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85_squashed
#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85_client
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85_client
#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85
#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85_squashed
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85_squashed
#sudo chown $UID:33 $AMPACHEDIR/release-test/7/php85_client
#sudo chmod 775 $AMPACHEDIR/release-test/7/php85_client

# ReLaunch all the containers

docker-compose -p "release-test7" \
 -f docker/test7-docker-compose82.yml -f docker/test7-docker-compose82_squashed.yml -f docker/test7-docker-compose82_client.yml \
 -f docker/test7-docker-compose83.yml -f docker/test7-docker-compose83_squashed.yml -f docker/test7-docker-compose83_client.yml \
 -f docker/test7-docker-compose84.yml -f docker/test7-docker-compose84_squashed.yml -f docker/test7-docker-compose84_client.yml \
 up -d --build
 #-f docker/test7-docker-compose85.yml -f docker/test7-docker-compose85_squashed.yml -f docker/test7-docker-compose85_client.yml \

# Install DB and add the admin user

USERCOMMAND="php /var/www/html/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/bin/cli admin:updateDatabase -e"

echo "INSTALLING PUBLIC AMPACHE on PHP8.2"

# php8.2
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache82-1 ${INSTALLCOMMAND}82
docker exec -u root -it release-test7-test7ampache82-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache82-1 ${UPDATEDBCOMMAND}

echo "INSTALLING PUBLIC AMPACHE on PHP8.3"

# php8.3
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache83-1 ${INSTALLCOMMAND}83
docker exec -u root -it release-test7-test7ampache83-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache83-1 ${UPDATEDBCOMMAND}

echo "INSTALLING PUBLIC AMPACHE on PHP8.4"

# php8.4
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}84 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache84-1 ${INSTALLCOMMAND}84
docker exec -u root -it release-test7-test7ampache84-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache84-1 ${UPDATEDBCOMMAND}

echo "INSTALLING PUBLIC AMPACHE on PHP8.5"

# php8.5
#INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}85 -p $DATABASE -d $DATABASE"
#docker exec -u root -it release-test7-test7ampache85-1 ${INSTALLCOMMAND}85
#docker exec -u root -it release-test7-test7ampache85-1 ${USERCOMMAND}
#docker exec -u root -it release-test7-test7ampache85-1 ${UPDATEDBCOMMAND}

USERCOMMAND="php /var/www/html/public/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/public/bin/cli admin:updateDatabase -e"

echo "INSTALLING SQUASHED AMPACHE on PHP8.2"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache82_squashed-1 ${INSTALLCOMMAND}82s
docker exec -u root -it release-test7-test7ampache82_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache82_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.3"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache83_squashed-1 ${INSTALLCOMMAND}83s
docker exec -u root -it release-test7-test7ampache83_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache83_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.4"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}84s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache84_squashed-1 ${INSTALLCOMMAND}84s
docker exec -u root -it release-test7-test7ampache84_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache84_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.5"

#INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}85s -p $DATABASE -d $DATABASE"
#docker exec -u root -it release-test7-test7ampache85_squashed-1 ${INSTALLCOMMAND}85s
#docker exec -u root -it release-test7-test7ampache85_squashed-1 ${USERCOMMAND}
#docker exec -u root -it release-test7-test7ampache85_squashed-1 ${UPDATEDBCOMMAND}

USERCOMMAND="php /var/www/html/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/bin/cli admin:updateDatabase -e"

echo "INSTALLING CLIENT AMPACHE on PHP8.2"

INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82c -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache82_client-1 ${INSTALLCOMMAND}82c
docker exec -u root -it release-test7-test7ampache82_client-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache82_client-1 ${UPDATEDBCOMMAND}

echo "INSTALLING CLIENT AMPACHE on PHP8.3"

INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83c -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache83_client-1 ${INSTALLCOMMAND}83c
docker exec -u root -it release-test7-test7ampache83_client-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache83_client-1 ${UPDATEDBCOMMAND}

echo "INSTALLING CLIENT AMPACHE on PHP8.4"

INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}84c -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test7-test7ampache84_client-1 ${INSTALLCOMMAND}84c
docker exec -u root -it release-test7-test7ampache84_client-1 ${USERCOMMAND}
docker exec -u root -it release-test7-test7ampache84_client-1 ${UPDATEDBCOMMAND}

echo "INSTALLING CLIENT AMPACHE on PHP8.5"

#INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}85c -p $DATABASE -d $DATABASE"
#docker exec -u root -it release-test7-test7ampache85_client-1 ${INSTALLCOMMAND}85c
#docker exec -u root -it release-test7-test7ampache85_client-1 ${USERCOMMAND}
#docker exec -u root -it release-test7-test7ampache85_client-1 ${UPDATEDBCOMMAND}

sed -i "s/session_name = \"ampache\"/session_name = \"7php82\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php82squashed\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php82client\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php83\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php83squashed\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php83client\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php84\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php84squashed\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"7php84client\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/session_name = \"ampache\"/session_name = \"7php85\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/session_name = \"ampache\"/session_name = \"7php85squashed\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/session_name = \"ampache\"/session_name = \"7php85client\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php82.log\"/g"   $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php82s.log\"/g"   $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php82c.log\"/g"   $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php83.log\"/g"   $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php83s.log\"/g"   $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php83c.log\"/g"   $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php84.log\"/g"   $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php84s.log\"/g"   $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php84c.log\"/g"   $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php85.log\"/g"   $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php85s.log\"/g"   $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php85c.log\"/g"   $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php82/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php82_client/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php83/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php83_client/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php84/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php84_client/config/ampache.cfg.php
#sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php85/config/ampache.cfg.php
#sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_squashed/config/ampache.cfg.php
#sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/7/php85_client/config/ampache.cfg.php

echo
#release-test7-test7ampache82
cat /dev/null > $AMPACHEDIR/docker/log/7php82.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18280 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION ampache82 $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18280 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18280 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7ampache82_squashed
cat /dev/null > $AMPACHEDIR/docker/log/7php82s.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18281 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION ampache82_squashed $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18281 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18281 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7php82_client
cat /dev/null > $AMPACHEDIR/docker/log/7php82c.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18282 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION php82_client $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18282 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18282 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7ampache83
cat /dev/null > $AMPACHEDIR/docker/log/7php83.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18380 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION ampache83 $DEMOPASSWORD"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18380 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7ampache83_squashed
cat /dev/null > $AMPACHEDIR/docker/log/7php83s.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18381 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION ampache83_squashed $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18381 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18381 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7php83_client
cat /dev/null > $AMPACHEDIR/docker/log/7php83c.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18382 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION php83_client $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18382 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18382 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7ampache84
cat /dev/null > $AMPACHEDIR/docker/log/7php84.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18480 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION ampache84 - $DEMOPASSWORD -"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18482 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18480 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7ampache84_squashed
cat /dev/null > $AMPACHEDIR/docker/log/7php84s.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18481 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION ampache84_squashed $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18482 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18481 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7php84_client
cat /dev/null > $AMPACHEDIR/docker/log/7php84c.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18482 admin $AMPACHEPASSWORD)
echo "Testing $RELEASEVERSION php84_client $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18482 $AMPACHEPASSWORD admin 1 $APIVERSION"
python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18482 $AMPACHEPASSWORD admin 1 $APIVERSION
echo
#release-test7-test7ampache85
#cat /dev/null > $AMPACHEDIR/docker/log/7php85.log
#DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18580 admin $AMPACHEPASSWORD)
#echo "Testing $RELEASEVERSION ampache85 - $DEMOPASSWORD -"
#echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18582 $AMPACHEPASSWORD admin 1 $APIVERSION"
#python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18580 $AMPACHEPASSWORD admin 1 $APIVERSION
#echo
#release-test7-test7ampache85_squashed
#cat /dev/null > $AMPACHEDIR/docker/log/7php85s.log
#DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18581 admin $AMPACHEPASSWORD)
#echo "Testing $RELEASEVERSION ampache85_squashed $DEMOPASSWORD"
#echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18582 $AMPACHEPASSWORD admin 1 $APIVERSION"
#python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18581 $AMPACHEPASSWORD admin 1 $APIVERSION
#echo
#release-test7-test7php85_client
#cat /dev/null > $AMPACHEDIR/docker/log/7php85c.log
#DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18582 admin $AMPACHEPASSWORD)
#echo "Testing $RELEASEVERSION php85_client $DEMOPASSWORD"
#echo "python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18582 $AMPACHEPASSWORD admin 1 $APIVERSION"
#python3 $AMPACHEDIR/python/build_all7.py http://${LOCALIP}:18582 $AMPACHEPASSWORD admin 1 $APIVERSION


echo "PRINT ERRORS"
cat $AMPACHEDIR/docker/log/7*.log | grep Error

echo
echo "DOCKER APACHE ERRORS LOG"
echo
echo "test7ampache82"
docker exec -u root -it release-test7-test7ampache82-1 cat /var/log/apache2/error.log
echo
echo "test7ampache83"
docker exec -u root -it release-test7-test7ampache83-1 cat /var/log/apache2/error.log
echo
echo "test7ampache84"
docker exec -u root -it release-test7-test7ampache84-1 cat /var/log/apache2/error.log
echo
#echo "test7ampache85"
#docker exec -u root -it release-test7-test7ampache85-1 cat /var/log/apache2/error.log
#echo
echo "test7ampache82_squashed"
docker exec -u root -it release-test7-test7ampache82_squashed-1 cat /var/log/apache2/error.log
echo
echo "test7ampache83_squashed"
docker exec -u root -it release-test7-test7ampache83_squashed-1 cat /var/log/apache2/error.log
echo
echo "test7ampache84_squashed"
docker exec -u root -it release-test7-test7ampache84_squashed-1 cat /var/log/apache2/error.log
echo
#echo "test7ampache85_squashed"
#docker exec -u root -it release-test7-test7ampache85_squashed-1 cat /var/log/apache2/error.log
#echo
echo "test7ampache82_client"
docker exec -u root -it release-test7-test7ampache82_client-1 cat /var/log/apache2/error.log
echo
echo "test7ampache83_client"
docker exec -u root -it release-test7-test7ampache83_client-1 cat /var/log/apache2/error.log
echo
echo "test7ampache84_client"
docker exec -u root -it release-test7-test7ampache84_client-1 cat /var/log/apache2/error.log
echo
#echo "test7ampache85_client"
#docker exec -u root -it release-test7-test7ampache85_client-1 cat /var/log/apache2/error.log

