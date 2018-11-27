#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Filename:    backup.sh
# Revision:    1.2
# Date:        2018-11-22
# Author:      taojianwen
#
#-------------------------------------------------------------------------------

if [ $# -eq 0 ]; then
   echo "Usage! $0 <project>"
   exit
fi

# 保存脚本当前路径
OLD_PWD=`pwd`
PROJECT="$1"
DATE=`date +%F_%H%M`
#保存备份路径
PATH=/deploy/$PROJECT/bak
APPDIR=/data/$PROJECT
echo ${APPDIR}
if [ ! $? -eq 0 ];then 
   echo "Usage! $0 <project>"
   exit
fi
if [ ! $2 ];then
NOW=${DATE}
else
NOW=$2
fi
test -d  $PATH || mkdir $PATH
test -d  ${PATH}/${PROJECT}_backup_${NOW} || mkdir ${PATH}/${PROJECT}_backup_${NOW}
BACKDIR=${PATH}/${PROJECT}_backup_${NOW}
if [ -z $PROJECT ]; then
        echo "Usage! $0 <project>"
        exit
else
        if [ -d ${BACKDIR} ];then
            cd ${BACKDIR}
            tar -cvzPf ${PATH}/${PROJECT}_full_backup_${NOW}.tar.gz --exclude=logs --exclude=download --exclude=tmp  --exclude=${PROJECT}.jar ${APPDIR}
        else
            echo "Error, directory ${BACKDIR} not exist, Exiting....."
         fi
fi

