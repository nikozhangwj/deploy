#!/usr/bin/env bash

PATH1=/data/$1
PATH2=/deploy/$1
chown -R admin:admin ${PATH1}
chown -R admin:admin ${PATH2}