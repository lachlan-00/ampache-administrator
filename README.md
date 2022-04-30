# Ampache Administrator Tools

I'm trying to formalize my Ampache tools into one repo to allow other to use them

## Files

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

Build the api website using npm. Then copy the markdown files into the Ampache folders and the Ampache website

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

### setup-docker.sh

Docker-compose setup allowing you locally run Ampache on php 7.4, 8.0 and 8.1

Used for testing releases on each release type.

You can launch a container for php7.4, 8.0 and 8.1 by issuing the following command
```
docker-compose up
```

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


