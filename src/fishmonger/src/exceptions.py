## PyBase modules included
import pybase.exception as PyExcept

class FishmongerException(PyExcept.BaseException):
	pass

class FishmongerPathException(FishmongerException):
	pass

class FishmongerConfigException(FishmongerException):
	pass

class FishmongerToolchainException(FishmongerException):
	pass

class FishmongerParallelTaskException(FishmongerException):
	pass