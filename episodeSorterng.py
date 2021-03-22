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

# start input
if len(sys.argv) > 1:
    filename = str(sys.argv[1])
    category = str(sys.argv[2])
    if (category == "TV"):
        src = "/mnt/drives/mnt3/torrent/downloaded/tv/"
    elif (category == "MOVIE"):
        src = "/mnt/drives/mnt3/torrent/downloaded/movies/"
    elif (category == "4K"):
        src = "/mnt/drives/mnt3/torrent/downloaded/4k/"
else:
    print(bcolors.FAIL + "ERROR: You need to supply a directory.")
    print(bcolors.HEADER + "USAGE: episodeSorter.py <directory>" + bcolors.ENDC)
#    raise Exception('Incorrect data')
# end input

# define some variables to be used.
# src = where you keep your downloaded torrents.
# src = "/mnt/drives/mnt3/torrent/downloading/"
# src = os.getcwd() + "/"
# dst : initializing for later use.
dst = ""
# dstTv = where you keep your tv shows, doesn't support multi-tier stuff
# because that shit is retarded. lern2plex, or something.
dstTv = "/mnt/drives/mnt2/tv/"
# dstMovie = where you keep your movies, again no multi-tier crap.
dstMovie = "/mnt/drives/mnt1/movies/hd/"
dstMovie4k = "/mnt/drives/mnt1/movies/4k/"
# Like fighting? no? 
dstUFC = "/mnt/drives/mnt2/ufc/"
# system variables.
# filename        = str(sys.argv[1])
# sanity check variables.
episodeExists   = "0"
movieExists     = "0"




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

# Get the movie name.
def getMovieName(filename):
    match = re.search(r'^(.*?)\W(?:(\d{4})(?:\W(\d+p)?)|(\d+p)(?:\W(\d{4}))?)\b', filename)
    if match:
        return match.group(0)

# This function looks for BluRay. It should be safe to assume that
# only movies use this tag. Also this match is made after we have
# determined if we have Season + episode, ie. if it's a Tv Show.
def getMovie(filename):
    uhd = re.search (r'(2160p)\s', filename)
    if uhd:
        dstMovie = "/mnt/drives/mnt1/4k"
    match = re.search(r'(BluRay|Bluray|BRRip|Blue-ray|Blue-Ray)\s*', filename)
    if match:
        return match.group(1)

# This filters on UFC events.
def getUFC(filename):
    match = re.search(r'(?ix)(^UFC\.[\d]{3})', filename)
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
MovieName       = getMovieName(filename)
ShowName        = getShowName(filename)
Season          = getSeason(filename)
Episode         = getEpisode(filename)
Movie           = getMovie(filename)
UFC             = getUFC(filename)

# If the functions declared earlier to fetch Season and Episode return anything
# other than a None type, we are dealing with a Tv-Show.
# if (ShowName is not None and Season is not None and Episode is not None):
if (category == "TV" ): 
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
        # trying something new. let's not copy everything, instead we unpack
        # from dir to dir.
        # os.makedirs(dst+filename)
        # sourcepath = src+filename
        # old behaviour was to copy evertything and then unpack.
        # copyEpisode(src+filename,dst+filename)
        #
        # create directory for unpack dst.
        print("Creating directory: [" + dst + filename + "]")
        os.makedirs(dst+filename)
        print(bcolors.OKBLUE + "Calling unpackng.sh..." + bcolors.ENDC)
        fullpath = dst+filename
        srcpath = src+filename
        subprocess.call(["/home/htpc/bin/unpackng.sh", srcpath, fullpath, "1"])
    else:
        print("Found a match: " + bcolors.OKBLUE + filename + bcolors.ENDC + " -> " + bcolors.WARNING + matchedEpisode + bcolors.ENDC)
        print(bcolors.FAIL + "episodeExists: " + bcolors.ENDC + episodeExists)
# If Season and Episode return None and Movie does not return a None value we
# are dealing with a Movie.
# elif (ShowName is not None and Movie is not None and Season is None and Episode is None):
elif (category == "MOVIE"):
    dst = dstMovie
    listing = os.listdir(dst)
    for checkfile in listing:
        if checkfile.startswith(MovieName):
            movieExists = "1"
            movieExistName = checkfile
    if (movieExists == "0"):
        print("No match for "+ bcolors.OKBLUE + filename + bcolors.ENDC + " in " + dst)
        print(bcolors.OKGREEN + "movieExists: " + bcolors.ENDC + movieExists)
        #print("Copying " + src + filename + " to " + dst + filename)
        #copyEpisode(src+filename,dst+filename)
        print("Creating directory: [" + dst + filename + "]")
        os.makedirs(dst+filename)
        print(bcolors.OKBLUE + "Calling unpackng.sh..." + bcolors.ENDC)
        fullpath = dst+filename
        srcpath = src+filename
        subprocess.call(["/home/htpc/bin/unpackng.sh", srcpath, fullpath, "1"])
        subprocess.call(["/home/htpc/bin/radarrRefresh.py", filename])
    else:
        print("Found a match: " + bcolors.OKBLUE + filename + bcolors.ENDC + " -> " + bcolors.WARNING + movieExistName + bcolors.ENDC)
        print(bcolors.FAIL + "movieExists: " + bcolors.ENDC + movieExists)
elif (category == "4K"):
    dst = dstMovie4k
    listing = os.listdir(dst)
    for checkfile in listing:
        if checkfile.startswith(MovieName):
            movieExists = "1"
            movieExistName = checkfile
    if (movieExists == "0"):
        print("No match for "+ bcolors.OKBLUE + filename + bcolors.ENDC + " in " + dst)
        print(bcolors.OKGREEN + "movieExists: " + bcolors.ENDC + movieExists)
        #print("Copying " + src + filename + " to " + dst + filename)
        #copyEpisode(src+filename,dst+filename)
        print("Creating directory: [" + dst + filename + "]")
        os.makedirs(dst+filename)
        print(bcolors.OKBLUE + "Calling unpackng.sh..." + bcolors.ENDC)
        fullpath = dst+filename
        srcpath = src+filename
        subprocess.call(["/home/htpc/bin/unpackng.sh", srcpath, fullpath, "1"])
    else:
        print("Found a match: " + bcolors.OKBLUE + filename + bcolors.ENDC + " -> " + bcolors.WARNING + movieExistName + bcolors.ENDC)
        print(bcolors.FAIL + "movieExists: " + bcolors.ENDC + movieExists)
# If we have a UFC event.
# elif (UFC is not None):
#     fullpath = dstUFC+filename
#     copyEpisode(src+filename,fullpath)
#     subprocess.call(["/usr/local/bin/unpack.sh", fullpath, "1"]) 
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
