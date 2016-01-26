## Python Imports
import os
import pickle
import multiprocessing

Cache = {}

def init():
	if os.path.isfile("./fishmonger.pickle"):
		pass