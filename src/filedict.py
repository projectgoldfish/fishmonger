## Python3.4
import os
import pickle

class FileDict():
	def __init__(self):
		self.data = {}
		self.loadFileStats()

		print "\t1",self,self.data.keys()

	def loadFileStats(self):
		if os.path.isfile(".fishmonger.pickle"):
			f = open(".fishmonger.pickle", "r")
			self.data = pickle.load(f)
			f.close()
		#print "\t2",self,self.data.keys()

	def saveFileStats(self, stats):
		
		#print "\tS0",self,len(self.data.keys())
		for stat in stats:
			self.data[stat] = stats[stat]

		#print "\tS1",len(stats.keys())
		#print "\tS2",self,len(self.data.keys())

		f = open(".fishmonger.pickle", "w")
		pickle.dump(self.data, f)
		f.close()
		#print "\tS3",self,len(self.data.keys())
		self.loadFileStats()
		#print "\tS4",self,len(self.data.keys())

	def updatedFiles(self, files):
		updated_files = []

		#print "\tU1",self,len(self.data.keys())
		
		#print "Updates"
		for f in files:
			if f not in self.data:
				updated_files.append(f)
			elif files[f].st_mtime > self.data[f].st_mtime:
				updated_files.append(f)

		#print "\tU2",self,len(self.data.keys())

		return updated_files

FileStats = FileDict()