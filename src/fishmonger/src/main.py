## Python modules included
import os
import sys
import signal

import functools
import itertools

## Fishmonger modules included
import fishmonger
import fishmonger.config     as FishConfig
import fishmonger.exceptions as FishExc
import fishmonger.toolchains as FishTC
import fishmonger.parallel   as FishParallel

## PyBase modules included
import pybase.log       as PyLog

if sys.version_info < (2, 7):
	"""
	Assure that python is at least 2.7

	This is required for list and dict comprehension support.
	"""
	raise "Requires python 2.7+"

def ctrl_c(signal, frame):
	"""
	Catch CTRL+C and exit cleanly
	"""
	print ""
	PyLog.log("Exiting on CTRL+C")

	FishParallel.shutdown.set()

	FishParallel.wait()

	sys.exit(0)
signal.signal(signal.SIGINT, ctrl_c)

def toBool(value):
	if value == None or value == 0:
		return False
	elif isinstance(value, str):
		return value.lower() in ["true", "t", "y", "yes"]
	else:
		return True

def main():
	"""
	Entry point of the application

	Reads CLI, ENV and base configuration.

	For each command given builds out the dependency tree and
	executes the commands determined necessary.

	1) Determine commands and build out command hierarchy
	2) For each command
		2a) Initialize necessary tool chain states
		2b) Determine order of execution for states
		2c) Run commands
	"""

	config_types = {
		"allow_invalid_tools" : toBool,
		"log_level"           : int,
		"skip_dep_update"     : toBool,
		"max_cores"           : int
	}

	config_lib   = FishConfig.ConfigLib(config_types)
	pconfig_lib  = FishConfig.PriorityConfigLib(config_types)
	config_lib["gen"]           = {}
	config_lib["cli"]           = FishConfig.Config.Sources.CLI
	config_lib["env"]           = FishConfig.Config.Sources.ENV
	config_lib["./.fishmonger"] = ".fishmonger" if os.path.isfile(".fishmonger") else {}
	
	pconfig_lib["system"]       = [config_lib["cli"], config_lib["env"], config_lib["./.fishmonger"], config_lib["gen"]]

	config       = pconfig_lib["system"]

	PyLog.setLogLevel(config.get("log_level", 0))

	fishmonger.toolchains.init()
	extra_tools  = [
		(FishTC.ToolType.EXCLUSIVE, config.get("exclusive_tool", [], single_as_list=True)),
		(FishTC.ToolType.INCLUSIVE, config.get("inclusive_tool", [], single_as_list=True))
	]
	[FishTC.enable(tool_name, tool_type, ignore_error_on_error=config.get("allow_invalid_tools", True)) for (tool_type, tool_names) in extra_tools for tool_name in tool_names]

	x        = 0
	commands = set()
	while x in config:
		commands |= set([config[x].lower()])
		x += 1
	#try:
	PyLog.log("Configuring...")
	(pconfig_lib, config_lib) = fishmonger.configure(pconfig_lib, config_lib)

	run_stage_fun = functools.partial(fishmonger.runStage, pconfig_lib, config_lib)
	map(run_stage_fun, [stage for stage in fishmonger.Stages if fishmonger.StageSynonyms[stage] & commands != set()])
	#except Exception as e:
	#	print e
main()