#!/bin/sh

# test python version - must be 2.7 for lambda
python --version 2>&1 | grep -q "Python 2.7"
if [ $? -ne 0 ] ; then
    echo "ERROR: `type python` isn't reporting as Python 2.7"
    exit 129
fi

# test for style
pylint --rcfile=pylint.conf src/grab_xmltv.py
if [ $? -ne 0 ] ; then
    echo "ERROR: pylint score isn't 10/10"
    exit 130
fi

# turn on non-zero exit detection
set -e

mkdir -p pkg
rm -f pkg/grab_xmltv.zip

pip install requests -t build_root/

cp -rp src/* build_root/

cd build_root/
zip -r ../pkg/grab_xmltv.zip ./

cd ../
rm -rf build_root
