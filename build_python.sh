#!/bin/sh

AMPACHEDIR=$PWD

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
python3 ./build_all.py

# go home
cd $AMPACHEDIR

