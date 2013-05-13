#!/bin/sh
cwd=$(pwd)
cd android/assets/www
./update-www.sh
cd $cwd
cd ios/StdGuide3/www
./update-www.sh
