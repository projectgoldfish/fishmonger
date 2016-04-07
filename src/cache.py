## Python Imports
import os
import queue
import pickle
import signal
import multiprocessing

import fishmonger.path     as FishPath
import fishmonger.parallel as FishParallel

_ShutDown = multiprocessing.Event()

class CacheReducer(multiprocessing.Process):
	"""
	Wrapper class for multiprocessing.Process that defines the behavior of a task as
	expected by the paralel mondule.

	The user must not implement __init__ or run.
	The user must implement action.
	"""

	def __init__(self, reduce_queue):
		multiprocessing.Process.__init__(self)

		self.cache_file = FishPath.Path(".fishmonger.pickle")
		if self.cache_file.isfile():
			with self.cache_file.open("rb") as f:
				self.data = pickle.load(f)
		else:
			self.data = {}
		self.reduce_queue = reduce_queue

	def run(self):
		signal.signal(signal.SIGINT, signal.SIG_IGN)
	
		while not (_ShutDown.is_set() and self.reduce_queue.empty()):
			try:
				task   = self.reduce_queue.get(timeout=.05)
				action = getattr(self, task[0])
				action(*task[1:])
			except queue.Empty:
				pass

		self.save()

	def save(self):
		with self.cache_file.open("wb") as f:
			pickle.dump(self.data, f)

	def store(self, key, value):
		self.data[key] = value

	def update(self, key, action):
		self.data[key] = action(self.data[key])

_ReduceQueue  = multiprocessing.Queue()
_CacheReducer = CacheReducer(_ReduceQueue)
_CacheFile    = FishPath.Path(".fishmonger.pickle")

_Cache        = {}
if _CacheFile.isfile():
	with _CacheFile.open("rb") as f:
		_Cache = pickle.load(f)

def init():
	_CacheReducer.start()

def shutdown():
	_ShutDown.set()
	if _CacheReducer.is_alive():
		_CacheReducer.join()

def save():
	_ReduceQueue.put(("save"))

def store(key, value):
	_ReduceQueue.put(("store", key, value))
	
def update(key, action):
	_ReduceQueue.put(("update", key, action))

def fetch(key, default=(None, None)):
	if key in _Cache:
		return _Cache[key]
	elif default is not (None, None):
		return default
	else:
		raise KeyError
