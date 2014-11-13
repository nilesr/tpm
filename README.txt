Ok this is it

The server has a directory of 7zipped files, packages
This list is complete
The server, every 12 hours or so goes through all the files in this directory and puts their info into a master BTEdb database
It then generates a torrent files
Both the database and torrent file are served over HTTP using a WSGI application
The torrent file is also used for a torrent client on the server which will act as the initial seeder

The daemon has an upstart job with a PID file and a daemon thread, which is a lot easier to set up than it sounds. The hard part is killing the daemon
This daemon gets both the torrent file and the package index from the server, makes a BTEdb database object out of the package index and starts the torrent file (replacing any older one) with the same directory, so old files are still seeded within the new torrent. It populates this list based on it's own list of installed packages, which is kept track of by the daemon in a different BTEdb database on the client
This directory is only partial, and only has the packages installed on the client

The CLI process accesses most things through interprocess communication using FIFO pipes and lockfiles. 
For example, if you run tpm install libexample, it would open the pipe and request information on libexample. This returns the information to the cli process, which can find in that data the list of dependencies. It continues recursing until it has a list of all packages that must be installed, then prompts the user (overridable with a command line option, and the user is not prompted if there are no uninstalled dependencies). The CLI process then tells the daemon to begin downloading some files. The daemon tells the client when each file is done, and the client installs them.

Each package file is a 7z archive with two folders, this is an example

libexample-0.1-x86_64.7z
	data
		usr
			lib
				libexample.so.0
				libexample.so.1
	info
		preinstall
		postinstall
		preupgrade
		postupgrade
		preremove
		postremove
		package.json

package.json is a BTEdb database with these objects
	Version
	Maintainer
	Description
	Dependencies
	Type
Type may be one of either "Binary" or "Source"
Binary packages have pre/post scripts run and are extracted directly to / (or a prefix specified with a command line argument)
Source packages do NOT have pre/post scripts run on them and are extracted to a temporary directory created with the mktemp command in /tmp/tpm. There, ./configure --prefix=/opt/tpm/buckets/(packagename), make and make install are run, returning an error if any of them exit uncleanly. Files are then recursively symlinked
On any install, before installing (we will use the install command) we check to see if there is any conflict with previously installed packages using package receipts. 
After installation, the files that were installed and the current version of the package is stored in a receipt on-disk, and the version and name are stored in the client configuration by the daemon