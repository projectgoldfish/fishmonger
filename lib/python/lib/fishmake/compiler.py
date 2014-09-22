from pybase.config import Config as PyConfig

import fishmake

import pybase.config

import os
import os.path

def compile():
	print "Compiling"
	res = 0

	for language in PyConfig["LANGUAGES"]:
		## Get per language configuration
		config = 


		print "==> Application ", os.path.basename(app_dir)

		src_dir = os.path.join(app_dir, "src")

		types = []
		for compiler in PyConfig["LANGUAGES"][app_dir]:
			res = compiler.compile(app_dir)
			if not res == 0:
				return res	

	print "Compilation done"

	return res