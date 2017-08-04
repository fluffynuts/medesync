This is a simple application to synchronise two folders. It was designed for
synchronising media across FTP to a mede8er player but should (in theory) be
able to sync local->local, local->ftp, ftp->local. Though the last hasn't really
been tested. Shout if it's important to you.

To use, you need python -- at least v 2.6. 3.1 seems to work as well -- though
this has only been briefly tested. Again, feed back if this is an issue, please!

Ok, so this should work on any python-capable system. Once you have a working
python install (it's "just there" on any decent Linux distro; alternatively
install ActivePython for windows), unpack this zip file somewhere and run

> medesync.py -h
or
> medesync.py --help
for more verbose help

Run from a console, of course. Usage is quite simple -- the help and sample
shell script should help out. I have this running in a cron job at night so
that my mede8er stays up to date and watched items (the watched indicator
only came in from firmware v3) are removed from the player, making finding
and playing something new / the next episode in a series much easier.

A note on how archiving works:

If you specify an archive directory with -a, medesync looks for files on the
remote host which have been marked as watched by the mede8er. The mede8er does
this in a very simple manner: it just creates a .t file in the same dir; ie
if you watched Aliens.avi, then a file Aliens.avi.t would appear in that folder.

When medesync sees one of these files, it removes the remote file and the
watched indicator file and moves the corresponding local file into the archive
folder. So your media isn't lost -- just moved to make it easier to get into
the new stuff!

This software is released under the BSD license. The license is very permissive:
basically the only thing you can't do is claim this is your own work. The source
is available for modification and I would appreciate it if any modifications
are submitted back for inclusion into the project.

Finally, I accept NO RESPONSIBILITY for the usage of this script IN ANY WAY. If
you lose precious videos because of this script, I'm sorry -- but I'm not
responsible. You shouldn't though -- I've been using this for at least 6 months
now, reliably.

If you have any queries or issues, you can email me at davydm@gmail.com
Please be patient with reply time (:
