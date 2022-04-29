#!/bin/sh

AMPACHEDIR=$PWD

if [ ! -d $AMPACHEDIR/docker ]; then
  mkdir $AMPACHEDIR/docker
fi

read -p "Enter Ampache Version: " a_version
# PREP
if [ ! -d $AMPACHEDIR/docker/ampache-docker/ ]; then
  git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
fi
if [ ! -d $AMPACHEDIR/docker/ampache-docker-nosql/ ]; then
  git clone -b nosql https://github.com/ampache/ampache-docker.git ampache-docker-nosql
fi
if [ ! -d $AMPACHEDIR/docker/ampache-docker-develop/ ]; then
  git clone -b develop https://github.com/ampache/ampache-docker.git ampache-docker-develop
fi
if [ ! -f $AMPACHEDIR/docker/ampache-docker/Dockerfile ]; then
  rm -rf $AMPACHEDIR/docker/ampache-docker
  git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
fi
if [ ! -f $AMPACHEDIR/docker/ampache-docker-nosql/Dockerfile ]; then
  rm -rf $AMPACHEDIR/docker/ampache-docker-nosql
  git clone -b nosql https://github.com/ampache/ampache-docker.git ampache-docker-nosql
fi
if [ ! -f $AMPACHEDIR/docker/ampache-docker-develop/Dockerfile ]; then
  rm -rf $AMPACHEDIR/docker/ampache-docker-develop
  git clone -b develop https://github.com/ampache/ampache-docker.git ampache-docker-develop
fi
# build everything
cd $AMPACHEDIR/docker/ampache-docker/ && git reset --hard origin/master && git pull && nohup docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${a_version} -t ampache/ampache:5 -t ampache/ampache:${a_version} -t ampache/ampache:latest --push . &
cd $AMPACHEDIR/docker/ampache-docker-nosql/ && git reset --hard origin/nosql && git pull && nohup docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${a_version} -t ampache/ampache:nosql5 -t ampache/ampache:nosql${a_version} -t ampache/ampache:nosql --push . &
cd $AMPACHEDIR/docker/ampache-docker-develop/ && git reset --hard origin/develop && git pull && nohup docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${a_version} -t ampache/ampache:develop -t ampache/ampache:preview --push . &

# go home
cd $AMPACHEDIR/ampache-docker/
