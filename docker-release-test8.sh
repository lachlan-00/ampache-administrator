#!/bin/sh
RELEASEBRANCH="patch8"
SQUASHBRANCH="squashed8"
CLIENTBRANCH="client8"
AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"
LOCALIP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
DATABASE="ampachetest8"
AMPACHEPASSWORD="]@zRGb_Rs2i'XVc"

# Ampache 8 requires PHP 8.5+ (composer.json "php": ">=8.5") and build_release8.sh only produces php8.5
# zips, so there is one build per structure: public, squashed and client.
PORTPUBLIC=18580
PORTSQUASHED=18581
PORTCLIENT=18582

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch8/src/Config/Init/InitializationHandlerConfig.php`
if [ ! $# -eq 0 ]; then
  RELEASEVERSION=$1
fi

APIVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' $AMPACHEDIR/ampache-patch8/src/Module/Api/Api.php`
if [ ! $# -eq 0 ]; then
  APIVERSION=$1
fi

cat /dev/null > $AMPACHEDIR/docker/log/8php85.log
cat /dev/null > $AMPACHEDIR/docker/log/8php85s.log
cat /dev/null > $AMPACHEDIR/docker/log/8php85c.log

echo "Enter your local database user:"
read DATABASEUSER
echo "Enter your local database password:"
read DATABASEPASSWORD

# Shutdown stack

docker-compose -p "release-test8" down -v

if [ ! -d $AMPACHEDIR/release-test ]; then
  mkdir $AMPACHEDIR/release-test
fi
if [ ! -d $AMPACHEDIR/release-test/8 ]; then
  mkdir $AMPACHEDIR/release-test/8
fi

# remove the old release
sudo rm -rf $AMPACHEDIR/release-test/8/php*

# Unpack the three php8.5 release zips, one per structure. Abort rather than test a stale unpack when a zip
# is missing: the containers would otherwise come up on whatever the previous run left behind, and pass.
for ZIP in \
  "ampache-${RELEASEVERSION}_all_php8.5.zip:php85" \
  "ampache-${RELEASEVERSION}_all_php8.5_squashed.zip:php85_squashed" \
  "ampache-${RELEASEVERSION}_all_php8.5_client.zip:php85_client"
do
  FILE=`echo "$ZIP" | cut -d: -f1`
  DEST=`echo "$ZIP" | cut -d: -f2`
  if [ ! -f "$AMPACHEDIR/releases/$FILE" ]; then
    echo "ERROR: missing release zip $AMPACHEDIR/releases/$FILE"
    echo "       run ./build_release8.sh $RELEASEVERSION first"
    exit 1
  fi
  unzip -oq "$AMPACHEDIR/releases/$FILE" -d "$AMPACHEDIR/release-test/8/$DEST"
done

# reset perms

sudo chown -R $UID:33 $AMPACHEDIR/docker/media
sudo chmod -R 775 $AMPACHEDIR/docker/media

sudo chown -R $UID:33 $AMPACHEDIR/docker/log
sudo chmod -R 775 $AMPACHEDIR/docker/log

for DEST in php85 php85_squashed php85_client; do
  sudo chown -R $UID:33 $AMPACHEDIR/release-test/8/$DEST
  sudo chmod -R 775 $AMPACHEDIR/release-test/8/$DEST
done

# ReLaunch all the containers

docker-compose -p "release-test8" \
 -f docker/test8-docker-compose85.yml -f docker/test8-docker-compose85_squashed.yml -f docker/test8-docker-compose85_client.yml \
 up -d --build

# Install DB and add the admin user
#
# Each structure gets its own database and its own ampache db user so the three installs cannot see each
# other's data. The suffix is appended to the whole command (`${INSTALLCOMMAND}85c`) so the trailing
# `-d $DATABASE` picks it up as well as the `-u` that already carries it inline.

# public and client keep bin/ at the repo root; squashed lifts the web root, so bin/ sits under public/
CLICOMMANDROOT="php /var/www/html/bin/cli"
CLICOMMANDSQUASHED="php /var/www/html/public/bin/cli"
INSTALLERROOT="php /var/www/html/bin/installer"
INSTALLERSQUASHED="php /var/www/html/public/bin/installer"

echo "INSTALLING PUBLIC AMPACHE on PHP8.5"

INSTALLCOMMAND="$INSTALLERROOT install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}85 -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test8-test8ampache85-1 ${INSTALLCOMMAND}85
docker exec -u root -it release-test8-test8ampache85-1 $CLICOMMANDROOT admin:addUser admin -p "$AMPACHEPASSWORD" -e admin@ampache.dev -l 100
docker exec -u root -it release-test8-test8ampache85-1 $CLICOMMANDROOT admin:updateDatabase -e

echo "INSTALLING SQUASHED AMPACHE on PHP8.5"

INSTALLCOMMAND="$INSTALLERSQUASHED install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}85s -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test8-test8ampache85_squashed-1 ${INSTALLCOMMAND}85s
docker exec -u root -it release-test8-test8ampache85_squashed-1 $CLICOMMANDSQUASHED admin:addUser admin -p "$AMPACHEPASSWORD" -e admin@ampache.dev -l 100
docker exec -u root -it release-test8-test8ampache85_squashed-1 $CLICOMMANDSQUASHED admin:updateDatabase -e

echo "INSTALLING CLIENT AMPACHE on PHP8.5"

INSTALLCOMMAND="$INSTALLERROOT install -f -U $DATABASEUSER -P $DATABASEPASSWORD -H $LOCALIP -u ${DATABASE}85c -p $DATABASE -d $DATABASE"
docker exec -u root -it release-test8-test8ampache85_client-1 ${INSTALLCOMMAND}85c
docker exec -u root -it release-test8-test8ampache85_client-1 $CLICOMMANDROOT admin:addUser admin -p "$AMPACHEPASSWORD" -e admin@ampache.dev -l 100
docker exec -u root -it release-test8-test8ampache85_client-1 $CLICOMMANDROOT admin:updateDatabase -e

# Configure the three installs
#
# A distinct session_name and log_filename per container keeps them from sharing a session cookie on the
# same host and keeps their logs apart. The rest switches on the optional features the harness exercises.
# `api_debug_handler` is deliberately absent from the list: Ampache8 removed the config option entirely.

sed -i "s/session_name = \"ampache\"/session_name = \"8php85\"/g"          $AMPACHEDIR/release-test/8/php85/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"8php85squashed\"/g"  $AMPACHEDIR/release-test/8/php85_squashed/config/ampache.cfg.php
sed -i "s/session_name = \"ampache\"/session_name = \"8php85client\"/g"    $AMPACHEDIR/release-test/8/php85_client/config/ampache.cfg.php

sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"8php85.log\"/g"   $AMPACHEDIR/release-test/8/php85/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"8php85s.log\"/g"  $AMPACHEDIR/release-test/8/php85_squashed/config/ampache.cfg.php
sed -i "s/log_filename = \"%name\.%Y%m%d\.log\"/log_filename = \"8php85c.log\"/g"  $AMPACHEDIR/release-test/8/php85_client/config/ampache.cfg.php

for CONFIG in \
  $AMPACHEDIR/release-test/8/php85/config/ampache.cfg.php \
  $AMPACHEDIR/release-test/8/php85_squashed/config/ampache.cfg.php \
  $AMPACHEDIR/release-test/8/php85_client/config/ampache.cfg.php
do
  sed -i "s/;allow_public_registration = \"true\"/allow_public_registration = \"true\"/g" $CONFIG
  sed -i "s/;user_no_email_confirm = \"true\"/user_no_email_confirm = \"true\"/g"         $CONFIG
  sed -i "s/;captcha_public_reg = \"true\"/captcha_public_reg = \"true\"/g"               $CONFIG
  sed -i "s/;licensing = \"true\"/licensing = \"true\"/g"                                 $CONFIG
  sed -i "s/;label = \"true\"/label = \"true\"/g"                                         $CONFIG
  sed -i "s/;show_similar = \"true\"/show_similar = \"true\"/g"                           $CONFIG
  sed -i "s/;debug = \"true\"/debug = \"true\"/g"                                         $CONFIG
done

# Run the API test harness against each structure

echo
#release-test8-test8ampache85
cat /dev/null > $AMPACHEDIR/docker/log/8php85.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:${PORTPUBLIC} $AMPACHEPASSWORD admin)
echo "Testing $RELEASEVERSION ampache85 - $DEMOPASSWORD -"
echo "python3 $AMPACHEDIR/python/build_all8.py http://${LOCALIP}:${PORTPUBLIC} $DEMOPASSWORD"
python3 $AMPACHEDIR/python/build_all8.py http://${LOCALIP}:${PORTPUBLIC} $DEMOPASSWORD admin 1 $APIVERSION 8

