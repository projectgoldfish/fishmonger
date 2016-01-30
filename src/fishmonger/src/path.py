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
	def __init__(self, *path, **kwargs):
		if   len(path) == 1:
			path = path[0]
		elif len(path) > 1:
			path = OSP.join(*[str(x) for x in path])
		else:
			raise PathException("Path must be supplied")

		path = path if not isinstance(path, Path) else path._path
		self._path = OSP.abspath(path)

	def __get__(self, index):
		return self._path[index]

	def __getitem__(self, index):
		return self.__get__(index)

	def __hash__(self):
		return hash(self._path)

	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return self._path

	def __cmp__(self, other):
		return self.__eq__(other)
	def __eq__(self, other):
		if   isinstance(other, Path):
			return self._path == other._path
		elif isinstance(other, str):
			return self._path == other
		return False

	def relative(self, root="."):
		return Path(OSP.relpath(self._path, root))

	def absolute(self):
		return Path(self._path)

	def isfile(self):
		return OSP.isfile(self._path)

	def isdir(self):
		return OSP.isdir(self._path)

	def basename(self):
		return Path(OSP.basename(self._path))

	def dirname(self):
		return Path(OSP.dirname(self._path))

	def join(self, *others):
		return Path(OSP.join(self._path, *[str(x) for x in others]))

	def mkdir(self):
		self._action(self._mkdirDir, self._mkdirFile, self._mkdirNone)
	def _mkdirDir(self):
		return
	def _mkdirFile(self):
		raise PathException("File exists, cannot create directory", filename=self._path)
	def _mkdirNone(self):
		OS.makedirs(self._path)

	def open(self, permissions):
		return self._action(self._openDir, self._openFile, self._openNone, permissions)
	def _openDir(self, *args):
		raise PathException("Cannot open directory")
	def _openFile(self, permissions):
		return open(self._path, permissions)
	def _openNone(self, permissions):
		if "w" in permissions or "a" in permissions:
			return open(self._path, permissions)
		else:
			raise PathException("No file to open", filename=self._path)

	def copy(self, target):
		self._action(self._copyDir, self._copyFile, self._copyNone, Path(target))
	def _copyDir(self, target):
		target = str(target)

		for (root, t_dirs, t_files) in OS.walk(self._path):
			if target == OSP.commonprefix([root, target]):
				#print root, target
				continue

			for t_dir in t_dirs:
				s_path = Path(root, t_dir)
				if s_path == target:
					continue
				t_path = Path(target, OSP.relpath(str(s_path), str(self)))
				print "Make", t_path
				t_path.mkdir()

			for t_file in t_files:
				s_path = Path(root, t_file)
				t_path = Path(target, OSP.relpath(str(s_path), str(self)))
				#print s_path, "->", t_path
				s_path.copy(t_path)
	def _copyFile(self, target):
		target.dirname().mkdir()
		target = str(target)
		shutil.copy(self._path, target)
	def _copyNone(self, target):
		raise PathException("Cannot copy from nonexistant source", source=self._path)

	def mv(self, target):
		self._action(self._mv, self._mv, self._mvNone, Path(target))
	def _mv(self, target):
		shutil.move(self._path, target)
	def _mvNone(self, target):
		raise PathException("Cannot mv nonexistant source", source=self._path)

	def rm(self):
		self._action(self._rmDir, self.rmFile, self.rmNone)
	def _rmDir(self):
		shutil.rmtree(self._path)
	def _rmFile(self):
		shutil.rm2(self._path, target)
	def _rmNone(self):
		raise PathException("Cannot rm nonexistant source", source=self._path)

	def ls(self, pattern="*"):
		return self._action(self._lsDir, self._lsFile, self._lsNone, pattern=pattern)
	def _lsDir(self, pattern):
		return [Path(x) for x in OS.listdir(self._path) if FNMatch.fnmatch(x, pattern)]
	def _lsFile(self, pattern):
		return self._matchFiles([self._path], pattern)
	def _lsNone(self, pattern):
		return []

	def find(self, **kwargs):
		return self._action(self._findDir, self._findFile, self._findNone, **kwargs)
	def _findDir(self, pattern="*", dirs_only=False, files_only=False):
		found = []
		for root, t_dirs, t_files in OS.walk(self._path):
			if not files_only:
				found += [Path(OSP.join(root, t_d)) for t_d in t_dirs  if t_d[0] != "." and FNMatch.fnmatch(t_d, pattern)]
			if not dirs_only:
				found += [Path(OSP.join(root, t_f)) for t_f in t_files if t_f[0] != "." and FNMatch.fnmatch(t_f, pattern)]
		return found
	def _findFile(self, pattern="*", **kwargs):
		return self._matchFiles([self._path], pattern)
	def _findNone(self, **kwargs):
		return []

	def _action(self, dir_action, file_action, error_action, *args, **kwargs):
		if OSP.isdir(self._path):
			return dir_action(*args, **kwargs)
		elif OSP.isfile(self._path):
			return file_action(*args, **kwargs)
		else:
			return error_action(*args, **kwargs)

	def _matchFiles(self, files, pattern):
		return [Path(f) for f in files if FNMatch.fnmatch(str(f), pattern)]
