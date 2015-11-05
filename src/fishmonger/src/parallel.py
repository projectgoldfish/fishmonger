## Python modules included
import sys

import multiprocessing

## Fishmonger modules included
import fishmonger.config     as FishConfig
import fishmonger.exceptions as FishExceptions

class ParallelTask(multiprocessing.Process):
	def __init__(self, data, reduce_queue):
		multiprocessing.Process.__init__(self)

		self.data         = data
		self.reduce_queue = reduce_queue

	def run(self):
		res   = None
		error = True
		try:
			res   = self.action(self.app)
			error = False
		except FishExceptions.FishmongerException as e:
			PyLog.increaseIndent()
			PyLog.error(e)
			PyLog.decreaseIndent()
		except Exception as e:
			et, ei, tb = sys.exc_info()
			PyLog.error("Exception during %s%s" % (self.action, self.key), exception=str(e))
			PyLog.increaseIndent()
			for line in traceback.format_tb(tb):
				for t_line in line.strip().split("\n"):
					PyLog.error(t_line)
			PyLog.decreaseIndent()
		self.clean_queue.put((error, res))

	def action(self, object):
		raise(FishExceptions.FishmongerParallelTaskException("ParallelTask action not defined"))

def process(task, objects, reducer=None, max_cores=1):
	manager          = multiprocessing.Manager()
	result_queue     = manager.Queue()

	used_cores       = 0

	tasks            = {}

	commands         = self.command_list
	dependencies     = self.command_dependencies

	command          = None

	result           = True

	clean_key        = None
	dependency_block = False
	while True:
		## We continue to process as long as we haven't failed
		## And as long as we have a command left to spawn
		if result != True:
			PyLog.debug("Result false", log_level=6)
			break
		elif len(commands) == 0 and command == None:
			PyLog.debug("Comamnd Stats", commands=commands, command=command, log_level=6)
			break
					
		## If we have no command extract one
		if command == None:
			dependency_block = False

			## Get the first command that has no dependencies outstanding
			for x in range(len(commands)):
				t_key = commands[x][0]
				if len(dependencies[t_key]) == 0:
					command = commands.pop(x)
					break

			PyLog.debug("Fetched Command", command=command, log_level=6)
			if command == None:
				dependency_block = True
			
		## If we have a command AND we have available cores build/dispatch the task
		if used_cores < max_cores and command != None:
			PyLog.debug("Have cores", used_cores=used_cores, max_cores=max_cores, log_level=9)
			
			(key, action, app)  = command
			PyLog.debug("Running Task", task=key, log_level=9)
			t_task              = BuildTask(key, action, app, clean_queue)
			tasks[key]          = t_task
			
			PyLog.debug("Starting task", log_level=9)
			t_task.start()

			used_cores         += 1
			command             = None

			continue
		else:
			PyLog.debug("Waiting on cores or command dependencies", used_cores=used_cores, max_cores=max_cores, command=command, log_level=6)

		## If we ever get to the point where we could not get a command AND no tasks are running
		##   There must be some error in the build dependencies
		##   Halt the system in error as we'll never take another action
		if used_cores == 0 and command == None and len(commands) != 0:
			PyLog.error("No commands can be built and no tasks are pending. Halting.", commands=commands, dependencies=dependencies)
			sys.exit(1)

		## If we have no cores OR
		## If we have remaining commands OR
		## If we are dependency blocked
		if used_cores == max_cores or len(commands) == 0 or dependency_block == True:		
			PyLog.debug("Waiting for a task to finish", cores=used_cores==max_cores, commands=len(commands), dependency_block=dependency_block, log_level=6)
			(clean_key, result) = clean_queue.get()

			PyLog.debug("Cleaning", clean_key=clean_key, result=result, log_level=6)
			tasks[clean_key].join()
			tasks[clean_key]  = None
			used_cores       -= 1

			for d in dependencies:
				dependencies[d] -= set([clean_key])

	for t in tasks:
		if tasks[t] is not None:
			PyLog.debug("Joining", task=t, log_level=6)
			if result != True:
				tasks[t].terminate()
			tasks[t].join()
			tasks[t] = None

	if not result:
		PyLog.error("Command returned unsuccessful result. Halting.", task=clean_key, result=result)
			sys.exit(1)