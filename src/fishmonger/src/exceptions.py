## PyBase modules included
import pybase.exception as PyExcept

class FishmongerException(PyExcept.BaseException):
	pass

class FishmongerConfigException(PyExcept.BaseException):
	pass

class FishmongerToolchainException(PyExcept.BaseException):
	pass

class FishmongerParallelTaskException(PyExcept.BaseException):
	pass