from pybase.config import Config as PyConfig

import os
import os.path

def compile():
	print "Compiling"
	res = 0

	for app_dir in PyConfig["LANGUAGES"]:
		print "==> Application ", os.path.basename(app_dir)

		src_dir = os.path.join(app_dir, "src")

		types = []
		for compiler in PyConfig["LANGUAGES"][app_dir]:
			res = compiler.compile(app_dir)
			if not res == 0:
				return res	

	print "Compilation done"

	return res