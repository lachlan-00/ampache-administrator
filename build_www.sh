#!/bin/sh

AMPACHEDIR=$PWD

if [ ! -d $AMPACHEDIR/ampache-develop ]; then
  git clone -b develop https://github.com/ampache/ampache.git ampache-develop
fi
if [ ! -f $AMPACHEDIR/ampache-develop/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-develop
  git clone -b develop https://github.com/ampache/ampache.git ampache-develop
fi
if [ ! -d $AMPACHEDIR/ampache-master ]; then
  git clone -b master https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -f $AMPACHEDIR/ampache-master/index.php ]; then
  rm -rf $AMPACHEDIR/ampache-master
  git clone -b master https://github.com/ampache/ampache.git ampache-master
fi
if [ ! -d $AMPACHEDIR/www/ampache.org-api ]; then
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi
if [ ! -f $AMPACHEDIR/www/ampache.github.io/index.html ]; then
  rm -rf ./ampache.github.io
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi
if [ ! -d $AMPACHEDIR/www/ampache.github.io ]; then
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi
if [ ! -f $AMPACHEDIR/www/ampache.github.io/index.html ]; then
  rm -rf $AMPACHEDIR/ampache.github.io
  cd $AMPACHEDIR/www && git clone -b master https://github.com/ampache/ampache.github.io.git ampache.github.io
fi

cd $AMPACHEDIR/ampache-master && git reset --hard origin/master && git pull
cd $AMPACHEDIR/ampache-develop && git reset --hard origin/develop && git pull
cd $AMPACHEDIR/www/ampache.github.io && git reset --hard origin/master && git pull
cd $AMPACHEDIR/www/ampache.org-api && git reset --hard origin/master && git pull

cd $AMPACHEDIR/www/ampache.org-api && npm run build && cp -rfv ./build/* $AMPACHEDIR/www/ampache.github.io/api/

cp $AMPACHEDIR/www/ampache.org-api/docs/index.md $AMPACHEDIR/ampache-develop/docs/API.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-json-methods.md $AMPACHEDIR/ampache-develop/docs/API-JSON-methods.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-xml-methods.md $AMPACHEDIR/ampache-develop/docs/API-XML-methods.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-advanced-search.md $AMPACHEDIR/ampache-develop/docs/API-advanced-search.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-errors.md $AMPACHEDIR/ampache-develop/docs/API-Errors.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-acls.md $AMPACHEDIR/ampache-develop/docs/API-acls.md

cp $AMPACHEDIR/www/ampache.org-api/docs/index.md $AMPACHEDIR/ampache-master/docs/API.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-json-methods.md $AMPACHEDIR/ampache-master/docs/API-JSON-methods.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-xml-methods.md $AMPACHEDIR/ampache-master/docs/API-XML-methods.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-advanced-search.md $AMPACHEDIR/ampache-master/docs/API-advanced-search.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-errors.md $AMPACHEDIR/ampache-master/docs/API-Errors.md
cp $AMPACHEDIR/www/ampache.org-api/docs/api-acls.md $AMPACHEDIR/ampache-master/docs/API-acls.md
