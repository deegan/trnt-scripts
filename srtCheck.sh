#!/bin/bash
# find movies with missing srts.

USAGE="Usage: $0 <directory>"
FILTER="1080p|720p|xvid|episode|dvdrip|UFC"

if [ "$1" ]; then
    tree="$1"
    echo "Tree: [$tree]"
else
    echo $USAGE
    exit 0;
fi

cd "$tree"
echo "CWD: [$tree]"
echo "PWD: [$(pwd)]"

for i in `tree -d -i|egrep -i "$FILTER"`; do
    if [ $i != "Subs" ] && [ $i != "Sample" ]; then
        cd "$i"
        if [ ! -f *.srt ]; then
            echo "Current dir: ["$i"]"
            echo "No subtitle found."
            touch no-srt
        fi
    fi
    cd $tree 
done

