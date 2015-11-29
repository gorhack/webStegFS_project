from fs.memoryfs import MemoryFS
import fs.errors

class CovertFilesystem(MemoryFS):

	def __init__(self, url = None):
		super(CovertFilesystem, self).__init__()
		self.url = url
		self.current_dir = '/'

	def sanitize_path(self, path = None):
		if path == '/':
			return ('/', 'dir')
		elif path == None or path == '.':
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
				fullpath = self.current_dir + path
			if self.exists(fullpath):
				if self.isdir(fullpath):
					return fullpath, 'dir'
				else:
					return fullpath, 'fil'
			else:
				return fullpath, 'non'

	def loadfs(self, fsstring):
		for fol in fsstring.split("\n")[:-1]:
			folderconents = fol.split(' ')
			curpath = folderconents[0]
			if curpath != '/':
				self.makedir(curpath)
			for filestring in folderconents[1:]:
				fileinfo = filestring.split(',')
				filename = fileinfo[0]
				downlink = fileinfo[1]
				dellink = fileinfo[2]
				self.setcontents(curpath + filename, downlink + ',' + dellink)

	def ls(self, path = None):
		san_path, node = self.sanitize_path(path)
		if node == 'dir':
			return self.listdir(san_path)
		elif node == 'fil':
			return ("File path given, directory path required")
		else:
			return ("Path given does not exist")

	def cd(self, path = '/'):
		if path == '/':
			self.current_dir = path
			return 1
		else:
			san_path, node = self.sanitize_path(path)
			if san_path[-1] != '/':
				san_path+='/'
			if node == 'dir':
				self.current_dir = san_path
				return 1
			elif node == 'fil':
				return "File path given, directory path required"
			else:
				return "Path given does not exist"

	def mkdir(self, path):
		san_path, node = self.sanitize_path(path)
		if san_path[-1] != '/':
			san_path+='/'
		if node == 'dir':
			return ("Directory already exists")
		else:
			self.makedir(san_path, recursive = True)
			return 1

	def rmdir(self, path = None, force = False):
		san_path, node = self.sanitize_path(path)
		if san_path[-1] != '/':
			san_path+='/'
		if node == 'fil':
			return ("Given path is a file; use rm")
		elif node == 'non':
			print(san_path)
			return ("Given path is not existent")
		else:
			try:
				self.removedir(san_path, force = force)
				return 1
			except:
				return ("Directory is not empty. Use force option to delete")


	def check_parent_dir(self, path):
		if path.find("/") == -1 or path.count("/") == 1 and path.find("/") == 0:
			return True
		san_path, node = self.sanitize_path(path)
		if self.exists(san_path.rsplit('/',1)[0] + '/'):
			return True
		return False

	def addfile(self, path, contents):
		san_path, node = self.sanitize_path(path)
		if not self.check_parent_dir(path):
			return ("Parent directory does not exist. Use mkdir")
		elif node == 'fil':
			return ("File already exists: file not added")
		elif node == 'dir':
			return ("Given path is a directory; name your file something else")
		else:
			self.setcontents(san_path, data = contents)
			return 1

	def rm(self, path):
		san_path, node = self.sanitize_path(path)
		if node == 'fil':
			self.remove(san_path)
			return 1
		elif node == 'dir':
			return ("Directory path given, file path required: use rmdir to remove directories")
		else:
			return ("Path given does not exist")

	def save(self):
		save_string = ''
		for directory, files in self.walk():
			save_string += directory
			if directory[-1]!='/':
				save_string += '/'
			for f in files:
				conts = self.getcontents(directory + '/' + f).decode().rsplit('\r',1)
				#self.setcontents(directory + '/' + f, data = conts[0])
				links = conts[1].split(',')
				save_string += ' ' + f + ',' + links[0]  + ',' + links[1]
			save_string += '\n'
		return save_string

	

"/ alpha.txt,a.url,aDel.url bravo.txt,b.url,bDel.url\n/folderA/ a.txt,asdf.ase,asgr.yhu\nr/folderA/folderB/\n/folderA/folderB/folderC/"