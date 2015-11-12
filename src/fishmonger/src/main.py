## Python modules included
import os
import sys
import signal

## Fishmonger modules included
##import fishmonger.config     as FishConfig
##import fishmonger.exceptions as FishExceptions

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



















