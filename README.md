# Ampache Administrator Tools

This repo containse the scripts used to build Ampache resources including:

* Release zip files
* Official Docker images
* API example documentation
* The ampache.org site
* Generate the static html for ampache.org/api

I'm trying to formalize my Ampache tools into one repo to allow others to use them.
Obviously not everyone has write access to do some of these things but by documenting
this process it should be easier for anyone else to pick this up by doing it all in the open

## Files for Ampache Administrators

### build_release.sh

Build ampache release files from the current master branch

Release files are built from the php dirs and will create a zip file in the releases folder

e.g. `releases/ampache-${a_version}_all_php7.4.zip`

### build_docker.sh

Build all the docker images and upload to docker hub

* master
* nosql
* develop

Build single branches with branch name as an argument
```
sh ./build_docker.sh master
```

### build_www.sh

Build the api website using npm.
 Then copy the markdown files into the Ampache folders and the Ampache website

* Compile the api content repo
  * `./www/ampache.org-api/content/`
* Copy api public folders to the website repo
  * `./www/ampache.github.io/api/`
* Copy doc files to the Ampache repos
  * `./ampache-develop/docs/`
  * `./ampache-master/docs/`

### build_python.sh

* Build the api docs for api3
* Build the api docs for api4
* Build the api docs for api5

This script will load up [ampache-test](https://github.com/lachlan-00/ampache-test) in the `/ampache-test` folder
and then generate the xml and json example documents against that server.

## Files for Ampache Users

### setup-workspace.sh

Just want to pull down ampache code repos and start patching?

If you don't have composer installed to `/usr/local/bin/composer` then it will be saved to `./docker/composer`

Clone Ampache develop to `./ampache-develop` and then clone Ampache master to `./ampache-master`

### setup-docker.sh

Docker-compose setup allowing you locally run Ampache on php 7.4, 8.0 and 8.1

Used for testing releases on each release type but an easy way for anyone to just get up and running

You can launch a container for php7.4, 8.0 and 8.1 by issuing the following command
```
docker-compose up
```

If you don't have composer installed to `/usr/local/bin/composer` then it will be saved to `./docker/composer`

Sites are then using the php* folders and creates the following container images:

* ampache_ampache74
  * Website root `./php74`
  * Accessible on http://localhost:8074
* ampache_ampache74_squashed
  * Website root `./php74_squashed`
  * Accessible on http://localhost:8075
* ampache_ampache80
  * Website root `./php80`
  * Accessible on http://localhost:8084
* ampache_ampache80_squashed
  * Website root `./php80_squashed`
  * Accessible on http://localhost:8085
* ampache_ampache81
  * Website root `./php81`
  * Accessible on http://localhost:8086
* ampache_ampache81_squashed
  * Website root `./php81_squashed`
  * Accessible on http://localhost:8087

## Reference Repos

Official repos

* [ampache](https://github.com/ampache/ampache)
* [ampache-docker](https://github.com/ampache/ampache-docker)
* [python3-ampache](https://github.com/ampache/python3-ampache)
* [ampache.github.io](https://github.com/ampache/ampache.github.io)
* [ampache.org-api](https://github.com/ampache/ampache.org-api)

Personal repos

* [ampache-test](https://github.com/lachlan-00/ampache-test)

