"""
Module that provides a simplified manner for parallel processing

Grammar:
	task()            - An class type that extends ParallelTask()
	data()            - term() | (term(), [term()])
	term()            - Any value
	integer()         - Integer within the range given
"""

## Python modules included
import sys
import signal
import multiprocessing

## PyBase modules included
import pybase.log       as PyLog
import pybase.exception as PyException

shutdown  = multiprocessing.Event()
processes = {}

class ParallelException(PyException.BaseException):
	pass

class ParallelTaskException(PyException.BaseException):
	pass

class DependentObject():
	def __init__(self, data, dependencies):
		self.data         = data
		self.dependencies = dependencies

class ParallelTask(multiprocessing.Process):
	"""
	Wrapper class for multiprocessing.Process that defines the behavior of a task as
	expected by the paralel mondule.

	The user must not implement __init__ or run.
	The user must implement action.
	"""

	def __init__(self, action, data, reduce_queue):
		multiprocessing.Process.__init__(self)

		self.action       = action
		self.data         = data
		self.reduce_queue = reduce_queue

	def run(self):
		signal.signal(signal.SIGINT, signal.SIG_IGN)

		res   = None
		error = None
		try:
			res   = self.action(self.data)
		except PyException.BaseException as e:
			error = e
		except Exception as e:
			error = ParallelTaskException(str(e), trace=sys.exc_info())
		self.reduce_queue.put((self.data, error, res))

	def action(self, object):
		raise(ParallelTaskException("ParallelTask action not defined"))

def wait():
	for t in processes:
		if processes[t] != None and processes[t].is_alive():
			processes[t].terminate()
			processes[t].join()

def defaultReducer(obj, acc=None):
	acc = acc if acc is not None else []
	acc.append(obj)
	return acc

def processObjects(objects, action, reducer=None, max_cores=None, acc0=None):
	"""
	processObjects(task()::Task, [data()]::Data, fun(term()::New, term()::Accumulator) -> data()::Reducer, integer(>=1)::Cores) -> data() :: Result
	
	Task    - The task class to run in parallel
	
	Data    - List of objects that contains data elements to process in parallel. If an element is of the
	          form (term()::A, [term()]::B) it is understood that A is not to be run until all of B have completed.
	          Processing is attempted semi inorder. The next element to process is chosen by taking the first element
	          of data that has all dependencies met.
	 
	Reducer - Function that takes a processed value and an accumulator and returns a new accumulator. The first value to
	          be processed will be given the accumulator None. If a reducer is not provide None will be returned.
	
	Cores   - The maximum instances of Task to run in parallel. When a value is not provided the n-1 cores will be used where
	          n is the number of cores available to the system. If n is ever below 0 1 core will be used.

	Result  - The final value of the accumulator or None if no accumulator is provided
	"""
	acc0             = acc0      if acc0      is not None else []
	reducer          = reducer   if reducer   is not None else defaultReducer
	max_cores        = max_cores if max_cores is not None else multiprocessing.cpu_count()

	#manager          = multiprocessing.Manager()
	#result_queue     = manager.Queue()
	result_queue     = multiprocessing.Queue()

	used_cores       = 0
	error            = False

	## Loop until we explicitly break
	while True:
		if len(objects) == 0:
			"""
			If we have no objects we've dispatched everything. Exit the loop and wait. 
			"""
			break

		(obj, objects) = getObject(objects)
		if obj != None:
			"""
			If we were able to get an object dispatch it.
			"""
			processes[obj] =  ParallelTask(action, obj, result_queue)
			processes[obj].start()
			used_cores += 1

			if used_cores < max_cores:
				"""
				If we have more cores avilable resume the loop
				"""
				continue
		
		"""
		If we do not immediately continue then we are either using all cores or we have no
		processes that cannot be started until a dependency completes.

		Wait for a running task to complete, perform cleanup, then attempt to dispatch.
		"""
		(r_obj, error, res) = result_queue.get()
		if error != None:
			"""
			If the task resulted in error halt running processes and rasie the error.
			"""
			for t in processes:
				if processes[t] != None:
					processes[t].terminate()
					processes[t].join()
			raise(error)
		if reducer != None:
			acc0 = reducer(res, acc0)
			
		if processes[r_obj].is_alive():
			processes[r_obj].join()
		processes[r_obj]  = None
		used_cores       -= 1

	"""
	At this point all objects have been dispatched. Retrieve final calculations, run reduce, return
	"""
	while used_cores > 0:
		(r_obj, error, res) = result_queue.get(block=True, timeout=1000)

		if error != None:
			"""
			If the task resulted in error halt running processes and raise the error.
			"""
			for t in processes:
				if processes[t] != None and processes[t].is_alive():
					processes[t].terminate()
					processes[t].join()
			raise(error)
		if reducer != None:
			acc0 = reducer(res, acc0)

		processes[r_obj].join()
		processes[r_obj]  = None
		used_cores       -= 1
	return acc0


def getObject(objects):
	"""
	getObject([data()]::Data) -> (term()::Next, [data()]::Data2)

	Data      - List of objects that contains data elements to process in parallel. If an element is of the
	            form (term()::A, [term()]::B) it is understood that A is not to be run until all of B have completed.
	            Processing is attempted semi inorder. The next element to process is chosen by taking the first element
	            of data that has all dependencies met.

	Completed - Dict of objects that have been processed.

	Next      - The next item to be processed.

	Data2     - The list generated by removing Next from Data
	"""

	for x in range(len(objects)):
		obj = objects[x]
		if isinstance(obj, DependentObject):
			if len(obj.dependencies) == 0:
				objects.pop(x)
				return (obj.data, objects)
		else:
			objects.pop(x)
			return (obj, objects)
	return (None, objects)
