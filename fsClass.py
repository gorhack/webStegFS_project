from fs.memoryfs import MemoryFS
import fs.errors

class CovertFilesystem(MemoryFS):

	def __init__(self, url = None):
		super(CovertFilesystem, self).__init__()
		self.url = url
		self.current_dir = '/'

	def sanitize_path(self, path = None):
		if path == '.' or path == None:
			return (self.current_dir, 'dir')
		elif path == '..':
			if self.current_dir == '/':
				return (self.current_dir, 'dir')
			else:
				return (self.current_dir.rsplit('/',2)[0]+'/', 'dir')
		else:
			if path[0] == '/':
				fullpath = path
			else:
				if path[-1] != '/':
					path+='/'
				fullpath = self.current_dir + path
			if self.exists(fullpath):
				if self.isdir(fullpath):
					return fullpath, 'dir'
				else:
					return fullpath, 'fil'
			else:
				return fullpath, 'non'

	def loadfs(self, fsstring):
		for fol in fsstring.split("\n"):
			folderconents = fol.split(' ')
			curpath = folderconents[0]
			if curpath != '/':
				self.makedir(curpath)
			for filestring in folderconents[1:]:
				fileinfo = filestring.split(',')
				filename = fileinfo[0]
				downlink = fileinfo[1]
				dellink = fileinfo[2]
				self.open(curpath + filename, 'wb').close()

	def ls(self, path = None):
		san_path, node = self.sanitize_path(path)
		if node == 'dir':
			return self.listdir(san_path)
		elif node == 'fil':
			print ("File path given, directory path required")
		else:
			print ("Path given does not exist")

	def cd(self, path = '/'):
		san_path, node = self.sanitize_path(path)
		if node == 'dir':
			self.current_dir = san_path
			return self.current_dir
		elif node == 'fil':
			print ("File path given, directory path required")
		else:
			print ("Path given does not exist")

	def mkdir(self, path):
		san_path, node = self.sanitize_path(path)
		if node == 'dir':
			print ("Directory already exists")
		else:
			self.makedir(san_path, recursive = True)
			return san_path

	def rmdir(self, path = None, force = False):
		san_path, node = self.sanitize_path(path)
		if node == 'fil':
			print ("Given path is a file; use rm")
		elif node == 'non':
			print ("Given path is not existent")
		else:
			try:
				fs.removedir(san_path, force = force)
				return
			except:
				print("Directory is not empty. Use force option to delete")

	def addfile(self, path, contents):
		san_path, node = self.sanitize_path(path)
		if path.find('/') != -1 and self.sanitize_path(path.rsplit('/',1)[1])[1] == 'non':
			print("Directory does not exist to put a file into. Use mkdir")
			return
		elif node == 'fil':
			print ("File already exists: file not added")
		elif node == 'dir':
			print ("Given path is a directory; name your file something else")
		else:
			self.setcontents(san_path, data = contents)
			return

	def rm(self, path):
		san_path, node = self.sanitize_path(path)
		if node == 'fil':
			self.remove(san_path)
		elif node == 'dir':
			print ("Directory path given, file path required: use rmdir to remove directories")
		else:
			print ("Path given does not exist")

	def save(self):
		save_string = ''
		for directory, files in fs.walk():
			save_string += directory
			for f in files:
				conts = fs.getcontents(directory + '/' + f).rsplit('\r',1)
				fs.setcontents(directory + '/' + f, data = conts[0])
				links = conts[1].split(',')
				save_string += ' ' + f + ',' + links[0]  + ',' + links[1]
			save_string += '\n'
		return save_string

	

"/ alpha.txt,a.url,aDel.url bravo.txt,b.url,bDel.url\n/folderA/ a.txt,asdf.ase,asgr.yhu\nr/folderA/folderB/\n/folderA/folderB/folderC/"