from pybase.config import GlobalConfig as PyConfig

import fishmake

import pybase.config

import os
import os.path

def getBuildOrder(config):
	tconfig = []
	return config

def compile():
	print "Compiling"
	res = 0

	config = {}

	## For every available language
	for language in PyConfig["LANGUAGES"]:

		## Get per app configuration

		for app in PyConfig["APP_DIRS"]:
			print "==> Application", os.path.basename(app)
			tconfig = PyConfig.clone()
			tconfig.merge(pybase.config.parseFile(os.path.join(app, language.configFile())))
			config[app] = tconfig
		## Resolve build order dependencies
		print config
		config = getBuildOrder(config)

		## Build the app
		for (app, app_dir, app_config) in config:
			res = language.compile(app, app_dir, app_config)
			if res != 0:
				return 1
				
	print "Compilation done"

	return res