#!/bin/bash

backup_path=$1
app_name=$2

cd ${backup_path}
cd ..
pwd

tar -xvzf ${backup_path}
cp -rf ./data/${app_name}/config /data/${app_name}/config