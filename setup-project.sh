#!/bin/sh

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

if [ -z "$MOZ_UPHEADLINER_PROD"];
then
    set -x
    echo "setting up development virtualenv"
    export MOZ_UPHEADLINER_DEV=1
else
    echo "setting up production virtualenv"
fi

rm -rf up-headliner-env

virtualenv --python=python2.7 --no-site-packages up-headliner-env
. up-headliner-env/bin/activate


python setup.py develop
