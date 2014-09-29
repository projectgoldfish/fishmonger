from   pybase.config import GlobalConfig as PyConfig
import pybase.config
import os.path

def configFile():
	return ".fishmake.cxx"

def getFileTypes():
	return ["c", "cpp"]

def compile(path):
	print "====> cxx"
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