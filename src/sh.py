## Python3.4
import os
import fnmatch
import subprocess
import shutil
## PIP
## Fishmonger
import fishmonger.log        as FishLog

################################
## Shell CMD Functions        ##
################################
def runCmd(command, prefix="", stderr=False, stdout=False, **kwargs):
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	proc.wait()

	if stdout:
		for line in proc.stdout:
			FishLog.log(prefix, line.rstrip())

	if stderr:
		for line in proc.stderr:
			FishLog.log(prefix, line.rstrip())

	return proc

## shell(string()) -> integer()
## Run a system command and return the result code.
def cmd(command, **kwargs):
	proc = runCmd(command, **kwargs)
	return proc.returncode

def cmdText(command, **kwargs):
	proc = runCmd(command, **kwargs)
	output = ""
	for line in proc.stdout:
		output += line
	return output.strip()