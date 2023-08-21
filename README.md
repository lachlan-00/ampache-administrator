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

### build_release.sh & build_release6.sh

Build ampache release files from the current patch5 or patch6 branches

Release files are built from the php dirs and will create a zip file in the releases folder

e.g. `releases/ampache-${a_version}_all_php7.4.zip`

#### Script workarounds for release builds

* Make sure the jquery-context menu map files are created
  * ./public/lib/components/jquery-contextmenu/dist/jquery.contextMenu.min.js.map
  * ./public/lib/components/jquery-contextmenu/dist/jquery.contextMenu.min.css.map
* Copy patched gettext StringReader.php to stop all the warning messages for translations
  * ./vendor/gettext/gettext/src/Utils/StringReader.php
* Copy missing prettyphoto images to ./public/lib/components/prettyphoto/images

### build_ampache-squashed.sh & build_ampache-squashed6.sh

This script will update the squashed repo so you don't have to manually edit the files for updating that branch

* Copy the files from `./ampache-master` to `./ampache-squashed`
* Run `./squash-ampache.py` to regex the strings to match the squashed structure

squashed 6 copies from `./ampache-patch6` to `./ampache-squashed6`

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

This script will load up [ampache-test](https://github.com/lachlan-00/ampache-test) in the `/ampache-test` folder
and then generate the xml and json example documents against that server.

* Build the api docs for api3
* Build the api docs for api4
* Build the api docs for api5

### docker-release-test.sh

Test Zip file releases but installing to a local docker stack. (make sure you build them using build_release first!)

Release zips must be in the `./releases/` folder. by default it will check for the latest version in `./patch6`

The zips are extracted to `./release-test/` and set as a volume for the local html folder for each container

Once the containers are build the database and admin user are installed.

Finally; `python/release_test.py` is run to create a test user which allows running demo build scripts.

Set a custom version number in the cli adding the version string at the end

e.g. `sh docker-release-test.sh 6.0.0`

Sites are then using the php* folders and creates the following container images:

* release-test-ampache_ampache74
  * Website root `./release-test/php74`
  * Accessible on http://localhost:18074
* release-test-ampache_ampache74_squashed
  * Website root `./release-test/php74_squashed`
  * Accessible on http://localhost:18075
* release-test-ampache_ampache80
  * Website root `./release-test/php80`
  * Accessible on http://localhost:18084
* release-test-ampache_ampache80_squashed
  * Website root `./release-test/php80_squashed`
  * Accessible on http://localhost:18085
* release-test-ampache_ampache81
  * Website root `./release-test/php81`
  * Accessible on http://localhost:18086
* release-test-ampache_ampache81_squashed
  * Website root `./release-test/php81_squashed`
  * Accessible on http://localhost:18087

## Files for Ampache Users

### setup-workspace.sh

Just want to pull down ampache code repos and start patching?

If you don't have composer installed to `/usr/local/bin/composer` then it will be saved to `./docker/composer`

Clone Ampache develop to `./ampache-develop` and then clone Ampache master to `./ampache-master`

### setup-python.sh

This file sets up all the api folders for building python documentation

### setup-docker.sh & setup-docker6.sh

Docker-compose setup allowing you locally run Ampache on php 7.4, 8.0, 8.1 and 8.2

Used for testing releases on each release type but an easy way for anyone to just get up and running

You can launch a container for php7.4, 8.0, 8.1 and 8.2 by issuing the following command

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

## TODO

Confirm correct data for Subsonic calls

* createShare
* getShares
* getTopSongs
* hls (is that needed as it's returning a playlist)
