#!/bin/sh

AMPACHEDIR=$PWD
BRANCH="all"
if [ ! $# -eq 0 ]; then
  BRANCH=$1
fi


if [ $BRANCH = "master" ] || [ $BRANCH = "nosql" ] || [ $BRANCH = "all" ]; then
  RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' ./ampache-master/src/Config/Init/InitializationHandlerConfig.php`
  status=$(curl --head --silent https://github.com/ampache/ampache/releases/download/${RELEASEVERSION}/ampache-${RELEASEVERSION}_all_php8.2.zip | head -n 1)
  if echo "$status" | grep -q 404; then
    read -p "Failed to find $RELEASEVERSION... Enter Ampache Version: " RELEASEVERSION
  fi
fi
 
if [ ! -d $AMPACHEDIR/docker ]; then
  mkdir $AMPACHEDIR/docker
fi

# MASTER
if [ $BRANCH = "master" ] || [ $BRANCH = "all" ]; then
  if [ ! -d $AMPACHEDIR/docker/ampache-docker/ ]; then
    cd $AMPACHEDIR/docker && git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker
    cd $AMPACHEDIR/docker && git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
  fi
  cd $AMPACHEDIR/docker/ampache-docker/ && git checkout master && git reset --hard origin/master && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${RELEASEVERSION} -t ampache/ampache:5 -t ampache/ampache:${RELEASEVERSION} --push . &
fi

# NOSQL
if [ $BRANCH = "nosql" ] || [ $BRANCH = "all" ]; then
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-nosql/ ]; then
    cd $AMPACHEDIR/docker && git clone -b nosql https://github.com/ampache/ampache-docker.git ampache-docker-nosql
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-nosql/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-nosql
    cd $AMPACHEDIR/docker && git clone -b nosql https://github.com/ampache/ampache-docker.git ampache-docker-nosql
  fi
  cd $AMPACHEDIR/docker/ampache-docker-nosql/ && git checkout nosql && git reset --hard origin/nosql && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${RELEASEVERSION} -t ampache/ampache:nosql5 -t ampache/ampache:nosql${RELEASEVERSION} -t ampache/ampache:nosql --push . &
fi

# go home
cd $AMPACHEDIR

