from   pybase.config import Config as PyConfig
import pybase.config
import os.path

def compiler(path):
	print "===> js"
	includes = " "
	for include in PyConfig["INCLUDE_DIRS"]:
		if include == "":
			continue
		includes += "-I " + include + " "

	return 0
