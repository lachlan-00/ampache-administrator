#!/bin/sh

AMPACHEDIR=$PWD
BRANCH="all"
if [ ! $# -eq 0 ]; then
  BRANCH=$1
fi
START=$(date)

if [ $BRANCH = "master" ] || [ $BRANCH = "stable" ] || [ $BRANCH = "nosql" ] || [ $BRANCH = "all" ]; then
  RELEASEVERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' ./ampache-develop/src/Config/Init/InitializationHandlerConfig.php`
  status=$(curl --head --silent https://github.com/ampache/ampache/releases/download/${RELEASEVERSION}/ampache-${RELEASEVERSION}_all_php8.2.zip | head -n 1)
  if echo "$status" | grep -q 404; then
    read -p "Failed to find $RELEASEVERSION... Enter Ampache Version: " RELEASEVERSION
  fi
fi
echo $RELEASEVERSION
if [ ! -d $AMPACHEDIR/docker ]; then
  mkdir $AMPACHEDIR/docker
fi

# MASTER
if [ $BRANCH = "master" ] || [ $BRANCH = "stable" ] || [ $BRANCH = "all" ]; then
  if [ ! -d $AMPACHEDIR/docker/ampache-docker/ ]; then
    cd $AMPACHEDIR/docker && git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker
    cd $AMPACHEDIR/docker && git clone -b master https://github.com/ampache/ampache-docker.git ampache-docker
  fi
  cd $AMPACHEDIR/docker/ampache-docker/ && git checkout master && git reset --hard origin/master && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${RELEASEVERSION} -t ampache/ampache:7 -t ampache/ampache:${RELEASEVERSION} -t ampache/ampache:latest --push . &
fi

# NOSQL
if [ $BRANCH = "nosql" ] || [ $BRANCH = "stable" ] || [ $BRANCH = "all" ]; then
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-nosql/ ]; then
    cd $AMPACHEDIR/docker && git clone -b nosql https://github.com/ampache/ampache-docker.git ampache-docker-nosql
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-nosql/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-nosql
    cd $AMPACHEDIR/docker && git clone -b nosql https://github.com/ampache/ampache-docker.git ampache-docker-nosql
  fi
  cd $AMPACHEDIR/docker/ampache-docker-nosql/ && git checkout nosql && git reset --hard origin/nosql && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 --build-arg VERSION=${RELEASEVERSION} -t ampache/ampache:nosql7 -t ampache/ampache:nosql${RELEASEVERSION} -t ampache/ampache:nosql --push . &
fi

# CLIENT
if [ $BRANCH = "master" ] || [ $BRANCH = "stable" ] || [ $BRANCH = "all" ]; then
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-client/ ]; then
    cd $AMPACHEDIR/docker && git clone -b client https://github.com/ampache/ampache-docker.git ampache-docker-client
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-client/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-client
    cd $AMPACHEDIR/docker && git clone -b client https://github.com/ampache/ampache-docker.git ampache-docker-client
  fi
  cd $AMPACHEDIR/docker/ampache-docker-client/ && git checkout client && git reset --hard origin/client && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:client --push . &
fi

# CLIENT NOSQL
if [ $BRANCH = "nosql" ] || [ $BRANCH = "stable" ] || [ $BRANCH = "all" ]; then
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-client-nosql/ ]; then
    cd $AMPACHEDIR/docker && git clone -b client-nosql https://github.com/ampache/ampache-docker.git ampache-docker-client-nosql
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-client-nosql/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-client-nosql
    cd $AMPACHEDIR/docker && git clone -b client-nosql https://github.com/ampache/ampache-docker.git ampache-docker-client-nosql
  fi
  cd $AMPACHEDIR/docker/ampache-docker-client-nosql/ && git checkout client-nosql && git reset --hard origin/client-nosql && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:client-nosql --push . &
fi

# DEVELOP
if [ $BRANCH = "develop" ] || [ $BRANCH = "all" ]; then
  # DEFAULT
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-develop/ ]; then
    cd $AMPACHEDIR/docker && git clone -b develop https://github.com/ampache/ampache-docker.git ampache-docker-develop
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-develop/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-develop
    cd $AMPACHEDIR/docker && git clone -b develop https://github.com/ampache/ampache-docker.git ampache-docker-develop
  fi
  cd $AMPACHEDIR/docker/ampache-docker-develop/ && git checkout develop && git reset --hard origin/develop && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:develop -t ampache/ampache:preview --push . &
  
  # NOSQL
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-nosql-develop/ ]; then
    cd $AMPACHEDIR/docker && git clone -b nosql-develop https://github.com/ampache/ampache-docker.git ampache-docker-nosql-develop
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-nosql-develop/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-nosql-develop
    cd $AMPACHEDIR/docker && git clone -b nosql-develop https://github.com/ampache/ampache-docker.git ampache-docker-nosql-develop
  fi
  cd $AMPACHEDIR/docker/ampache-docker-nosql-develop/ && git checkout nosql-develop && git reset --hard origin/nosql-develop && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:nosql-develop -t ampache/ampache:nosql-preview --push . &
fi

# PREVIEW
if [ $BRANCH = "preview" ]; then
  # DEFAULT
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-preview/ ]; then
    cd $AMPACHEDIR/docker && git clone -b preview https://github.com/ampache/ampache-docker.git ampache-docker-preview
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-preview/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-preview
    cd $AMPACHEDIR/docker && git clone -b preview https://github.com/ampache/ampache-docker.git ampache-docker-preview
  fi
  cd $AMPACHEDIR/docker/ampache-docker-preview/ && git checkout preview && git reset --hard origin/preview && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:preview --push . &

  # NOSQL
  if [ ! -d $AMPACHEDIR/docker/ampache-docker-nosql-preview/ ]; then
    cd $AMPACHEDIR/docker && git clone -b nosql-preview https://github.com/ampache/ampache-docker.git ampache-docker-nosql-preview
  fi
  if [ ! -f $AMPACHEDIR/docker/ampache-docker-nosql-preview/Dockerfile ]; then
    rm -rf $AMPACHEDIR/docker/ampache-docker-nosql-preview
    cd $AMPACHEDIR/docker && git clone -b nosql-preview https://github.com/ampache/ampache-docker.git ampache-docker-nosql-preview
  fi
  cd $AMPACHEDIR/docker/ampache-docker-nosql-preview/ && git checkout nosql-preview && git reset --hard origin/nosql-preview && git pull && docker buildx build --no-cache --platform linux/amd64,linux/arm64,linux/arm/v7 -t ampache/ampache:nosql-preview --push . &
fi

# go home
cd $AMPACHEDIR

echo $START
date

