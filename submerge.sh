#!/bin/bash
#
# This script attempts to merge a srt file into the
# mkv container on track 0 and mark it as English.
#
# deegan @ freenode
# hakan@monkii.net
#

if [ ! $1 ]; then
    echo "Usage: $0 <dir>"
    exit 0;
fi

cd $1

echo "----------------------------------------------------------------------------------"
echo "CWD: $1"

SRT=$(ls *.srt)
MKV=$(ls *.mkv)

if [ -f $SRT ]; then
    echo "MKV: $MKV"
    echo "SRT: $SRT"
    mv $MKV tmp.mkv
    mkvmerge -o $MKV --default-track 0 --language 0:eng $SRT tmp.mkv
    if [ $? -eq 0 ]; then
        echo "Removing tmp.mkv and $SRT .."
        rm tmp.mkv
        rm $SRT
    else
        echo "there was a problem with $MKV, aborting.."
        mv tmp.mkv $MKV
    fi
else
    echo "No srt found.."
fi

cd ..
echo "----------------------------------------------------------------------------------"
