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

## PyBase modules included
import pybase.log       as PyLog
import pybase.find      as PyFind

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
	PyLog.log("Exiting on CTRL+C")
	sys.exit(0)
signal.signal(signal.SIGINT, ctrl_c)

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
	config_lib = {
		"cli" : FishConfig.Config(FishConfig.Config.Sources.CLI, {"log_level" : int}),
		"env" : FishConfig.Config(FishConfig.Config.Sources.ENV)
	}

	config     = FishConfig.PriorityConfig(*[(config_lib["cli"], 1), (config_lib["env"], 2)])

	PyLog.setLogLevel(config.get("log_level", 0))

	x        = 0
	commands = set()
	while x in config:
		commands |= set([config[x].lower()])
		x += 1
	
	[runStage(stage, config) for stage in fishmonger.Stages if fishmonger.StageSynonyms[stage] & commands != set()]

def runStage(stage, config):
	PyLog.log(stage.title() + "...")
	PyLog.increaseIndent()
	configureStage(stage, config)
	PyLog.decreaseIndent()












main()