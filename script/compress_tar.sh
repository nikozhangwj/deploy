#!/usr/bin/env bash

APP_name=${1}
version=${2}
tar_file=/deploy/${APP_name}/app/${version}.tar.gz
file_path=/deploy/${APP_name}/app/${version}
target_dir=/data/${APP_name}/

tar -xvzf ${tar_file} -C /
cp -rf ${file_path}/conf/* ${target_dir}/conf/
cp -rf ${file_path}/lib/* ${target_dir}/lib/