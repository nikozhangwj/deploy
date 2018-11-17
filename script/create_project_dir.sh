<<<<<<< HEAD
# !/bin/bash
=======
#!/bin/bash
>>>>>>> f7543d14941cee4b7501a33106e6f571f75b3f48

if [ $# -eq 0 ];then
echo "empty"
echo "usage:"
echo "APP_NAME"
exit 1;
fi


APP_NAME=$1
<<<<<<< HEAD
mkdir -p /data/${APP_NAME}/{tmp,download,static,secrets,bin,config,logs}
=======
mkdir -p /data/${APP_NAME}/{tmp,download,static,secrets,bin,config,logs}
>>>>>>> f7543d14941cee4b7501a33106e6f571f75b3f48
