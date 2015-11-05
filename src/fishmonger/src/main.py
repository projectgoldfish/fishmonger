## Python modules included
import os
import sys
import signal

## Fishmonger modules included
##import fishmonger.config     as FishConfig
##import fishmonger.exceptions as FishExceptions

## PyBase modules included
import pybase.log       as PyLog
import pybase.find      as PyFind

if sys.version_info < (2, 7):
	"""
	Assure that python is at least 2.7

	This is required for list and dict comprehension support.
	"""
	raise "Requires python 2.7+"

def ctrl_c(signal, frame):
	"""
	Catch CTRL+C and exit cleanly
	"""
	PyLog.log("Exiting on CTRL+C")
	sys.exit(0)
signal.signal(signal.SIGINT, ctrl_c)

def detectAppDirs(parent=None, root=".", app_dirs=None):
	"""
	detectAppDirs(string()::Parent, string()::Root, [()]|None::AppDirs) ->

	Scans the 
	"""
	if app_dirs == None:
		app_dirs = []

	app_dirs.append((parent, root))
	src_dir   = os.path.join(root, "src")
	#PyLog.debug("Finding app dirs in ", src_dir, log_level=6)
	
	nparent = root
	dirs    = []
	if os.path.isdir(src_dir):
		dirs = PyFind.getDirDirs(src_dir)
	else:
		nparent = parent
		dirs    = PyFind.getDirDirs(root)

	#PyLog.debug("Found app dirs", dirs, log_level=8)
	for d in dirs:
		if os.path.basename(d)[0] != ".":
			detectAppDirs(nparent, d, app_dirs)

	return app_dirs

print detectAppDirs(None, "../" + os.getcwd().split("/")[-1])