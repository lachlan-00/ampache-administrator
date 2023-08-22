#!/bin/sh
RELEASEBRANCH="patch6"
SQUASHBRANCH="squashed6"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"
LOCALIP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
DATABASE="ampachetest"

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch6/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

LOCALIP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
DATABASE="ampachetest"
AMPACHEPASSWORD="]@zRGb_Rs2i'XVc"

echo "Enter your local database user:"
read DATABASEUSER
echo "Enter your local database password:"
read DATABASEPASSWORD

# Shutdown stack

docker-compose -p "release-test" down -v

# remove the old release

rm -rf $AMPACHEDIR/release-test/php*

# php7.4
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php7.4.zip -d $AMPACHEDIR/release-test/php74
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php7.4.zip -d $AMPACHEDIR/release-test/php74_squashed

# php8.0
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.0.zip -d $AMPACHEDIR/release-test/php80
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.0.zip -d $AMPACHEDIR/release-test/php80_squashed

# php8.1
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.1.zip -d $AMPACHEDIR/release-test/php81
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.1.zip -d $AMPACHEDIR/release-test/php81_squashed

# php8.2
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_php8.2.zip -d $AMPACHEDIR/release-test/php82
unzip $AMPACHEDIR/releases/ampache-${RELEASEVERSION}_all_squashed_php8.2.zip -d $AMPACHEDIR/release-test/php82_squashed

# reset perms

# php7.4
chown $UID:33 $AMPACHEDIR/release-test/php74/composer.json 
chmod 775 $AMPACHEDIR/release-test/php74/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php74/config
chmod -R 775 $AMPACHEDIR/release-test/php74/config
chown -R $UID:33 $AMPACHEDIR/release-test/php74/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php74/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php74/public/
chmod -R 775 $AMPACHEDIR/release-test/php74/public/

chown $UID:33 $AMPACHEDIR/release-test/php74_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php74_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php74_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php74_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php74_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php74_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php74_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php74_squashed/

# php8.0
chown $UID:33 $AMPACHEDIR/release-test/php80/composer.json 
chmod 775 $AMPACHEDIR/release-test/php80/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php80/config
chmod -R 775 $AMPACHEDIR/release-test/php80/config
chown -R $UID:33 $AMPACHEDIR/release-test/php80/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php80/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php80/public/
chmod -R 775 $AMPACHEDIR/release-test/php80/public/

chown $UID:33 $AMPACHEDIR/release-test/php80_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php80_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php80_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php80_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php80_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php80_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php80_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php80_squashed/

# php8.1
chown $UID:33 $AMPACHEDIR/release-test/php81/composer.json 
chmod 775 $AMPACHEDIR/release-test/php81/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php81/config
chmod -R 775 $AMPACHEDIR/release-test/php81/config
chown -R $UID:33 $AMPACHEDIR/release-test/php81/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php81/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php81/public/
chmod -R 775 $AMPACHEDIR/release-test/php81/public/

chown $UID:33 $AMPACHEDIR/release-test/php81_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php81_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php81_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php81_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php81_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php81_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php81_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php81_squashed/

# php8.2
chown $UID:33 $AMPACHEDIR/release-test/php82/composer.json 
chmod 775 $AMPACHEDIR/release-test/php82/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php82/config
chmod -R 775 $AMPACHEDIR/release-test/php82/config
chown -R $UID:33 $AMPACHEDIR/release-test/php82/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php82/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php82/public/
chmod -R 775 $AMPACHEDIR/release-test/php82/public/

chown $UID:33 $AMPACHEDIR/release-test/php82_squashed/composer.json 
chmod 775 $AMPACHEDIR/release-test/php82_squashed/composer.json
chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/config
chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/config
chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/vendor/
chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/vendor/
chown -R $UID:33 $AMPACHEDIR/release-test/php82_squashed/
chmod -R 775 $AMPACHEDIR/release-test/php82_squashed/

chown $UID:33 $AMPACHEDIR/release-test/php74
chmod 775 $AMPACHEDIR/release-test/php74
chown $UID:33 $AMPACHEDIR/release-test/php74_squashed
chmod 775 $AMPACHEDIR/release-test/php74_squashed
chown $UID:33 $AMPACHEDIR/release-test/php80
chmod 775 $AMPACHEDIR/release-test/php80
chown $UID:33 $AMPACHEDIR/release-test/php80_squashed
chmod 775 $AMPACHEDIR/release-test/php80_squashed
chown $UID:33 $AMPACHEDIR/release-test/php81
chmod 775 $AMPACHEDIR/release-test/php81
chown $UID:33 $AMPACHEDIR/release-test/php81_squashed
chmod 775 $AMPACHEDIR/release-test/php81_squashed
chown $UID:33 $AMPACHEDIR/release-test/php82
chmod 775 $AMPACHEDIR/release-test/php82
chown $UID:33 $AMPACHEDIR/release-test/php82_squashed
chmod 775 $AMPACHEDIR/release-test/php82_squashed

