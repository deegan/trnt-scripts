#!/usr/bin/python
# 
# The purpose of this script is to be called by rtorrent, or anything
# like that, after a torrent has finished downloading. It's
# as simple as it is genious: do some regexp to figure what we are
# looking at and if we find a match we copy it to the desired destination.
#
# There's also a call to "unpack.sh" which does some simple logic and unpacks
# the files so that Plex can index them, it also makes a valiant attempt at
# fetching subtitles using periscope which you will have to install yourself
# but is not required, it will just throw an error saying "no such command".
#
# ugly code, but it works. // deegan @ IRCnet.
#
# imports
import re
import sys
import os
import shutil
import errno
import subprocess

# define some variables to be used.
# src = where you keep your downloaded torrents.
src = "/mnt/drives/mnt2/torrent/downloading/"
# dst : initializing for later use.
dst = ""
# dstTv = where you keep your tv shows, doesn't support multi-tier stuff
# because that shit is retarded. lern2plex, or something.
dstTv = "/mnt/drives/mnt3/tv/"
# dstMovie = where you keep your movies, again no multi-tier crap.
dstMovie = "/mnt/drives/mnt2/movies/"
# system variables.
# filename        = str(sys.argv[1])
# sanity check variables.
episodeExists   = "0"
movieExists     = "0"

# start fancy stuff.
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
# end fancy stuff.

if len(sys.argv) > 1:
    filename = str(sys.argv[1])
else:
    print(bcolors.FAIL + "ERROR: You need to supply a directory.")
    print(bcolors.HEADER + "USAGE: episodeSorter.py <directory>" + bcolors.ENDC)
#    raise Exception('Incorrect data')


# start functions to grab information from input.
# This function grabs the Episode number NN.
def getEpisode(filename):
    match = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          e|episode|^             # e or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)
    if match:
        return match.group(1)

# This function grabs the Season number NN.
def getSeason(filename):
    match = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          s|season|^              # s or season or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)
    if match:
        return match.group(1)

# This function grabs the Episode name, Show.Name.
def getShowName(filename):
    match = re.search(r'(?P<show>[\w\s.,_-]+?)\.[Ss]?(?P<season>[\d]{1,2})[XxEe]?(?P<episode>[\d]{2})', filename)
    if match:
        return match.group(1)

# This function looks for BluRay. It should be safe to assume that
# only movies use this tag. Also this match is made after we have
# determined if we have Season + episode, ie. if it's a Tv Show.
def getMovie(filename):
    match = re.search(r'(BluRay|Bluray)\s*', filename)
    if match:
        return match.group(1)

# This function will copy the src to dst.
def copyEpisode(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

# end functions.

# for filename in os.listdir(src):
ShowName        = getShowName(filename)
Season          = getSeason(filename)
Episode         = getEpisode(filename)
Movie           = getMovie(filename)

# If the functions declared earlier to fetch Season and Episode return anything
# other than a None type, we are dealing with a Tv-Show.
if (ShowName is not None and Season is not None and Episode is not None):
    dstTv = dstTv+ShowName+"/Season "+re.sub("^0+","",Season+"/")
    dst = dstTv
# If the ShowName does not exist under our tv-root, we create it.
    if not os.path.exists(dstTv+ShowName):
        os.makedirs(dstTv+ShowName)
# If the Season does not exist we create it.
    if not os.path.exists(dst):
        os.makedirs(dst)
# Loop through all possible directories under tv-root/ShowName/Season to see if
# we already have a matching episode in our library.
    for checkfile in os.listdir(dst):
        epid = getEpisode(checkfile)
# If we happen to stumble on a duplicate Episode we set episodeExists=1
        if ( epid == Episode ):
            episodeExists = "1"
            matchedEpisode = checkfile
# Otherwise, continue copying Episode to Season dir.
    if (episodeExists == "0"):
        print("No match for "+ bcolors.OKBLUE + filename + bcolors.ENDC + " in " + dst)
        print(bcolors.OKGREEN + "episodeExists: " + bcolors.ENDC + episodeExists)
        print("Copying " + filename + " to " + dst)
        copyEpisode(src+filename,dst+filename)
        print(bcolors.OKBLUE + "Calling unpack.sh..." + bcolors.ENDC)
        fullpath = dst+filename
        subprocess.call(["/home/htpc/bin/unpack.sh", fullpath, "1"])
    else:
        print("Found a match: " + bcolors.OKBLUE + filename + bcolors.ENDC + " -> " + bcolors.WARNING + matchedEpisode + bcolors.ENDC)
        print(bcolors.FAIL + "episodeExists: " + bcolors.ENDC + episodeExists)
# If Season and Episode return None and Movie does not return a None value we
# are dealing with a Movie.
elif (ShowName is not None and Movie is not None and Season is None and Episode is None):
    dst = dstMovie
    listing = os.listdir(dst)
    for checkfile in listing:
        if checkfile.startswith(ShowName):
            movieExists = "1"
            movieExistName = checkfile
    if (movieExists == "0"):
        print("No match for "+ bcolors.OKBLUE + filename + bcolors.ENDC + " in " + dst)
        print(bcolors.OKGREEN + "movieExists: " + bcolors.ENDC + movieExists)
        print("Copying " + filename + " to " + dst)
        copyEpisode(src+filename,dst+filename)
        print(bcolors.OKBLUE + "Calling unpack.sh..." + bcolors.ENDC)
        fullpath = dst+filename
        subprocess.call(["/home/htpc/bin/unpack.sh", fullpath, "1"])
    else:
        print("Found a match: " + bcolors.OKBLUE + filename + bcolors.ENDC + " -> " + bcolors.WARNING + movieExistName + bcolors.ENDC)
        print(bcolors.FAIL + "movieExists: " + bcolors.ENDC + movieExists)
# Otherwise, something went terribly wrong. Time to start debugging?
else:
    print(bcolors.FAIL + "Zero freaking matches son! Get your head out of your ass.." + bcolors.ENDC)
    print(bcolors.WARNING + "sys.argv[1] -> " + sys.argv[1] + bcolors.ENDC)
# filename = str(sys.argv[1])

# print(filename, "->", getShowName(filename), getSeason(filename), getEpisode(filename))

# uncomment this stuff if you want to run some tests. only for dev i guess.
# tests = (
#     'Series Name s01e01.avi',
#     'Series Name 1x01.avi',
#     'Series Name episode 01.avi',
#     '01 Episode Title.avi',
#     'American.Dad.S01E01.720p.HDTV-IMMERSE'
#     )

#for filename in tests:
#    print("-----------------")
#    print(filename, "->", getShowName(filename), getSeason(filename), getEpisode(filename))
#    print(filename, "Episode", getEpisode(filename))
#    print(filename, "Season",  getSeason(filename))
#    print(filename, "ShowName", getShowName(filename))
