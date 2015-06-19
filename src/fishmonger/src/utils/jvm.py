import socket

import os.path

import pybase.set  as PySet
import pybase.find as PyFind

import fishmonger.dirflags as DF

ClassPath   = {}
PackageRoot = None

def initPackageRoot():
	global PackageRoot
	host = socket.getfqdn()
	host = host.split(".")
	host.reverse()

	package_root = host[0]
	for token in host[1:]:
		package_root = package_root + "/" + token
	PackageRoot = package_root

def getAppClassPath(app, path_type):
	paths = PySet.Set()
	
	## Add the src and lib dirs
	paths.append(app.path(path_type|DF.src))
	paths.append(app.path(path_type|DF.lib))
	for child in app.children:
		paths.append(child.path(path_type|DF.src))
		paths.append(child.path(path_type|DF.lib))
	return paths

def getSourceClassPath(apps, lang="java", extension="jar"):
	global ClassPath

	if lang not in ClassPath:
		ClassPath[lang] = {}

	path_type = DF.source
	if path_type in ClassPath[lang]:
		return ClassPath[lang][path_type]

	paths = PySet.Set()
	for lib_dir in apps[0]["LIB_DIRS"]:
		jars = PyFind.findAllByExtension(extension, lib_dir, root_only=True)
		paths.append(jars)

	for app in apps:
		paths.append(getAppClassPath(app, path_type))

	cp = apps[0].path(path_type|DF.langlib, lang=lang)
	for path in paths:
		if os.path.isdir(path) or os.path.isfile(path):
			cp = cp + ":" + path

	ClassPath[lang][path_type] = cp
	return ClassPath[lang][path_type]

def getSourceFiles(apps, lang="java"):
	files = PySet.Set()
	for app in apps:
		files.append(PyFind.findAllByExtensions([lang], app.path(DF.source|DF.src), root_only=True))
		for child in app.children:
			files.append(PyFind.findAllByExtensions([lang], child.path(DF.source|DF.src), root_only=True))
	return files
