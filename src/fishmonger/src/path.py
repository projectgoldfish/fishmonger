## Python Imports
import os      as OS
import os.path as OSP

import fnmatch as FNMatch

## RlesZilm Imports
import pybase.exception as PyExcept

class PathException(PyExcept.BaseException):
	pass

class Path():
	def __init__(self, path):
		self.path = path

	def __str__(self):
		return self.path

	def absolute(self):
		path = None
		if self.path[0] == "~":
			path = OSP.expanduser(self.path)
		else:
			path = OSP.join(OS.getcwd(), self.path)

		ptokens = []
		tokens  = path.split("/")
		for token in tokens:
			if   token == ".":
				continue
			elif token == "..":
				ptokens = ptokens[:-1]
			else:
				ptokens.append(token)
		return Path("/".join(ptokens))

	def relative(self, root="."):
		root     = str(Path(root).absolute()).split("/")
		target   = str(Path(self.path).absolute()).split("/")

		rootiter = root
		for token in rootiter:
			if token == target[0]:
				root   = root[1:]
				target = target[1:]
		ptokens = ([".."] * len(root)) + target
		if ptokens[0] != "..":
			ptokens = ["."] + ptokens
		return Path("/".join(ptokens))

	def isFile(self):
		return OSP.isfile(self.path)

	def isDir(self):
		return OSP.isdir(self.path)

	def mkdir(self):
		self._action(self._mkdirDir, self._mkdirFile, self._mkdirNone)

	def _mkdirDir(self):
		return

	def _mkdirFile(self):
		raise PathException("File exists, cannot create directory", filename=self.path)

	def _mkdirNone():
		OS.makedirs(self.path)

	def open(self, permissions):
		return self._action(self._openDir, self._openFile, self._openNone, permissions)

	def _openDir(self, *args):
		raise PathException("Cannot open directory")

	def _openFile(self, permissions):
		return open(self.path, permissions)

	def _openNone(self, permissions):
		if "w" in permissions or "a" in permissions:
			return open(self.path, permissions)
		else:
			raise PathException("No file to open", filename=self.path)

	def copy(self, target):
		self._action(self._copyDir, self.copyFile, self.copyNone, target)

	def _copyDir(self, target):

	def _copyFile(self, target):

	def _copyNone(self, target):
		if OSP.isfile(self.path):
		elif OSP.isdir(self.path):
		else:
			raise PathException("Cannot copy from nonexistant source", source=self.path)

	def ls(self, pattern="*"):
		if OSP.isfile(self.path):
			return [Path(self.path)]
		else OSP.isdir()

	def find(self, pattern="*"):

	def touch(self):

	def _action(self, dir_action, file_action, error_action, *args, **kwargs):
		if OSP.isdir(self.path):
			return dir_action(*args, **kwargs)
		elif OSP.isfile(self.path):
			return file_action(*args, **kwargs)
		else:
			return error_action(*args, **kwargs)

	def _copyDir(self, target):

	def _copyFile(self, target):