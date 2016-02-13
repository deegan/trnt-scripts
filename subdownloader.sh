#!/bin/bash
python /home/htpc/subdownloader/run.py -c -l eng,sv $1 1> /dev/null

SRT=*.srt
# MKV=`$1|sed 's/.mkv//'`

if [ -f $SRT ]; then
    echo "Downloaded: $SRT"
else
    echo "No srt found.."
fi

