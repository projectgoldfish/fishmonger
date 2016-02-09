## Python Imports
import os
import pickle
import multiprocessing

import fishmonger.path as FishPath

Manager   = multiprocessing.Manager()
Cache     = {}
CacheLock = multiprocessing.Lock()
CacheFile = FishPath.Path(".fishmonger.pickle")

def init():
	with CacheLock:
		if CacheFile.isfile():
			h_file = CacheFile.open("r")
			Cache  = pickle.loads(h_file.read())
			h_file.close()
		else:
			Cache = {}

def save():
	with CacheLock:
		h_file = CacheFile.open("w")
		h_file.write(pickle.dumps(Cache))
		h_file.close()

def store(key, value):
	with CacheLock:
		Cache[key] = value

def update(key, action):
	with CacheLock:
		if key in Cache:
			Cache[key] = action(Cache[key])
		else:
			Cache[key] = action()

def fetch(key, default=(None, None)):
	with CacheLock:
		if key in Cache:
			return Cache[key]
		elif default is not (None, None):
			return default
		else:
			raise KeyError
