import urllib.request, random, string

def imagePathFetch():
	imageObject = urllib.request.urlopen("http://thecatapi.com/api/images/get?type=jpg")
	outFileName = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.jpg' #http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
	storeImage = open(outFileName, 'wb')
	storeImage.write(imageObject.read())
	imageObject.close()
	storeImage.close()
	return outFileName

def imageObjectFetch():
	return urllib.request.urlopen("http://thecatapi.com/api/images/get?type=jpg")