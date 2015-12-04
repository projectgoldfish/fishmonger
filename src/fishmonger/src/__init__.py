## Python modules included
import os
import sys

## PyBase modules included
import pybase.log       as PyLog
import pybase.find      as PyFind

## Fishmonger modules included
import fishmonger.exceptions as FishExc
import fishmonger.toolchains as FishTC

def addToolChains(array, target, prefix=""):
	if isinstance(array, basestring):
		array = [array]

	if prefix != "":
		prefix += "."

	modules = []
	for c in array:
		modules.append(prefix + c)
	PyUtil.loadModules(modules, target)
	PyUtil.loadModules(modules, AllToolChains)

def getAppDirs(root = "."):
	"""
	getAppDirs(string()::Root) -> [string()]::Return

	Scans the directory structure to determine the application directories.

	Root   - The Directory to start scanning from.

	Return - A list of directories that are root directories for applications
	"""

	def scanSrcDirs(parent=None, root=".", app_dirs=None):
		"""
		scanSrcDirs(string()::Parent, string()::Root, [()]|None::AppDirs) ->

		Scans the directory structure for src directories and thier parents.
		"""
		if app_dirs == None:
			app_dirs = []

		app_dirs.append((parent, root))
		src_dir   = os.path.join(root, "src")
		
		nparent = root
		dirs    = []
		if os.path.isdir(src_dir):
			dirs = PyFind.getDirDirs(src_dir)
		else:
			nparent = parent
			dirs    = PyFind.getDirDirs(root)

		for d in dirs:
			if os.path.basename(d)[0] != ".":
				scanSrcDirs(nparent, d, app_dirs)

		return app_dirs

	def makeAppDirTree(acc, dirs):
		(parent, child) = dirs
		
		children = acc.get(parent, [])
		children.append(child)
		acc[parent] = children

		return acc

	tree = reduce(makeAppDirTree, scanSrcDirs(None, root, None), {})

	app_dirs = []
	parents  = set(tree.keys())
	for app_dir in parents:
		if parents & set(tree[app_dir]) == set():
			app_dirs.append(app_dir)
	return app_dirs

def configure():
	"""
	configure() -> [{}]

	Generates base app configuration for all used tool chains.
	"""

	pass

def configureStage():
	pass
	
