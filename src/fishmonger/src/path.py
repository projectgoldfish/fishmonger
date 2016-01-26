## Python Imports
import os      as OS
import os.path as OSP

import fnmatch as FNMatch

import shutil

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
	def _mkdirNone(self):
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
		(root, t_dirs, t_files) = os.walk(self.path).next()
		found += [OSP.join(root, t_d) for t_d in t_dirs  if FNMatch.fnmatch(OSP.join(root, t_d), pattern)]
		found += [OSP.join(root, t_f) for t_f in t_files if FNMatch.fnmatch(OSP.join(root, t_f), pattern)]
	def _copyFile(self, target):
		dirname = OSP.dirname(target)
		if   OSP.isfile(target):
		elif OSP.isfile()
		elif OSP.isdir(target):
		elif OSP.isdir():
	def _copyNone(self, target):
		raise PathException("Cannot copy from nonexistant source", source=self.path)

	def ls(self, pattern="*"):
		self._action(self._lsDir, self._lsFile, self.lsNone, pattern=pattern)
	def _lsDir(self, pattern):
		found = []
		(root, t_dirs, t_files) = os.walk(self.path).next()
		found += [OSP.join(root, t_d) for t_d in t_dirs  if FNMatch.fnmatch(OSP.join(root, t_d), pattern)]
		found += [OSP.join(root, t_f) for t_f in t_files if FNMatch.fnmatch(OSP.join(root, t_f), pattern)]
		return found
	def _lsFile(self, pattern):
		return self._matchFiles([self.path], pattern)
	def _lsNone(self, pattern):
		return []

	def find(self, pattern="*"):
		return self._action(self._findDir, self._findFile, self._findNone, pattern=pattern)
	def _findDir(self, pattern):
		found = []
		for root, t_dirs, t_files in os.walk(self.path):
			found += [OSP.join(root, t_d) for t_d in t_dirs  if FNMatch.fnmatch(OSP.join(root, t_d), pattern)]
			found += [OSP.join(root, t_f) for t_f in t_files if FNMatch.fnmatch(OSP.join(root, t_f), pattern)]
		return found
	def _findFile(self, pattern):
		return self._matchFiles([self.path], pattern)
	def _findNone(self, pattern):
		return []

	def _action(self, dir_action, file_action, error_action, *args, **kwargs):
		if OSP.isdir(self.path):
			return dir_action(*args, **kwargs)
		elif OSP.isfile(self.path):
			return file_action(*args, **kwargs)
		else:
			return error_action(*args, **kwargs)

	def _matchFiles(self, files, pattern):
		return [f for f in files if FNMatch.fnmatch(f, pattern)]

	







