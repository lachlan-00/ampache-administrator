#!/bin/sh
# Re-resolves resources/composer_php8.6.lock against resources/composer_php8.6.json using the
# real php8.6 binary, so the pin used by build_release8.sh can be refreshed deliberately instead
# of drifting on every build. Run from anywhere; commit both files afterwards.

set -e

SCRIPTDIR=$(cd "$(dirname "$0")" && pwd)
PHPBIN=${PHPBIN:-php8.6}
COMPOSERPATH=${COMPOSERPATH:-/usr/local/bin/composer}

cd "$SCRIPTDIR"
COMPOSER=composer_php8.6.json $PHPBIN $COMPOSERPATH update --no-install --no-interaction "$@"

echo
echo "Updated $SCRIPTDIR/composer_php8.6.lock - review the diff and commit both files."