echo
#release-test8-test8ampache85_squashed
cat /dev/null > $AMPACHEDIR/docker/log/8php85s.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:${PORTSQUASHED} $AMPACHEPASSWORD admin)
echo "Testing $RELEASEVERSION ampache85_squashed $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all8.py http://${LOCALIP}:${PORTSQUASHED} $DEMOPASSWORD"
python3 $AMPACHEDIR/python/build_all8.py http://${LOCALIP}:${PORTSQUASHED} $DEMOPASSWORD admin 1 $APIVERSION 8

echo
#release-test8-test8ampache85_client
cat /dev/null > $AMPACHEDIR/docker/log/8php85c.log
DEMOPASSWORD=$(python3 $AMPACHEDIR/python/release_test6.py http://${LOCALIP}:${PORTCLIENT} $AMPACHEPASSWORD admin)
echo "Testing $RELEASEVERSION php85_client $DEMOPASSWORD"
echo "python3 $AMPACHEDIR/python/build_all8.py http://${LOCALIP}:${PORTCLIENT} $DEMOPASSWORD"
python3 $AMPACHEDIR/python/build_all8.py http://${LOCALIP}:${PORTCLIENT} $DEMOPASSWORD admin 1 $APIVERSION 8

echo "PRINT ERRORS"
cat $AMPACHEDIR/docker/log/8*.log | grep Error

echo
echo "DOCKER APACHE ERRORS LOG"
echo
echo "test8ampache85"
docker exec -u root -it release-test8-test8ampache85-1 cat /var/log/apache2/error.log
echo
echo "test8ampache85_squashed"
docker exec -u root -it release-test8-test8ampache85_squashed-1 cat /var/log/apache2/error.log
echo
echo "test8ampache85_client"
docker exec -u root -it release-test8-test8ampache85_client-1 cat /var/log/apache2/error.log
