#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR/..
python setup.py sdist
cp -v dist/*.tar.gz $DIR/worker.tar.gz
if [ $? != 0 ]; then
	echo 'Copying distribution files failed'
	exit 1
fi
