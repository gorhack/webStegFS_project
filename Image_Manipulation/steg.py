from PIL import Image
from Web_Connection import proxy_list
from Image_Manipulation import genImage
from io import BytesIO

"""@package steg

Documentation for the steg module.
"""

proxies = proxy_list.proxies

class Steg(object):

	def __init__(self, proxy):
		"""
		The constructor. Extends the superclass constructor.
		"""
		self.proxy = proxy
	
	def cleanVal(self, value):
		if len(value) == 3:
			return value
		if len(value) == 2:
			return "0" + value
		if len(value) == 1:
			return "00" + value
		else:
			raise Exception("Unexpected ASCII character: " + value)


	def encodeImage(self, img, msg, output):
		tagged = msg + "ENDMSG"  # add end tag to message to aid in decoding the image
		
		width, height = img.size  # get the width and height of the image
		
		if len(tagged) > width * height:  # if the length of the message is greater than the number of pixels in the message
			print("Mesage is too big to encode into this image")  # throw this error message
			print("Message length: " + str(len(msg)))
			print("Number of pixels in image: " + str(width * height))
			return  # do not encode the image

		pix = img.load() # returns a pixel access object that can be used to read and modify pixels

		curWidth = 0  # initialize width counter
		curHeight = 0  # intialize height counter
		
		for c in tagged:  # for each character in the tagged message
			asciiVal = self.cleanVal(str(ord(c)))  # get the ascii value for the character
			redVal = asciiVal[0]  # get the first digit of the ascii value to be assigned to the red pixel bits
			greenVal = asciiVal[1]  # get the second digit of the ascii value to be assigned to the green pixel bits
			blueVal = asciiVal[2]  # get the third digit of the ascii value to be assigned to the blue pixel bits
			
			curPix = pix[curWidth, curHeight]

			pixRed = self.cleanVal(str(curPix[0]))
			pixGreen = self.cleanVal(str(curPix[1]))
			pixBlue = self.cleanVal(str(curPix[2]))

			pixRed = pixRed[0] + pixRed[1] + redVal
			pixGreen = pixGreen[0] + pixGreen[1] + greenVal
			pixBlue = pixBlue[0] + pixBlue[1] + blueVal

			newPix = (int(pixRed), int(pixGreen), int(pixBlue))
			pix[curWidth, curHeight] = newPix

			curWidth += 1
			if (curWidth >= width):
				curWidth = 0
				curHeight += 1
				if (curHeight > height):
					print("Somehow we tried going above the height of the picture at character: " + c)
		
		img.save(output, format="PNG")
		img.close()
		return output

	def encode(self, msg):
		img = Image.open(genImage.genCatImage())  # retrieve image from Cat API
		return self.encodeImage(img, msg, BytesIO())

	def cleanPix(self, pix):
		redPix = self.cleanVal(str(pix[0]))
		greenPix = self.cleanVal(str(pix[1]))
		bluePix = self.cleanVal(str(pix[2]))
		return (redPix, greenPix, bluePix)

	def decodePixel(self, pixTup):
		fixedTup = self.cleanPix(pixTup)
		redPix = fixedTup[0][2]
		greenPix = fixedTup[1][2]
		bluePix = fixedTup[2][2]
		return int(redPix + greenPix + bluePix)

	def decodeImage(self, img):
		pix = img.load()
		width, height = img.size
		decodedMsg = ""
		for y in range(height):
			for x in range(width): 
				decodedAscii = self.decodePixel(pix[x,y])
				decodedMsg += chr(decodedAscii)
				if len(decodedMsg) >= 6:
					end = decodedMsg[-6:-1] + decodedMsg[-1]
					if end == "ENDMSG":
						return decodedMsg[:len(decodedMsg) - 6]

	def decode(self, url):
		"""
		The decodeImageFromURL method retrieves an image from a url, and extracts a message from the
        image. The image needs to have been encoded using the steg.encode(msg) method.
        This method takes a url as a string.
        This method returns the decoded message as a string.
        """
		if self.proxy:  # if the application is using proxies
			r = requests.get(url, proxies=proxies)  # open a url using the proxies
		else:  # if the application is not using proxies
			r = requests.get(url)  # open the url without proxies

		if r.status_code == requests.codes.ok:  # if the url was successfully opened
			return self.decode(BytesIO(r.content))  # decode the image found in the url
		else:  # if the url was not successfully opened
			raise FileNotFoundError("Could not retrieve image at {}.".format(url))  # raise an exception that shows the faulty url

	def imgPrep(self):
		name = "test.jpg"
		img = Image.open(name)
		pix = img.load()  # returns a pixel acess object that can be used to read and modify pixels
		width, height = img.size
		for x in range(width):
			for y in range(height):
				
				red, green, blue = pix[x,y]
				red = red - (red % 10)
				green = green - (green % 10)
				blue = blue - (blue % 10)
				pix[x,y] = (red, green, blue)
		
		img.save("result.png")
		img.close()

# if __name__ == "__main__":
	
# 	steg = Steg()
# 	name = "result.png"
# 	newName = "encodedImage.png"
	
# 	img = Image.open(name)
# 	steg.encode(img, "testing")
# 	img.save(newName)
	
# 	newimg = Image.open(newName)
# 	# pix = newimg.load()
# 	# pix = img.load()
# 	# for x in range(30):
# 	# 	print(pix[x,0])
	
# 	print(steg.decode(newimg))
# 	img.close()
# 	newimg.close()