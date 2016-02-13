#!/bin/bash
#
# checks for no-srt files in movie/tv folders
# and makes an attempt at downloading a srt.
#
# - hakan@monkii.net
export PATH=$PATH:/home/htpc/bin/

LASTCHECK="Last checked: $(date)"
DIRS="/mnt/drives/mnt2/movies /mnt/drives/mnt3/tv"
# CRAWLDIR="/mnt/drives/mnt3/tv"

for CRAWLDIR in $DIRS; do
    find $CRAWLDIR -type f -name no-srt -print | while read f ; do
        DIR=${f::-6}
        cd "$DIR"
        MKV=`ls -u *.mkv|head -1 2> /dev/null`
        echo "Attempting to download subs.. [$DIR/$MKV]"
        if [ -f $MKV ]; then
            periscope --quiet $MKV
            if [ ! -f *.srt ]; then
                subdownloader.sh $MKV
            fi
            if [ -f *.srt ]; then
                rm no-srt
            else
                echo $LASTCHECK >> no-srt
            fi
        fi
    done
done
