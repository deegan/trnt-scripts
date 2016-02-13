# trnt-scripts
A collection of scripts that does stuff to you torrents. I'll leave the
spagetti-code-decryption to those knowledgable.

A perfect use example is this: system.method.set_key =
# rtorrent.rc
event.download.finished,execute=~/bin/episodeSorter.py,$d.get_name="
