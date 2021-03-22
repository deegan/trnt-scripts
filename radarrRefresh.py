#!/usr/bin/python3
#
# Quick hack made because to update the path of a given movie in Radarr. If you
# only use a blackhole solution for torrents and at the same time are not
# using Radarr to move your finnished torrents to their final destination, you
# will find that your "Wanted" movies will be stuck as missing forever and ever
# until you update the path yourself, which is a manual job in the Web GUI
# which we like to avoid.
#
# This script takes a single argument and that is the name of your movie as it
# has downloaded, so My.Movie.1080p.BluRay-GROUP for example. The script is
# best suited to be run either in your .rtorrent.rc file or wrapped in some
# other script that does POST processing today.
#
# Order of operations:
# 1) Take input, clean up the name to mostly include just the movie name.
# 2) searchImdb for a ImdDBid.
# 3) getRadarrID get's all movies in Radarr and we match on ImDBid and return
#    the internal Radarr movie ID.
# 4) updateRadarrID takes the internal radarrid + movie name and updates the
#    path and calls for Radarr to refresh the movie so it goes from Missing to
#    Downloaded status.
#
# deegan @ Discord / IRC
# 
import imdb
import sys
import re
import json
import requests

# define global variables that should not change.
apikey = "YOUR_API_KEY"
apiurl = "192.168.2.2:7878/api/v3/movie"
apicmd = "192.168.2.2:7878/api/v3/command"

# initialize object.
ia = imdb.IMDb()

# clean up name.
def getMovieName(filename):
    match = re.search(r'^(.*?)\W(?:(\d{4})(?:\W(\d+p)?)|(\d+p)(?:\W(\d{4}))?)\b', filename)
    if match:
        return match.group(0)

# search imdb for a id.
def searchImdb(name):
    #movie = getMovieName(name)
    result = ia.search_movie(name)
    imdbID = "tt"+result[0].movieID
    return imdbID

# search Radarr and match on imdbid.
# return Radarr internal id.
def getRadarrID(imdbid):
    count = 0
    radarrid = 0
    response = requests.get("http://"+apiurl+"?apikey="+apikey) # get it all.
    parsed = json.dumps(response.json(), indent=4)
    loaded = json.loads(parsed)
    for item in loaded:
        imdbId = item.get('imdbId')
        if imdbId == imdbid:
            radarrid = item.get('id')
            print("Match: "+imdbid+"->"+imdbId+"")
            print("RadarrID: " + str(radarrid) + "")
        count+=1;
    return radarrid

# Update the movie in radarr with the actual path.
def updateRadarrID(radarrid, movie):
    response = requests.get("http://"+apiurl+"/"+radarrid+"?apikey="+apikey)
    parsed = json.dumps(response.json(), indent=4)
    loaded = json.loads(parsed)
    oldpath = loaded['path']
    newpath = "/mnt1/movies/hd/"+movie
    loaded['path'] = loaded['path'].replace(oldpath, newpath)
    loaded['folderName'] = loaded['folderName'].replace(oldpath, newpath)
    put = requests.put("http://"+apiurl+"/"+radarrid+"?apikey="+apikey,data=json.dumps(loaded))
    res = put.json()
    print(res)
    print("--------")
    ref_json = '{"name": "RefreshMovie", "movieIds": ['+radarrid+']}'
    ref_json = json.loads(ref_json)
    refresh = requests.post("http://"+apicmd+"?apikey="+apikey,data=json.dumps(ref_json))
    ref = refresh.json()
    print(ref)
#
# int main() LUL
#
if len(sys.argv) > 1:
    movie = getMovieName(sys.argv[1])
    movie = movie.replace("1080p","")
    movie = re.sub("\d{4}", "", movie)
    movieFolder = sys.argv[1].replace(".mkv","")
    print("Movie: " + movie)
    imdbID = searchImdb(movie)
    print("imdbID: " + imdbID)
    radarrId = getRadarrID(imdbID)
    if radarrId != 0:
        print("Not zero: " + str(radarrId))
        updateRadarrID(str(radarrId), movieFolder)
