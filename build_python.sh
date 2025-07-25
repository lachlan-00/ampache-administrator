#!/bin/sh

AMPACHEDIR=$PWD
BRANCH="0"
if [ ! $# -eq 0 ]; then
  BRANCH=$1
fi
COMPOSERPATH="/usr/local/bin/composer"

echo $BRANCH

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi
sh ./setup-python.sh
cd $AMPACHEDIR/ampache-test/ampache && git reset --hard origin/develop  && git pull && $COMPOSERPATH install

docker container stop ampache-test-ampachetest-1

cd $AMPACHEDIR/ampache-test && docker-compose up -d --build

# recreate the DB
#mysql -uroot -e "CREATE DATABASE ampachetest;"

echo "wake up ampache-test!"
sleep 7
mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
cd $AMPACHEDIR/python/
if [ ! $BRANCH -eq 0 ]; then
  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START $BRANCH"
  python3 ./build_all7.py $BRANCH
  echo "DONE $BRANCH"
else
  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 6"
  python3 ./build_all7.py 6
  echo "DONE 6"

  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 5"
  python3 ./build_all7.py 5
  echo "DONE 5"

  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 4"
  python3 ./build_all7.py 4
  echo "DONE 4"

  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START 3"
  python3 ./build_all7.py 3
  echo "DONE 3"

  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START Subsonic"
  python3 ./build_all7.py s
  echo "DONE Subsonic"

  echo "RESET THE DATABASE"
  mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
  docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"
  echo "START OpenSubsonic"
  python3 ./build_all7.py o
  echo "DONE OpenSubsonic"
fi

echo "RESET THE DATABASE"
mysql -uroot ampachetest < $AMPACHEDIR/ampache-test/docker/data/sql/ampache-test.sql
docker exec ampache-test-ampachetest-1 sh -c "php /var/www/html/bin/cli admin:updateDatabase -e"

# go home
cd $AMPACHEDIR

