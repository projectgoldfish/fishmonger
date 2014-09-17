from   pybase.config import Config as PyConfig
import pybase.config
import os.path

def getFileTypes():
	return ["js"]

def compile(path):
	print "====> js"
	includes = " "
	for include in PyConfig["INCLUDE_DIRS"]:
		if include == "":
			continue
		includes += "-I " + include + " "

	return 0

def install(path):
	
	pass

def doc(path):
	pass