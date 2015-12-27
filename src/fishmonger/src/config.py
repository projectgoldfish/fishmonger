## Python modules included
import importlib

## PyBase modules included
import pybase.log as PyLog

## Fishmonger modules included
import fishmonger.exceptions as FishExc

"""
Config

Four sources

CLI
ENV
.fishmonger file at project root
.fishmonger file at source  root

CLI overrides environment
ENV overrides file
SRC file overrides root
ROOT file overrides defaults
"""

class Config():
	def __init__(self):
		self.configs  = []
		self.values   = {}

	def __getitem__(self, key):
		if key in self.values:
			return self.values[key]
		else:
			for (t, config) in self.configs:
				if key in config:
					return config[key]

	def __setitem__(self, key, value):
		self.value[key] = value

	def get(self, key, default=(None, False)):
		try:
			return self.__getitem__(key)
		except Exception as e:
			if default == (None, False):
				raise(e)
			return default

	def set(self, key, value):
		self.__setitem__(key, value)

	def addConfig(self, config, priority=None):
		priority = priority if priority != None else len(self.configs)
		self.configs.append((priority, config))
		self.configs.sort()
