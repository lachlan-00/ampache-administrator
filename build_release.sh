#!/bin/sh

AMPACHEDIR=$PWD
COMPOSERPATH="/usr/local/bin/composer"

read -p "Enter Ampache Version: " a_version

if [ ! -d $AMPACHEDIR/releases ]; then
  mkdir $AMPACHEDIR/releases
fi

if [ ! -f $COMPOSERPATH ]; then
  COMPOSERPATH="$AMPACHEDIR/docker/composer"
  wget -q -O $COMPOSERPATH https://getcomposer.org/download/latest-stable/composer.phar
  chmod +x $COMPOSERPATH
fi

if [ ! -d $AMPACHEDIR/php74 ]; then
  git clone -b master https://github.com/ampache/ampache.git php74
fi
if [ ! -f $AMPACHEDIR/php74/index.php ]; then
  rm -rf $AMPACHEDIR/php74
  git clone -b master https://github.com/ampache/ampache.git php74
fi
if [ ! -d $AMPACHEDIR/php74_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php74_squashed
fi
if [ ! -f $AMPACHEDIR/php74_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php74_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php74_squashed
fi

if [ ! -d $AMPACHEDIR/php80 ]; then
  git clone -b master https://github.com/ampache/ampache.git php80
fi
if [ ! -f $AMPACHEDIR/php80/index.php ]; then
  rm -rf $AMPACHEDIR/php80
  git clone -b master https://github.com/ampache/ampache.git php80
fi
if [ ! -d $AMPACHEDIR/php80_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php80_squashed
fi
if [ ! -f $AMPACHEDIR/php80_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php80_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php80_squashed
fi

if [ ! -d $AMPACHEDIR/php81 ]; then
  git clone -b master https://github.com/ampache/ampache.git php81
fi
if [ ! -f $AMPACHEDIR/php81/index.php ]; then
  rm -rf $AMPACHEDIR/php81
  git clone -b master https://github.com/ampache/ampache.git php81
fi
if [ ! -d $AMPACHEDIR/php81_squashed ]; then
  git clone -b squashed https://github.com/ampache/ampache.git php81_squashed
fi
if [ ! -f $AMPACHEDIR/php81_squashed/index.php ]; then
  rm -rf $AMPACHEDIR/php81_squashed
  git clone -b squashed https://github.com/ampache/ampache.git php81_squashed
fi

# php 7.4
cd $AMPACHEDIR/php74 && git fetch origin patch5 && git checkout patch5 && git reset --hard origin/patch5 && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php7.4 $COMPOSERPATH install
php7.4 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;
rm $AMPACHEDIR/releases/ampache-${a_version}_all_php7.4.zip & cd $AMPACHEDIR/php74 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess $AMPACHEDIR/releases/ampache-${a_version}_all_php7.4.zip ./

cd $AMPACHEDIR/php74_squashed && git fetch origin squashed && git checkout squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* ./docker/ && php7.4 $COMPOSERPATH install
php7.4 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;
rm $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php7.4.zip & cd $AMPACHEDIR/php74_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php7.4.zip ./

# php 8.0
cd $AMPACHEDIR/php80 && git fetch origin patch5 && git checkout patch5 && git reset --hard origin/patch5 && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.0 $COMPOSERPATH install
php8.0 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;
rm $AMPACHEDIR/ampache-${a_version}_all_php8.0.zip & cd $AMPACHEDIR/php80 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess $AMPACHEDIR/releases/ampache-${a_version}_all_php8.0.zip ./

cd $AMPACHEDIR/php80_squashed && git fetch origin squashed && git checkout squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* ./docker/ && php8.0 $COMPOSERPATH install
php8.0 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;
rm $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php8.0.zip & cd $AMPACHEDIR/php80_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php8.0.zip ./


# php 8.1
cd $AMPACHEDIR/php81 && git fetch origin patch5 && git checkout patch5 && git reset --hard origin/patch5 && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* && php8.1 $COMPOSERPATH install
php8.1 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./public/lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;
rm $AMPACHEDIR/releases/ampache-${a_version}_all_php8.1.zip & cd $AMPACHEDIR/php81 && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./public/rest/.htaccess --exclude=./public/play/.htaccess --exclude=./public/channel/.htaccess $AMPACHEDIR/releases/ampache-${a_version}_all_php8.1.zip ./

cd $AMPACHEDIR/php81_squashed && git fetch origin squashed && git checkout squashed && git reset --hard origin/squashed && git pull
rm -rf ./composer.lock vendor/* public/lib/components/* ./docker/ && php8.1 $COMPOSERPATH install
php8.1 $COMPOSERPATH install
find . -xtype l -exec rm {} \;
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.js.map
wget -P ./lib/components/jQuery-contextMenu/dist/ https://raw.githubusercontent.com/swisnl/jQuery-contextMenu/a7a1b9f3b9cd789d6eb733ee5e7cbc6c91b3f0f8/dist/jquery.contextMenu.min.css.map
find . -name "*.map.1" -exec rm {} \;
rm $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php8.1.zip & cd $AMPACHEDIR/php81_squashed && zip -r -q -u -9 --exclude=./config/ampache.cfg.php --exclude=./docker/* --exclude=./.git/* --exclude=./.github/* --exclude=./.tx/* --exclude=./.idea/* --exclude=.gitignore --exclude=.gitattributes --exclude=.scrutinizer.yml --exclude=CNAME --exclude=.codeclimate.yml --exclude=.php* --exclude=.tgitconfig --exclude=.travis.yml --exclude=./rest/.htaccess --exclude=./play/.htaccess --exclude=./channel/.htaccess $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php8.1.zip ./

# go back
cd $AMPACHEDIR

# copy the file for default releases
cp -vf $AMPACHEDIR/releases/ampache-${a_version}_all_squashed_php7.4.zip $AMPACHEDIR/releases/ampache-${a_version}_all_squashed.zip
cp -vf $AMPACHEDIR/releases/ampache-${a_version}_all_php7.4.zip $AMPACHEDIR/releases/ampache-${a_version}_all.zip

cd $AMPACHEDIR/releases
# echo the version checksum
echo
echo "php7.4"
md5sum ./ampache-${a_version}_all.zip
md5sum ./ampache-${a_version}_all_php7.4.zip
md5sum ./ampache-${a_version}_all_squashed.zip
md5sum ./ampache-${a_version}_all_squashed_php7.4.zip
echo
echo "php8.0"
md5sum ./ampache-${a_version}_all_php8.0.zip
md5sum ./ampache-${a_version}_all_squashed_php8.0.zip
echo
echo "php8.1"
md5sum ./ampache-${a_version}_all_php8.1.zip
md5sum ./ampache-${a_version}_all_squashed_php8.1.zip
echo
echo

# go home
cd $AMPACHEDIR

