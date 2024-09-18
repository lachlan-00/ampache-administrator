#!/bin/sh
RELEASEBRANCH="patch7"
SQUASHBRANCH="squashed7"
CLIENTBRANCH="client"
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

echo "Enter your local database user:"
read DATABASEUSER
echo "Enter your local database password:"
read DATABASEPASSWORD

# Shutdown stack

docker-compose -p "release-test" down -v

# remove the old release
rm -rf $AMPACHEDIR/release-test/php*

# php8.2
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d $AMPACHEDIR/release-test/php82
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d $AMPACHEDIR/release-test/php82_squashed
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_client_php8.2.zip -d $AMPACHEDIR/release-test/php82_client

# php8.3
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.3.zip -d $AMPACHEDIR/release-test/php83
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.3.zip -d $AMPACHEDIR/release-test/php83_squashed
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_client_php8.3.zip -d $AMPACHEDIR/release-test/php83_client

# reset perms

sudo chown -R $UID:33 $AMPACHEDIR/docker/media
sudo chmod -R 775 $AMPACHEDIR/docker/media

# php8.2
sudo chown $UID:33 $AMPACHEDIR/release-test/php82/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/php82/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82/config
sudo chmod -R 775 $AMPACHEDIR/release-test/php82/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/php82/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/php82/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/php82_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/php82_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/

sudo chown $UID:33 $AMPACHEDIR/release-test/php82_client/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/php82_client/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82_client/config
sudo chmod -R 775 $AMPACHEDIR/release-test/php82_client/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82_client/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/php82_client/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php82_client/
sudo chmod -R 775 $AMPACHEDIR/release-test/php82_client/

# php8.3
sudo chown $UID:33 $AMPACHEDIR/release-test/php83/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/php83/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83/config
sudo chmod -R 775 $AMPACHEDIR/release-test/php83/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/php83/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83/public/
sudo chmod -R 775 $AMPACHEDIR/release-test/php83/public/

sudo chown $UID:33 $AMPACHEDIR/release-test/php83_squashed/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/php83_squashed/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83_squashed/config
sudo chmod -R 775 $AMPACHEDIR/release-test/php83_squashed/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83_squashed/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/php83_squashed/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83_squashed/
sudo chmod -R 775 $AMPACHEDIR/release-test/php83_squashed/

sudo chown $UID:33 $AMPACHEDIR/release-test/php83_client/composer.json 
sudo chmod 775 $AMPACHEDIR/release-test/php83_client/composer.json
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83_client/config
sudo chmod -R 775 $AMPACHEDIR/release-test/php83_client/config
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83_client/vendor/
sudo chmod -R 775 $AMPACHEDIR/release-test/php83_client/vendor/
sudo chown -R $UID:33 $AMPACHEDIR/release-test/php83_client/
sudo chmod -R 775 $AMPACHEDIR/release-test/php83_client/

sudo chown $UID:33 $AMPACHEDIR/release-test/php82
sudo chmod 775 $AMPACHEDIR/release-test/php82
sudo chown $UID:33 $AMPACHEDIR/release-test/php82_squashed
sudo chmod 775 $AMPACHEDIR/release-test/php82_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/php82_client
sudo chmod 775 $AMPACHEDIR/release-test/php82_client
sudo chown $UID:33 $AMPACHEDIR/release-test/php83
sudo chmod 775 $AMPACHEDIR/release-test/php83
sudo chown $UID:33 $AMPACHEDIR/release-test/php83_squashed
sudo chmod 775 $AMPACHEDIR/release-test/php83_squashed
sudo chown $UID:33 $AMPACHEDIR/release-test/php83_client
sudo chmod 775 $AMPACHEDIR/release-test/php83_client

# ReLaunch all the containers

docker-compose -p "release-test" \
 -f docker/test7-docker-compose82.yml -f docker/test7-docker-compose82_squashed.yml -f docker/test7-docker-compose82_client.yml \
 -f docker/test7-docker-compose83.yml -f docker/test7-docker-compose83_squashed.yml -f docker/test7-docker-compose83_client.yml \
 up -d --build

# Install DB and add the admin user

USERCOMMAND="php /var/www/html/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/bin/cli admin:updateDatabase -e"

echo "INSTALLING PUBLIC AMPACHE on PHP8.2"

# php8.2
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache82-1 ${INSTALLCOMMAND}82
docker exec -u root -it release-test-testampache82-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache82-1 ${UPDATEDBCOMMAND}

echo "INSTALLING PUBLIC AMPACHE on PHP8.3"

# php8.3
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache83-1 ${INSTALLCOMMAND}83
docker exec -u root -it release-test-testampache83-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache83-1 ${UPDATEDBCOMMAND}

USERCOMMAND="php /var/www/html/public/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/public/bin/cli admin:updateDatabase -e"

echo "INSTALLING SQUASHED AMPACHE on PHP8.2"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache82_squashed-1 ${INSTALLCOMMAND}82s
docker exec -u root -it release-test-testampache82_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache82_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.3"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache83_squashed-1 ${INSTALLCOMMAND}83s
docker exec -u root -it release-test-testampache83_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache83_squashed-1 ${UPDATEDBCOMMAND}

USERCOMMAND="php /var/www/html/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/bin/cli admin:updateDatabase -e"

echo "INSTALLING CLIENT AMPACHE on PHP8.2"

INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82c -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache82_client-1 ${INSTALLCOMMAND}82c
docker exec -u root -it release-test-testampache82_client-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache82_client-1 ${UPDATEDBCOMMAND}

echo "INSTALLING CLIENT AMPACHE on PHP8.3"

INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}83c -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache83_client-1 ${INSTALLCOMMAND}83c
docker exec -u root -it release-test-testampache83_client-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache83_client-1 ${UPDATEDBCOMMAND}

sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;label = \"true\"/label = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php82.log\"/g"   $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php82s.log\"/g"   $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php82c.log\"/g"   $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php83.log\"/g"   $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php83s.log\"/g"   $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"7php83c.log\"/g"   $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/php82_client/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/php83/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/php83_squashed/config/ampache.cfg.php
sed -i "s/;api_debug_handler = \"true\"/api_debug_handler = \"true\"/g"  $AMPACHEDIR/release-test/php83_client/config/ampache.cfg.php

echo
echo "Testing $RELEASEVERSION ampache82"
#release-test-testampache82
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18280 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18280 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache82_squashed"
#release-test-testampache82_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18281 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18281 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION php82_client"
#release-test-testphp82_client
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18282 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18282 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache83"
#release-test-testampache83
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18380 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18380 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION ampache83_squashed"
#release-test-testampache83_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18381 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18381 $DEMOPASSWORD admin 1 $RELEASEVERSION
echo
echo "Testing $RELEASEVERSION php83_client"
#release-test-testphp83_client
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:18382 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all6.py http://${LOCALIP}:18382 $DEMOPASSWORD admin 1 $RELEASEVERSION


