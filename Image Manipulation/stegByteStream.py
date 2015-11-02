import sys
import argparse
import hashlib
from PIL import Image
from io import BytesIO
from urllib.request import urlopen

#CDT Sjoholm learned how to work with byte streams from http://xlsxwriter.readthedocs.org/example_images_bytesio.html

class Steg(object):

    name = None
    uploaded = False
    SIZE_FIELD_LEN = 64
    imageBuffer = None

    def __int__(self):
        self.name = None
        self.uploaded = False

    def assignImage(self, url):
        image_data = BytesIO(urlopen(url).read())
        image_file = open("test2.png", "rb")
        image_data = BytesIO(image_file.read())

        image = Image.open(image_file)
        self.imageBuffer = image


    #cite the git Kyle got this from!!!!!!!!
    def encode(self, msg, newImageName):

        if type(msg) is not str:
            raise Exception("The message being encoded needs to be a string")

        if type(newImageName) is not str:
            raise Exception("The name of the new image needs to be a string")

        #if not self.uploaded:
            #raise Exception("Use the assignImage method to select an image within the directory")

        def formatImage(newImageName):
            if newImageName[-4:-1] + newImageName[-1] is not ".png":
                return newImageName + ".png"
            else:
                return newImageName

        def set_bit(target, index, value):
            mask = 1 << index
            target &= ~mask
            return target | mask if value else target
        
        def bits_from_int(i, width=1):
            bits = bin(i)[2:].zfill(width)
            return [int(b) for b in bits]  

        def embed_message(bits, img):
            pixels = img.load()
            width, height = img.size
            pixel_comps = len(pixels[0, 0])

            padding = []
            if self.SIZE_FIELD_LEN % pixel_comps != 0:
                padding = (pixel_comps - self.SIZE_FIELD_LEN % pixel_comps) * [0]

            bits = bits_from_int(len(bits), self.SIZE_FIELD_LEN) + padding + bits
            if len(bits) > width * height * pixel_comps * 0.1:
                raise Exception('The message you are trying to embed is too long')

            bits = iter(bits)
            for x in range(width):
                for y in range(height):
                    pixel = list(pixels[x, y])
                    for i, b in enumerate(pixel):
                        bit = next(bits, None)
                        if bit is None:
                            pixels[x, y] = tuple(pixel)
                            return

                        pixel[i] = set_bit(b, 0, bit)

                    pixels[x, y] = tuple(pixel)

        def embed(msg, image, newImageName):
            bits = bits_from_str(msg)

            embed_message(bits, image)
            image.save(newImageName, "PNG")


        def bits_from_bytes(bytes):
            bits = []
            for b in bytes:
                bits.extend([((b >> i) & 1) for i in range(7, -1, -1)])

            return bits


        def bits_from_str(s):
            return bits_from_bytes(s.encode('utf-8')) 
            return bits



        image = self.imageBuffer
        #newImageName = formatImage(newImageName)
        
        embed(msg, image, newImageName)
        image.close()


    def decode(self, name):


        def bytes_from_bits(bits):
            bytes = []

            lenBits = len(bits)
            for i in range(0, lenBits, 8):
                byte = bits[i:i+8]
                bytes.append(sum([(byte[8-b-1] << b) for b in range(7, -1, -1)]))

            return bytes

        def extract_length(pixels, width, height):
            bits = []
            for x in range(width):
                for y in range(height):
                    if len(bits) >= self.SIZE_FIELD_LEN:
                        return int(''.join(map(str, bits[:self.SIZE_FIELD_LEN])), 2), x, y

                    pixel = list(pixels[x, y])
                    bits.extend([(b & 1) for b in pixel])


        def extract_message(img):
            pixels = img.load()

            width, height = img.size
            length, offset_x, offset_y = extract_length(pixels, width, height)

            bits = []
            for x in range(offset_x, width):
                for y in range(offset_y, height):
                    pixel = list(pixels[x, y])
                    for b in pixel:
                        if len(bits) == length:
                            return bytes(bytes_from_bits(bits))

                        bits.append(b & 1)

        def extract(image):
            message = extract_message(image)

            decodedMsg = message.decode('utf-8')
            return decodedMsg

        image = Image.open(name)
        decodedMsg = extract(image)
        image.close()
        return decodedMsg

def test(testNum, imageName, newImageName, message, predicted):
    steg = Steg()
    newImageName = newImageName + ".png"
    steg.assignImage(imageName)
    steg.encode(message, newImageName)
    actual = steg.decode(newImageName)
    if actual is None:
        print("TEST " + str(testNum) + " FAILED: returned 'None'")
        return -1

    elif predicted == actual:
        print("TEST " + str(testNum) + " PASSED")
        return 1

    else:
        print("TEST " + str(testNum) + " FAILED: " + predicted + " does not equal  '" + actual + "'")
        return -1

if __name__ == '__main__':
   url = "http://thecatapi.com/api/images/get?format=src&type=png"
   steg = Steg()
   steg.assignImage(url)
   steg.encode("testing", "testBuffer.png")
   print(steg.decode("testBuffer.png"))

   #image_file.close()