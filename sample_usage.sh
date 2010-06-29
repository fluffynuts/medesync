#!/bin/zsh
# this shell script illustrates example usage for medesync
#	this script is (very nearly) what I have in my crontab
#	for some wee hour in the morning. Note that medesync
#	is designed for "job runs", so I have multiple runs to
#	deal with series, movies, animated, etc
#	my local sources all look like:
#	/base/<type>
#						/new
#						/watched
# my remote syncs are just of the format:
# /<type>
#	* items in (new) dirs are synced to the player
#	* items marked as watched by the player (player
#			generates a file of the same path, but ending
#			in .t, containing the local path (according to
#			the player) of the file) will be archived to
#			the relative (watched) dirs
#	
PIDFILE="/tmp/update_mede8er.pid"
FTP_USER="anonymous"
FTP_PASS="foo@bar.com"
# check that we're not already running...
if test -f $PIDFILE; then
	OTHERPID=$(cat $PIDFILE)
	OTHERPROCESS=$(ps -p $OTHERPID -o comm=)
	if test ! -z "$OTHERPROCESS"; then
		echo "Bailing out: mede8er update already running with pid $OTHERPID"
		exit 1
	fi
fi
echo -n "$$" > $PIDFILE
src_base="/mnt/media"
SS=$(dirname $0)/medesync.py
dst_base="ftp://$FTP_USER:$FTP_PASS@mede8er"
for d in movies series animated comedy; do
	echo " === syncing $d ==="
	$SS -s $src_base/$d/new -d $dst_base/$d -a $src_base/$d/watched
done
# remove running state file
rm -f $PIDFILE
