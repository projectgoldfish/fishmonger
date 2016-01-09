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
	config   = FishConfig.PriorityConfig()
	config.addConfig(FishConfig.Config.Sources.CLI, 1)
	config.addConfig(FishConfig.Config.Sources.ENV, 2)

	PyLog.setLogLevel()

	commands = {}
	x        = 0
	while x in config:
		commands[config[x].lower()] = True
		x += 1
	
	"""
	"""
	
	

	[runStage(stage, modules, config) for stage in fishmonger.Stages if stage in fishmonger.StageSynonyms[stage]]

def runStage(stage, modules, config):
	pass












main()