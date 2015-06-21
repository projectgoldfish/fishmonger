import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.find as PyFind
import pyrcs       as PyRCS
import pybase.file as PyFile
import pybase.sh   as PySH
import pybase.set  as PySet
import pybase.log  as PyLog

import os.path
import shutil

import fishmonger
import fishmonger.dirflags  as DF
import fishmonger.utils.erl as FishErl

class ToolChain(fishmonger.ToolChain):	
	def genConfigFile(self, app):
		doc         = PyErl.PyErlDocument()
		expressions = PyErl.PyErlList()
		config_file = app.path(DF.install|DF.etc, file_name=app.name()+".erl_config.default")
		apps        = FishErl.getRequiredApps(app.name(), app.path(DF.install|DF.langlib, lang="erlang"))

		config      = {os.path.basename(d) : d for d in PyFind.findAllByPattern("*.erl_config", "./src") + PyFind.findAllByPattern("*.erl_config", "./deps")}
		for t_app in apps:
			app_file   = t_app + ".erl_config"
			if app_file in config:
				terms = PyErl.parse_file(config[app_file])
				expressions.appendChild(terms)

		doc.appendChild(expressions)

		PyErl.write_file(config_file, doc)

	def __init__(self):
		self.extensions = ["erl"]
		self.defaults   = {
			"BUILD_AFTER_TOOLS" : ["erl_app"],
			"TOOL_OPTIONS"      : {
				"ERL_MAIN"      : "",
				"EXECUTABLE"    : False
			}
		}

	def installApp(self, child, app):
		main_steps = [self.genConfigFile]
		if app.name() == app["TOOL_OPTIONS"]["ERL_MAIN"] or ("EXECUTABLE" in app["APP_OPTIONS"] and app["APP_OPTIONS"]["EXECUTABLE"] == True):
			self.genConfigFile(app)

