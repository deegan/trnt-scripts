# trnt-scripts
A collection of scripts that does stuff to you torrents. I'll leave the
spagetti-code-decryption to those knowledgable.

A perfect use example is this in rtorrent.rc: 
# rtorrent.rc
system.method.set_key = event.download.finished,execute=~/bin/episodeSorter.py,$d.get_name="

# ToDo
* argparser instead of variables in code.
* refractor some of the code that is duplicated.
* clean up error / information messages.
