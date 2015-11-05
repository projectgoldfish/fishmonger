## Python modules included
import os
import sys

## Fishmonger modules included
import fishmonger.config     as FishConfig
import fishmonger.exceptions as FishExceptions

## Assure we have the minimum version of python required
if sys.version_info < (2, 7):
	raise "Requires python 2.7+"

## Catch ctrl+c and exit cleanly
def ctrl_c(signal, frame):
	PyLog.log("Exiting on CTRL+C")
	sys.exit(0)
signal.signal(signal.SIGINT, ctrl_c)

def detectAppDirs(self, parent=None, root=".", app_dirs=[]):
	app_dirs.append((parent, root))
	src_dir   = os.path.join(root, "src")
	PyLog.debug("Finding app dirs in ", src_dir, log_level=6)
	
	nparent = root
	dirs    = []
	if os.path.isdir(src_dir):
		dirs = PyFind.getDirDirs(src_dir)
	else:
		nparent = parent
		dirs    = PyFind.getDirDirs(root)

	PyLog.debug("Found app dirs", dirs, log_level=8)
	for d in dirs:
		if os.path.basename(d)[0] != ".":
			self.findAppDirs(nparent, d, app_dirs)

	return app_dirs
