#!/bin/bash

if [ $# -eq 1 ]
  then
    echo "Check Ref " $1
    python3 check.py -a feed --feedftp conf/ftp-feed.json \
    --feedbase https://www.opikanoba.org/feeds/ \
    --dataftp conf/ftp-data.json \
    --mail conf/mail.json \
    $1
fi
