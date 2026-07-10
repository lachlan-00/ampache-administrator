#!/bin/sh

AMPACHEDIR=$PWD
BRANCH="0"
if [ ! $# -eq 0 ]; then
  BRANCH=$1
fi
COMPOSERPATH="/usr/local/bin/composer"
DEVELOPBRANCH="develop8"

echo $BRANCH

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi
sh $AMPACHEDIR/setup-python.sh

sudo chown $USER:33 -R $AMPACHEDIR/ampache-test/ampache/

cd $AMPACHEDIR/ampache-test/ampache
git reset --hard origin/$DEVELOPBRANCH  && git pull && $COMPOSERPATH install
npm install
npm run build

sudo systemctl start mysql

sudo chown $USER:33 -R $AMPACHEDIR/ampache-test/ampache/config
sudo chown $USER:33 -R $AMPACHEDIR/ampache-test/docker/log

docker container stop ampache-test-ampachetest-1

cd $AMPACHEDIR/ampache-test && docker-compose up -d --build

# recreate the DB
#mysql -u root -e "CREATE DATABASE ampachetest;"

echo "wake up ampache-test!"
sleep 7

# Clean up the log files
docker exec -u root ampache-test-ampachetest-1 sh -c '[ -f /var/log/apache2/error.log ] && : > /var/log/apache2/error.log'
docker exec -u root ampache-test-ampachetest-1 sh -c '[ -f /var/log/ampache/ampache-test.log ] && : > /var/log/ampache/ampache-test.log'

mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
cd $AMPACHEDIR/python/
if [ "$BRANCH" != "0" ]; then
  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START $BRANCH"
  python3 ./build_all8.py $BRANCH
  echo "DONE $BRANCH"
else
  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 8"
  python3 ./build_all8.py 8
  echo "DONE 8"
  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 6"
  python3 ./build_all8.py 6
  echo "DONE 6"

  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 5"
  python3 ./build_all8.py 5
  echo "DONE 5"

  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 4"
  python3 ./build_all8.py 4
  echo "DONE 4"

  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 3"
  python3 ./build_all8.py 3
  echo "DONE 3"

  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START Subsonic"
  python3 ./build_all8.py s
  echo "DONE Subsonic"

  echo "RESET THE DATABASE"
  mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START OpenSubsonic"
  python3 ./build_all8.py o
  echo "DONE OpenSubsonic"
fi

echo "RESET THE DATABASE"
mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"

echo
echo "DOCKER APACHE ERRORS LOG"
docker exec -u root -it ampache-test-ampachetest-1 cat /var/log/apache2/error.log

echo
echo "DOCKER Ampache log errors"
docker exec -u root -it ampache-test-ampachetest-1 cat /var/log/ampache/ampache-test.log | grep Error

### Update test sql
#mysql -u root ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
#docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
#mysqldump -u root ampachetest > $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql

cat $AMPACHEDIR/ampache-test/docker/log/apache2/error.log
# go home
cd $AMPACHEDIR

