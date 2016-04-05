## Python3.4
import traceback
## PIP
## Fishmonger
import fishmonger.log as FishLog

class FishmongerException(Exception):
	def __init__(self, msg=None, *args, **kwargs):
		msg         = msg if msg is not None else ""

		error_type  = None
		error_value = None
		error_stack = None
		if "trace" in kwargs:
			(error_type, error_value, error_stack) = kwargs["trace"]
			error_stack = traceback.extract_tb(error_stack)
			del kwargs["trace"]
		else:
			error_type  = "<" + self.__class__.__name__ + ">"
			error_value = msg
			error_stack = traceback.extract_stack()

		self.trace = error_stack

		(file, line, function, ignore) = self.trace[-2 if len(self.trace) > 1 else 0]

		trace = ""
		for e in self.trace:
			trace += "\n\t" + repr(e)
		self.trace = trace

		file = file.split("/")
		if file[-1] == "__init__.py":
			file = "(%s:__init__.py)" % file[-2]
		else:
			file = file[-1]

		prefix          = "[%s:%s@%d] " % (file, function, line) + str(error_type) + " - Exception: "
		self.value      = FishLog.formatMsg(prefix + str(error_value), *args, **kwargs)
	
	def __str__(self):
		return self.value + "\nTrace:" + self.trace

class FishmongerPathException(FishmongerException):
	pass

class FishmongerConfigException(FishmongerException):
	pass

class FishmongerToolchainException(FishmongerException):
	pass

class FishmongerParallelTaskException(FishmongerException):
	pass