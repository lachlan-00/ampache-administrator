# Ampache Administrator Tools

I'm trying to formalize my Ampache tools into one repo to allow other to use them

## Files

### build_release.sh

* Build ampache release files from the current master branch

### build_docker.sh

* Build all the docker images and upload to docker hub
  * Latest
  * Nosql
  * Develop

### build_docker_develop.sh

* Build the develop branch for docker only

### build_www.sh

* Compile the api content repo
* Copy api public folders to the website repo

### build_python.sh

* Build the api docs for api3
* Build the api docs for api4
* Build the api docs for api5

### setup-docker.sh

Docker-compose setup allowing you locally run Ampache on php 7.4, 8.0 and 8.1

Used for testing releases on each release type