# ReLaunch all the containers

docker-compose -p "release-test" -f docker/test-docker-compose74.yml -f docker/test-docker-compose74_squashed.yml -f docker/test-docker-compose80.yml -f docker/test-docker-compose80_squashed.yml -f docker/test-docker-compose81.yml -f docker/test-docker-compose81_squashed.yml -f docker/test-docker-compose82.yml -f docker/test-docker-compose82_squashed.yml up -d --build

# Install DB and add the admin user

USERCOMMAND="php /var/www/html/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/bin/cli admin:updateDatabase -e"

echo "INSTALLING AMPACHE on PHP7.4"

# php7.4
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}74 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache74-1 ${INSTALLCOMMAND}74
docker exec -u root -it release-test-testampache74-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache74-1 ${UPDATEDBCOMMAND}


echo "INSTALLING AMPACHE on PHP8.0"

# php8.0
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}80 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache80-1 ${INSTALLCOMMAND}80
docker exec -u root -it release-test-testampache80-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache80-1 ${UPDATEDBCOMMAND}

echo "INSTALLING AMPACHE on PHP8.1"

# php8.1
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}81 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache81-1 ${INSTALLCOMMAND}81
docker exec -u root -it release-test-testampache81-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache81-1 ${UPDATEDBCOMMAND}

echo "INSTALLING AMPACHE on PHP8.2"

# php8.2
INSTALLCOMMAND="php /var/www/html/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache82-1 ${INSTALLCOMMAND}82
docker exec -u root -it release-test-testampache82-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache82-1 ${UPDATEDBCOMMAND}

USERCOMMAND="php /var/www/html/public/bin/cli admin:addUser admin -p $AMPACHEPASSWORD -e admin@ampache.dev -l 100"
UPDATEDBCOMMAND="php /var/www/html/public/bin/cli admin:updateDatabase -e"

echo "INSTALLING SQUASHED AMPACHE on PHP7.4"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}74s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache74_squashed-1 ${INSTALLCOMMAND}74s
docker exec -u root -it release-test-testampache74_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache74_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.0"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}80s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache80_squashed-1 ${INSTALLCOMMAND}80s
docker exec -u root -it release-test-testampache80_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache80_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.1"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}81s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache81_squashed-1 ${INSTALLCOMMAND}81s
docker exec -u root -it release-test-testampache81_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache81_squashed-1 ${UPDATEDBCOMMAND}

echo "INSTALLING SQUASHED AMPACHE on PHP8.2"

INSTALLCOMMAND="php /var/www/html/public/bin/installer install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}82s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test-testampache82_squashed-1 ${INSTALLCOMMAND}82s
docker exec -u root -it release-test-testampache82_squashed-1 ${USERCOMMAND}
docker exec -u root -it release-test-testampache82_squashed-1 ${UPDATEDBCOMMAND}

sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php74/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php74_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php80/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php80_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php81/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php81_squashed/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/;debug = \"true\"/debug = \"true\"/g"  $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
 = "%name.%Y%m%d.log"
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php74.log\"/g"  $AMPACHEDIR/release-test/php74/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php74s.log\"/g"   $AMPACHEDIR/release-test/php74_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php80.log\"/g"   $AMPACHEDIR/release-test/php80/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php80s.log\"/g"   $AMPACHEDIR/release-test/php80_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php81.log\"/g"   $AMPACHEDIR/release-test/php81/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php81s.log\"/g"   $AMPACHEDIR/release-test/php81_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php82.log\"/g"   $AMPACHEDIR/release-test/php82/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"php82s.log\"/g"   $AMPACHEDIR/release-test/php82_squashed/config/ampache.cfg.php
echo
echo "Testing $RELEASEVERSION ampache74"
#release-test-testampache74
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:17480 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:17480 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache74_squashed"
#release-test-testampache74_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:17481 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:17481 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache80"
#release-test-testampache80
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:18080 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:18080 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache80_squashed"
#release-test-testampache80_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:18081 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:18081 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache81"
#release-test-testampache81
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:18180 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:18180 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache81_squashed"
#release-test-testampache81_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:18181 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:18181 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache82"
#release-test-testampache82
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:18280 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:18280 $DEMOPASSWORD admin 1
echo
echo "Testing $RELEASEVERSION ampache82_squashed"
#release-test-testampache82_squashed
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test.py http://${LOCALIP}:18281 admin $AMPACHEPASSWORD)
python3 $AMPACHEDIR/python/build_all.py http://${LOCALIP}:18281 $DEMOPASSWORD admin 1

