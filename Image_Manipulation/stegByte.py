import requests
from PIL import Image
from Web_Connection import proxy_list
from Image_Manipulation import genImage
from io import BytesIO

class Steg(object):

	def __init__(self, proxy):
		"""
		The constructor. Extends the superclass constructor.
		"""
		self.proxy = proxy

	def encodeImage(self, bytes, img):
		# https://stevendkay.wordpress.com/2009/10/07/image-steganography-with-pil/