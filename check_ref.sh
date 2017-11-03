#!/bin/bash

if [ $# -eq 1 ]
  then
    echo "Check Ref " $1
    python3 check.py -a feed --feedftp myconf/ftp-feed.json \
    --feedbase https://www.opikanoba.org/feeds/ \
    --dataftp myconf/ftp-data.json \
    --mail myconf/mail.json \
    $1
fi
