#!/bin/sh

AMPACHEDIR=$PWD

if [ ! -d $AMPACHEDIR/docker ]; then
  mkdir $AMPACHEDIR/docker
fi

if [ ! -d $AMPACHEDIR/docker/ampache-docker-develop/ ]; then
  git clone -b develop https://github.com/ampache/ampache-docker.git ampache-docker-develop
fi
if [ ! -f $AMPACHEDIR/docker/ampache-docker-develop/Dockerfile ]; then
  rm -rf $AMPACHEDIR/docker/ampache-docker-develop
  git clone -b develop https://github.com/ampache/ampache-docker.git ampache-docker-develop
fi

cd $AMPACHEDIR/docker/ampache-docker-develop/ && git reset --hard origin/develop && git pull && nohup docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:develop -t ampache/ampache:preview --push . &

# go home
cd $AMPACHEDIR

