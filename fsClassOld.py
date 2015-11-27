#from Image_Manipulation import lsbsteg
#from Web_Connection import *
import requests

class fileSystem(object):
	def __init__(self, fsString = None):
		self.currentDir = None
		self.fsString = fsString
		self.root = None
		self.history = None

	def readFS(self):
		rootCont = self.fsString.split('\n')
		tempDict = {}
		for rootNode in rootCont:
			foldOrCont = rootNode.split()
			foldName = foldOrCont[0]
			foldCont = {}
			fileNameCont = []
			for node in foldOrCont[1:]:
				fileInfo = node.split(',')
				fileName = fileInfo[0]
				fileDown = fileInfo[1]
				fileDel = fileInfo[2]
				foldCont[fileName] = (fsFile(fileName,fileDown,fileDel))
#				fileNameCont.append(fileName)
			foldLevel = foldName.count('/') -1
			if foldLevel>0:
				foldParent = tempDict[foldName.rsplit('/',2)[0] + '/']
			else:
				foldParent = None
			foldNameShort = foldName.rsplit('/')[-2]
			tempDict[foldName] = fsFolder(foldNameShort, foldCont, foldLevel, foldParent)
			tempDict[foldName].fileNames = fileNameCont
			if foldLevel > 0:
				tempDict[foldName].parent.contents[foldNameShort] = (tempDict[foldName])
#				tempDict[foldName].foldNames.append(foldName)
		self.root = tempDict['root/']
		return self.root

	def loadFS(self):
		if self.fsString == None:
			print ("No input string! New filesystem created.")
			return self.newFS()
		self.currentDir = self.readFS()
		return 'File system loaded, currently in root/'

	def newFS(self):
		self.currentDir = fsFolder('root', {}, 0, '')
		self.root = self.currentDir
		return 'New file system created'

	def ls(self, path = None):
		#outString = "The folder '" + self.currentDir.name + "' contains:\n"
		#for node in self.currentDir.contents.keys():
			#if type(node) is fsFolder:
				#TODO color outputs
		#	if isinstance(self.currentDir.contents[node], fsFile):
		#		name = self.currentDir.contents[node].name.rsplit('/')[-1]
		#	else:
		#		name = self.currentDir.contents[node].name.rsplit('/')[-2]
		#	length = len(name)
		#	outString+= name + (16-length)*" "
		#return outString
		outList = []
		if path != None:
			curDir = self.currentDir
			self.cd(path)
			print(curDir.name)
			outList = self.currentDir.contents.keys()
			self.currentDir = curDir
		else:
			outList = self.currentDir.contents.keys()
		return list(outList)

	def cdRoot(self):
		self.currentDir = self.root

	def cd(self, destDir, fullyQual = False):
		dirPath = destDir.split('/')
		if fullyQual:
			self.cdRoot()
		curDir = self.currentDir
		for fol in dirPath:
			if fol in curDir.contents.keys():
				if isinstance(curDir.contents[fol],fsFolder):
					curDir = curDir.contents[fol]
				else:
					return '{} is not a folder in {}'.format(fol, curDir.name)
			else:
				return '{} is not a folder in {}'.format(fol, curDir.name)
		self.currentDir = curDir
		return 'Current folder is {}'.format(self.currentDir.name)


	def rm(self, fName):
		fileName = self.currentDir.name + fName
		if fileName not in self.currentDir.contents.keys():
			return 'File not in current directory'
		elif isinstance(self.currentDir.contents[fileName], fsFolder):
			return 'Use "rmdir" command to remove directories'
		else:
			"""try:
				delStat = deleteFile(self.currentDir.contents[fileName].deleteUrl)
				print('deleted from sendSpace')
			except:
				print('not deleted from sendSpace')"""
			del self.currentDir.contents[fileName]
			return 'File deleted'

	def addFile(self, fName, downLink, delLink):
		fileName = self.currentDir.name + fName
		if fileName in self.currentDir.contents.keys():
			fName = fName[:-4] + "COVERT" + fName[-4:]
			print('File already in current directory. New name is {}'.format(fName))
		self.currentDir.contents[fName] = fsFile(fName, downLink, delLink)
		return 'File added'

	def mkdir(self, dirName):
		dirObj = fsFolder(dirName, {}, self.currentDir.level+1, self.currentDir)
		self.currentDir.contents[dirName] = dirObj

	def writeFolder(self,parentPath):
		print(self.currentDir)
		outString = self.currentDir.name + '/'
		currentDict = self.currentDir.contents
		nextString = '\n' + parentPath + '/'
		for node in currentDict.keys():
			item = currentDict[node]
			if  node == '..' or node == '.':
				continue
			elif isinstance(item, fsFile):
				outString += ' ' + item.name + ',' + item.downLink + ',' + item.delLink 
			else:
				self.cd(item.name)
				nextString += self.writeFolder(parentPath + '/' + item.name) 
				self.cd('..')
		if len(nextString) > 2 + len(parentPath):
			outString += nextString
		return outString

	def writeFS(self):
		self.cdRoot()
		return self.writeFolder("root")


def uploadFile(localPath):
	pass

def deleteFile(deleteUrl): #deprecated, no longer deleting files from sendspace (as it is pointless)
	payload = {'delete':'Delete+File'}
	proxies = {'https':'https://165.139.149.169:3128'}
	r = requests.post(deleteUrl, data=payload, proxies = proxies)
	if r.status_code == 200:
		return "File Deleted"
	else:
		return "Error deleting file"

class fsFolder(object):
	def __init__(self, name, contents, level, parent):
		self.name = name
		self.contents = contents
		self.contents['.'] = self
		self.contents['..'] = parent
		self.level = level
		self.parent = parent

class fsFile(object):
	def __init__(self, name, downLink, delLink):
		self.name = name
		self.downLink = downLink
		self.delLink = delLink

if __name__ == "__main__":
	fs = fileSystem("root/ alpha.txt,a.url,aDel.url bravo.txt,b.url,bDel.url\nroot/folderA/ a.txt,asdf.ase,asgr.yhu\nroot/folderA/folderB/\nroot/folderA/folderB/folderC/")
	#fs.decode(fs.fsString)
	print(fs.loadFS())
	print(fs.ls())
	print(repr(fs.writeFS()))

