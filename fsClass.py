class fileSystem(object):
	def __init__(self, fsString):
		self.currentDir = None
		self.fsString = fsString

	def decode(self):
		rootCont = self.fsString.split('\n')
		tempDict = {}
		for rootNode in rootCont:
			foldOrCont = rootNode.split()
			foldName = foldOrCont[0][:-1]
			foldCont = {}
			fileNameCont = []
			for node in foldOrCont[1:]:
				fileInfo = node.split(',')
				fileName = fileInfo[0]
				fileDown = fileInfo[1]
				fileDel = fileInfo[2]
				foldCont[fileName] = (fsFile(fileName,fileDown,fileDel))
				#fileNameCont.append(fileName)
			foldLevel = foldName.count('/') - 1
			foldParent = foldName.rsplit('/', 1)[0] 
			tempDict[foldName] = fsFolder(foldName, foldCont, foldLevel, foldParent)
			tempDict[foldName].fileNames = fileNameCont
			if foldLevel > 0:
				tempDict[foldName].parent.contents[foldName] = (tempDict[foldName])
				#tempDict[foldName].foldNames.append(foldName)
		return tempDict['root']

	def loadFS(self, url):
		if url == 'test':
			self.currentDir = self.decode()
			return 'Test FS read complete'
		steg = lsbsteg.Steg()
		try:
			steg.assignImage(url)
		except:
			print('Bad URL or computer offline')
			
		self.currentDir = decode(steg.decode())
		return 'File system loaded'

	def newFS(self):
		self.currentDir = fsFolder('root', [], 0, '')
		return 'New file system created'

	def ls(self): #TODO:// ls [path]
		outString = "" #The folder: " + self.currentDir.name + " contains:\n"
		for key,node in self.currentDir.contents.items():
			#if type(node) is fsFolder:
				#TODO color outputs
			#needs to handle errors:
			"""
			if cd .. with test dir then ls will error 
			"""
			name = node.name
			length = len(name)
			outString+= name + (16-length)*" "
		return outString

	def cd(self, destDir):
		if destDir == '..':
			self.currentDir = self.currentDir.parent
		elif destDir in self.currentDir.foldNames:
			self.currentDir = self.currentDir.contents


class fsFolder(object):
	def __init__(self, name, contents, level, parent):
		self.name = name
		self.contents = contents
		self.level = level
		self.parent = parent
		self.foldNames = []
		self.fileNames = []

class fsFile(object):
	def __init__(self, name, downLink, delLink):
		self.name = name
		self.downLink = downLink
		self.delLink = delLink

#def fsSend(root):
#fs = fileSystem("root/ root/alpha.txt,a.url,aDel.url root/bravo.txt,b.url,bDel.url")
#fs.decode(fs.fsString)
#print(fs.loadFS('test'))
#print(fs.ls())