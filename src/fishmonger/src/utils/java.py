import socket

import os.path

import pybase.set  as PySet
import pybase.find as PyFind

def getPackageDir(app, dir):
	root = ""

	if app["JAVA_PACKAGE_ROOT"]:
		root =  app["JAVA_PACKAGE_ROOT"]
	else:
		host = socket.gethostname()
		host = host.split(".")

		package_root = host[0]
		for token in host[1:]:
			package_root = package_root + "." + token
		root = package_root
	return os.path.join(root, dir)

def getClassPath(apps):
	class_path = PySet.Set()
	for app in apps:
		for file in PyFind.findAllByExtension("java", app.srcDir()):
			class_path.append(os.path.dirname(file))
		for dir in PyFind.findAllByExtension("java", app.srcDir()):
			class_path.append(os.path.dirname(file))
	print class_path
