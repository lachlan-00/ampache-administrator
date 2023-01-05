#!/bin/sh

AMPACHEDIR=$PWD

docker-compose -f docker/docker-compose74.yml -f docker/docker-compose74_squashed.yml -f docker/docker-compose80.yml -f docker/docker-compose80_squashed.yml -f docker/docker-compose81.yml -f docker/docker-compose81_squashed.yml -f docker/docker-compose82.yml -f docker/docker-compose82_squashed.yml up -d --build

