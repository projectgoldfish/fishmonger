## Python modules included
import sys
import os.path

## PyBase modules included
import pybase.log as PyLog

## Fishmonger modules included
#import fishmonger.exceptions as FishExc
import exceptions as FishExc

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

def proplistToDictReducer(acc, item):
	(k, v) = item
	k      = k.lower() if isinstance(k, str) else k
	if k not in acc:
		acc[k] = v
	elif isinstance(acc[k], list):
		acc[k].append(v)
	else:
		acc[k] = [acc[k], v]
	return acc

class Config():
	class Sources:
		CLI, ENV = range(0, 2)

	class CLIParser():
		def __init__(self):
			pass

		def parse(self):
			x = 1
			y = 0
			args = {}
			while x < len(sys.argv):
				(x, y, arg) = self.parseCLIArg(x, y)
				args.append(arg)
			return reduce(proplistToDictReducer, args, {})

		def parseCLIArg(self, x, y):
			if sys.argv[x][:2] == "--":
				(x, arg) = self.parseCLIArgValue(x, sys.argv[x][2:])
				return (x, y, arg)
			elif sys.argv[x][:1] == "-":
				(x, arg) = self.parseCLIArgValue(x, sys.argv[x][1:])
				return (x, y, arg)
			else:
				return (x+1, y+1, (y, sys.argv[x]))

		def parseCLIArgValue(self, x, name):
			if "=" in name:
				tokens = name.split("=")
				return (x+1, (tokens[0], tokens[1]))
			elif (x+1) < len(sys.argv) and sys.argv[x+1][:1] != "-":
				return (x+2, (name, sys.argv[x+1]))
			else:
				return (x+1, (name, True))

	class ENVParser():
		def __init__(self):
			pass
		def parse(self):
			return os.environ
	
	class FileParser():
		def __init__(self):
			pass
		def parse(self, file_name):
			terms = eval(open(file_name).read())
			if isinstance(terms, list):
				return reduce(proplistToDictReducer, terms, {})
			elif isinstance(terms, dict):
				return terms
			else:
				raise FishExc.FishmongerConfigException("File config is invalid", terms=terms)

	def __init__(self, source, types={}):
		values      = {}
		self.values = {}
		self.types  = {self.configKey(k) : types[k] for k in types}
		if isinstance(source, str) and os.path.isfile(source):
			parser = FileParser()
			values = parser.parse(source)
		elif isinstance(source, dict):
			values = source
		elif isinstance(source, Config):
			values = source.values
		elif source == Config.Sources.CLI:
			parser = Config.CLIParser()
			values = parser.parse()
		elif source == Config.Sources.ENV:
			parser = Config.ENVParser()
			values = parser.parse()
		else:
			raise FishExc.FishmongerConfigException("Cannot instantiate Config from", source=source)
		
		for k in values:
			self.set(k, values[k])

	def __getitem__(self, key):
		return self.values[self.configKey(key)]

	def __setitem__(self, key, value):
		key   = self.configKey(key)
		value = self.configValue(key, value)
		self.values[key] = value

	def configKey(self, key):
		return key.lower() if isinstance(key, str) else key

	def configValue(self, key, value):
		return value if key not in self.types else self.types[key](value)

	def get(self, key, default=(None, False)):
		try:
			return self.__getitem__(key)
		except KeyError as e:
			if default == (None, False):
				raise(e)
			return default

	def set(self, key, value):
		self.__setitem__(key, value)

class PriorityConfig(Config):
	def __init__(self):
		Config.__init__(self)
		self.configs = []

	def addConfig(self, config, priority=None):
		priority = priority if priority != None else len(self.configs)
		self.configs.append((priority, config))
		self.configs.sort()
