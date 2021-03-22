#!/bin/bash
#
# unpacks movies and tv-shows and deletes the rar's, but only
# if successful. Can be used standalone or together with episodeSorter.py
#
# ugly code, but it works. //deegan @ IRCnet.
#
export IFS=$'\n'
USAGE="Usage: unpack.sh <directory>"
FILTER="2160p|1080p|720p|xvid|episode|dvdrip|UFC"
SINGLE="0"
PACKFILTER="Trilogy|Duology|PACK|Pack"
REPACK_FILTER="Repack|REPACK|repack"
IS_PACK="0"
echo "Filter: $FILTER"

# Takes one argument.
if [ "$1" ]; then
    tree="$1"
    echo "Tree: [$tree]"
    res=$(echo $tree|egrep -v $REPACK_FILTER|egrep $PACKFILTER)
    if [ $? -eq 0 ]; then
        IS_PACK="1"
    fi
else
    echo $USAGE
    exit 0;
fi

# We actually take two arguments, but this is not required.
# Only use this if you are not plowing through a
# pile of directories.
# example usage: unpack.sh /tmp/movies/My.Movie.1080p 1
#
if [ "$3" ]; then
    SINGLE=1
fi

# Defining funtions.
# Function subextract.
# tries to locate any pre-existing subs in any given folder and unpack that.
function subextract {
    movieDir=$1
    subsDir="$movieDir/Subs"
    
    if [ $subsDir ]; then
        echo "Entering $subsDir.."
        cd $subsDir
        rar=`ls *.rar`
        if [ $rar ]; then
            echo "Found subs rar. $rar"
            unrar yx $rar $movieDir
            rar_in_rar=`ls $movieDir/*.rar`
            if [ $rar_in_rar ]; then
                echo "We unpacked another rar.."
                cd $movieDir
                unrar ye $rar_in_rar
            fi
        else
            echo "Non rar found in $subsDir"
        fi
    else
        echo "No subs dir found, exiting."
    fi
}

# Force update of the plex library.
function updatePlexLibrary {
    curl -vL -H "X-Plex-Token: <TOKEN>" "http://192.168.2.2:32400/library/sections/1/refresh?force=1"
}

# let's enter the root of our directory tree.
# this should be 1 step up from wherever your rar-files are.
# ie: /path/movies/, not /path/movies/mymovie
# ie: /path/tv/show/season\ 1/, not /path/tv/show/season\ 1/episode01
# 
cd "$tree"
echo "CWD: [$tree]"
echo "PWD: [$(pwd)]"
echo "IS_PACK: [$IS_PACK]"

# if we're doing a single ep/movie.
if [ $SINGLE == "1" ]; then
    i=$tree
    cd "$i"
    FILE=`ls -U *.rar *.r[0-9][0-9]|head -1 2> /dev/null`
    MKV=`ls -u *.mkv|head -1 2> /dev/null`
    if [[ ! -f "$i"/"$FILE" ]] && [[ $IS_PACK != "1" ]]; then
        echo "no rar-file, moving on. [$FILE]"
        if [ -f $MKV ]; then
            echo "Found videofile [$MKV]. copying to $2"
            cp $MKV $2
        fi
    elif [ $IS_PACK == "1" ]; then
        for dir in *BluRay*; do
            cd $dir
            unrar e -o+ *.rar $2
            if [ $? -eq 0 ]; then
                cd $2
                # Subtitles.
                subextract $dir
                cd $dir
                MKV=`ls -u *.mkv|head -1 2> /dev/null`
                echo "Attempting to download subs.. [$1/$MKV]"
                if [ -f $MKV ]; then
                    periscope --quiet -l en -l sv $MKV
                    if [ ! -f *.srt ]; then
                        subdownloader.sh $MKV
                    fi
                    if [ ! -f *.srt ]; then
                        touch no-srt
                    else
                        rm no-srt
                    fi
                fi
                cd ..
            fi
        done
    else
        echo $FILE
        unrar e -o+ $FILE $2
        if [ $? -eq 0 ]; then
            cd $2
            # Subtitles.
            subextract $i
            cd $i
            MKV=`ls -u *.mkv|head -1 2> /dev/null`
            echo "Attempting to download subs.. [$1/$MKV]"
            if [ -f $MKV ]; then
                periscope --quiet -l en -l sv $MKV
                if [ ! -f *.srt ]; then
                    subdownloader.sh $MKV
                fi
                if [ ! -f *.srt ]; then
                    touch no-srt
                else
                    rm no-srt
                fi
            fi
        fi
    fi
else
# so for each directory we get a neat list of stuff to plow through
# ignoring Subs and Sample directories because they fuck everything up.
    for i in `tree -d -i|egrep -i "$FILTER"`; do
        if [ $i != "Subs" ] && [ $i != "Sample" ]; then
            echo "Current dir: ["$i"]"
            cd "$i"
            FILE=`ls -U *.rar|head -1 2> /dev/null`
            if [ ! -f "$tree"/"$i"/$FILE ]; then
                echo "no rar-file, moving on. [$FILE]"
            else
                if [ ! -f currently-unpacking ]; then 
                    touch currently-unpacking
                    echo $FILE
                    unrar e -o+ $FILE
                    if [ $? -eq 0 ]; then
                        echo "Deleting rar's.. [$FILE]"
                        rm *.rar *.r[0-9][0-9] 
                        rm -rf Sample/ Proof/
                        rm currently-unpackning
                        updatePlexLibrary
                        # Subtitles.
                        subextract $i
                        cd $i
                        MKV=`ls -u *.mkv|head -1 2> /dev/null`
                        echo "Attempting to download subs.. [$1/$MKV]"
                        if [ -f $MKV ]; then
                            periscope --quiet -l en -l sv $MKV
                            if [ ! -f *.srt ]; then
                                subdownloader.sh $MKV
                            fi
                            if [ ! -f *.srt ]; then
                                touch no-srt
                            else
                                rm no-srt
                            fi
                        fi
                    fi
                fi
            fi
        fi
        cd ..
    done
fi
