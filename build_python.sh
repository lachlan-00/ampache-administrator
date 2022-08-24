#!/bin/sh

AMPACHEDIR=$PWD
BRANCH="0"
if [ ! $# -eq 0 ]; then
  BRANCH=$1
fi

if [ ! -d $AMPACHEDIR/python ]; then
  mkdir $AMPACHEDIR/python
fi


if [ ! -d $AMPACHEDIR/ampache-test ]; then
  git clone https://github.com/lachlan-00/ampache-test.git ampache-test
  cd $AMPACHEDIR/ampache-test && setup-ampache-test.sh
fi
if [ ! -f $AMPACHEDIR/ampache-test/ampache.cfg.php ]; then
  rm -rf $AMPACHEDIR/ampache-test
  git clone https://github.com/lachlan-00/ampache-test.git ampache-test
fi

if [ ! -d $AMPACHEDIR/python/python3-ampache3 ]; then
  cd $AMPACHEDIR/python && git clone -b api3 https://github.com/ampache/python3-ampache.git python3-ampache3
fi
if [ ! -f $AMPACHEDIR/python/python3-ampache3/setup.py ]; then
  rm -rf $AMPACHEDIR/python/python3-ampache3
  cd $AMPACHEDIR/python && git clone -b api3 https://github.com/ampache/python3-ampache.git python3-ampache3
fi

if [ ! -d $AMPACHEDIR/python/python3-ampache4 ]; then
  cd $AMPACHEDIR/python && git clone -b api4 https://github.com/ampache/python3-ampache.git python3-ampache4
fi
if [ ! -f $AMPACHEDIR/python/python3-ampache4/setup.py ]; then
  rm -rf $AMPACHEDIR/python/python3-ampache4
  cd $AMPACHEDIR/python && git clone -b api4 https://github.com/ampache/python3-ampache.git python3-ampache4
fi
if [ ! -d $AMPACHEDIR/python/python3-ampache5 ]; then
  cd $AMPACHEDIR/python && git clone -b api5 https://github.com/ampache/python3-ampache.git python3-ampache5
fi
if [ ! -f $AMPACHEDIR/python/python3-ampache5/setup.py ]; then
  rm -rf $AMPACHEDIR/python/python3-ampache5
  cd $AMPACHEDIR/python && git clone -b api5 https://github.com/ampache/python3-ampache.git python3-ampache5
fi

cd $AMPACHEDIR/ampache-test && docker-compose up -d

echo "wake up ampache-test!"
sleep 7

cd $AMPACHEDIR/ampache-test/ampache && git pull

cd $AMPACHEDIR/python/
if [ ! $BRANCH -eq 0 ]; then
  echo "RESET THE DATABASE"
  docker exec ampache-test_ampachetest_1 sh -c "mysql -uroot ampachetest < /var/lib/mysql/ampache-test.sql"
  python3 ./build_all.py $BRANCH
  echo "DONE $BRANCH"
else
  echo "RESET THE DATABASE"
  docker exec ampache-test_ampachetest_1 sh -c "mysql -uroot ampachetest < /var/lib/mysql/ampache-test.sql"
  python3 ./build_all.py 5
  echo "DONE 5"

  echo "RESET THE DATABASE"
  docker exec ampache-test_ampachetest_1 sh -c "mysql -uroot ampachetest < /var/lib/mysql/ampache-test.sql"
  python3 ./build_all.py 4
  echo "DONE 4"

  echo "RESET THE DATABASE"
  docker exec ampache-test_ampachetest_1 sh -c "mysql -uroot ampachetest < /var/lib/mysql/ampache-test.sql"
  python3 ./build_all.py 3
  echo "DONE 3"
fi

# go home
cd $AMPACHEDIR

