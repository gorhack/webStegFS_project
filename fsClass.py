#from Image_Manipulation import lsbsteg
#from Web_Connection import *
import requests

class fileSystem(object):
	def __init__(self, fsString):
		self.currentDir = None
		self.fsString = fsString
		self.root = None

	def decode(self):
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
			tempDict[foldName] = fsFolder(foldName, foldCont, foldLevel, foldParent)
			tempDict[foldName].fileNames = fileNameCont
			if foldLevel > 0:
				tempDict[foldName].parent.contents[foldName] = (tempDict[foldName])
#				tempDict[foldName].foldNames.append(foldName)
		self.root = tempDict['root/']
		return self.root

	def loadFS(self, url):
		if url == 'test':
			self.currentDir = self.decode()
			return 'works'
		steg = lsbsteg.Steg()
		try:
			steg.assignImage(url)
		except:
			print('Bad URL or computer offline')
			
		self.currentDir = decode(steg.decode())
		return 'File system loaded, currently in root/'

	def newFS(self):
		self.currentDir = fsFolder('root', [], 0, '')
		return 'New file system created'

	def ls(self):
		outString = "The folder '" + self.currentDir.name + "' contains:\n"
		for node in self.currentDir.contents.keys():
			#if type(node) is fsFolder:
				#TODO color outputs
			if isinstance(self.currentDir.contents[node], fsFile):
				name = self.currentDir.contents[node].name.rsplit('/')[-1]
			else:
				name = self.currentDir.contents[node].name.rsplit('/')[-2]
			length = len(name)
			outString+= name + (16-length)*" "
		return outString

	def cdRoot(self):
		self.currentDir = self.root

	def cd(self, destDir, fullyQual = False):
		destDirFull = self.currentDir.name + destDir + '/'
		if fullyQual:
			destDirFull = destDir
		if destDir == '..':
			if (self.currentDir.name == 'root/'):
				return 'Already in highest folder'
			else:
				self.currentDir = self.currentDir.parent
		elif ((destDirFull) in self.currentDir.contents.keys()):
			if isinstance(self.currentDir.contents[destDirFull], fsFolder) :
				self.currentDir = self.currentDir.contents[destDirFull]
			else:
				print("Input name is not a directory")
		else:
			print ("Desired directory is not in current directory")
		return self.currentDir.name

	def rm(self, fName):
		fileName = self.currentDir.name + fName
		if fileName not in self.currentDir.contents.keys():
			return 'File not in current directory'
		elif isinstance(self.currentDir.contents[fileName], fsFolder):
			return 'Use "rmdir" command to remove directories'
		else:
			out = ''
			try:
				delStat = deleteFile(self.currentDir.contents[fileName].deleteUrl)
				print('deleted from sendSpace')
			except:
				print('not deleted from sendSpace')
			del self.currentDir.contents[fileName]
			return 'File deleted'

	def addFile(self, localPath, fName):
		fileName = self.currentDir.name + fName
		if fileName in self.currentDir.contents.keys():
			return 'File already in current directory| pick another name'
		else:
			deleLink, uploadFile(localPath)

	def writeFolder(self):
		outString = self.currentDir.name
		currentDict = self.currentDir.contents
		nextString = '\n'
		for node in currentDict.values():
			if isinstance(node, fsFile):
				outString += ' ' + node.name + ',' + node.downLink + ',' + node.delLink 
			else:
				self.cd(node.name, True)
				nextString += self.writeFolder() 
				self.cd('..')
		if len(nextString) > 2:
			outString += nextString
		return outString

	def writeFS(self):
		self.cdRoot()
		return self.writeFolder()


def uploadFile(localPath):
	pass

def deleteFile(deleteUrl):
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
		self.level = level
		self.parent = parent

class fsFile(object):
	def __init__(self, name, downLink, delLink):
		self.name = name
		self.downLink = downLink
		self.delLink = delLink

# if __name__ == "__main__":
# 	fs = fileSystem("root/ root/alpha.txt,a.url,aDel.url root/bravo.txt,b.url,bDel.url\nroot/folderA/ root/folderA/a.txt,asdf.ase,asgr.yhu\nroot/folderA/folderB/\nroot/folderA/folderB/folderC/")
# 	#fs.decode(fs.fsString)
# 	(fs.loadFS('test'))
# 	nextfs = (fs.writeFolder())
# 	newFS = fileSystem(nextfs)
# 	newFS.loadFS('test')
# 	print(newFS.ls())
