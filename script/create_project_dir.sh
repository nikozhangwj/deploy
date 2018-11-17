#!/bin/bash

if [ $# -eq 0 ];then
echo "empty"
echo "usage:"
echo "APP_NAME"
exit 1;
fi

APP_NAME=$1
mkdir -p /data/${APP_NAME}/{tmp,download,static,secrets,bin,config,logs}
