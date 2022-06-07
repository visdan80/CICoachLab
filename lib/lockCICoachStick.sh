#!/bin/bash

mountPathEncrypted=$1
mountPathClear=$2

#echo $mountPathEncrypted
#echo $mountPathClear


sudo umount  $mountPathClear
if [ $? -ne 0 ]; then
    echo 'umount: unmounting decrypted mount failed:' "$mountPathClear"
    exit 1
fi
sudo umount $mountPathEncrypted
if [ $? -ne 0 ]; then
    echo 'umount: unmounting encrypted mount failed:' "$mountPathEncrypted"
    exit 2
fi

echo 'Nothing failed'

exit 0
