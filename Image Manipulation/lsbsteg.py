#import sys
#import argparse
#import hashlib
from PIL import Image
import argparse
import os

class Steg(object):

    name = None
    uploaded = False
    SIZE_FIELD_LEN = 64

    def __init__(self):
        self.name = None
        self.uploaded = False
        self.action = args.action
        self.message = args.message
        self.image_path = args.image_path

    def assignImage(self, name):
        try:
            f = open(name, "r")
            self.name = name
            f.close()
            self.uploaded = True
            return 1
        except IOError:
            return -1

    # https://github.com/adrg/lsbsteg/blob/master/lsbsteg.py
    def encode(self, msg, newImageName):

        if type(msg) is not str:
            raise Exception("The message being encoded needs to be a string")

        if type(newImageName) is not str:
            raise Exception("The name of the new image needs to be a string")

        if not self.uploaded:
            raise Exception("Use the assignImage method to select an image within the directory")

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
            if len(bits) > width * height * pixel_comps:
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



        image = Image.open(self.name)
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

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Encode or decode message within an image with LSB encoding.')
  parser.add_argument('action', choices=['encode', 'decode'], help='Encode or decode image.')
  parser.add_argument('--image_path', default='', help='Path to image') # local or relative 
  parser.add_argument('--message', default='', help='Message to encode in image') # change to file path

  # TODO:// if encoding image path and message required
  # TODO:// if decoding image name required
  args = parser.parse_args()
  steg = Steg() #creates the object
  if (steg.action == 'encode'):
    # TODO:// error handling on params
    newImageName = os.path.splitext(steg.image_path)[0] + '_1.png'
    print('encoding ' + steg.message + ' to ' + steg.image_path + ' as ' + newImageName)
    steg.assignImage(steg.image_path)
    steg.encode(steg.message, newImageName)
  else: 
    print('decoding ' + steg.image_path)
    print(steg.decode(steg.image_path))

def test(testNum, imageName, newImageName, message, predicted):
    steg = Steg()
    newImageName = newImageName + ".png"
    steg.assignImage(imageName)
    try:
        steg.encode(message, newImageName)
    except:
        if (len(message) > 28):
            message = message[0:27]
        print("TEST " + str(testNum) + " FAILED: message is probably too long\nMessage: " + message)
        return -1
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

# if __name__ == '__main__':
#    testPass = 0
#    totalTests = 26

#    msg1 = ""
#    msg1result = ""
#    testPass += test(1, "test1.jpg", "test1result1", msg1, msg1result)
   
#    msg2 = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    msg2result = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    testPass += test(2, "test1.jpg", "test1result2", msg2, msg2result)
    
#    msg3 = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    msg3result = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    testPass += test(3, "test1.jpg", "test1result3", msg3, msg3result)
   
#    msg4 = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    msg4result = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    testPass += test(4, "test1.jpg", "test1result4", msg4, msg4result)

#    msg5 = "This is just a normal sentence. It is not a long sentence!"
#    msg5result = "This is just a normal sentence. It is not a long sentence!"
#    testPass += test(5, "test1.jpg", "test1result5", msg5, msg5result)

#    msg6 = ""
#    msg6result = ""
#    testPass += test(6, "test2.png", "test2result1", msg6, msg6result)
   
#    msg7 = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    msg7result = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    testPass += test(7, "test2.png", "test2result2", msg7, msg7result)
    
#    msg8 = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    msg8result = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    testPass += test(8, "test2.png", "test2result3", msg8, msg8result)
   
#    msg9 = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    msg9result = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    testPass += test(9, "test2.png", "test2result4", msg9, msg9result)

#    msg10 = "This is just a normal sentence. It is not a long sentence!"
#    msg10result = "This is just a normal sentence. It is not a long sentence!"
#    testPass += test(10, "test2.png", "test2result5", msg10, msg10result)

#    msg11 = ""
#    msg11result = ""
#    testPass += test(11, "test3.jpg", "test3result1", msg11, msg11result)
   
#    msg12 = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    msg12result = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    testPass += test(12, "test3.jpg", "test3result2", msg12, msg12result)
    
#    msg13 = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    msg13result = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    testPass += test(13, "test3.jpg", "test3result3", msg13, msg13result)
   
#    msg14 = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    msg14result = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    testPass += test(14, "test3.jpg", "test3result4", msg14, msg14result)

#    msg15 = "This is just a normal sentence. It is not a long sentence!"
#    msg15result = "This is just a normal sentence. It is not a long sentence!"
#    testPass += test(15, "test3.jpg", "test3result5", msg15, msg15result)

#    msg16 = ""
#    msg16result = ""
#    testPass += test(16, "test4.png", "test4result1", msg16, msg16result)
   
#    msg17 = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    msg17result = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    testPass += test(17, "test4.png", "test4result2", msg17, msg17result)
    
#    msg18 = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    msg18result = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    testPass += test(18, "test4.png", "test4result3", msg18, msg18result)
   
#    msg19 = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    msg19result = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    testPass += test(19, "test4.png", "test4result4", msg19, msg19result)

#    msg20 = "This is just a normal sentence. It is not a long sentence!"
#    msg20result = "This is just a normal sentence. It is not a long sentence!"
#    testPass += test(20, "test4.png", "test4result5", msg20, msg20result)

#    msg21 = ""
#    msg21result = ""
#    testPass += test(21, "test5.jpg", "test5result1", msg21, msg21result)
   
#    msg22 = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    msg22result = "this is testing all lowercase abcdefghijklmnopqrstuvwxyz fe f wfa arfa fgrgs a"
#    testPass += test(22, "test5.jpg", "test5result2", msg22, msg22result)
    
#    msg23 = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    msg23result = "THIS IS TESTING ALL UPPERCASE ABCDEFGHIJKLMNOPQRSTUVWXYZ FIF WERFOAQ EFJA QD QADC"
#    testPass += test(23, "test5.jpg", "test5result3", msg23, msg23result)
   
#    msg24 = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    msg24result = "this is testing symbols 1234567890!(@%*)%##*$(%&**#%&^&%$)_+_@)#-012-=301-=0-=0-=}{{:{:><:<[];';,/.,"
#    testPass += test(24, "test5.jpg", "test5result4", msg24, msg24result)

#    msg25 = "This is just a normal sentence. It is not a long sentence!"
#    msg25result = "This is just a normal sentence. It is not a long sentence!"
#    testPass += test(25, "test5.jpg", "test5result5", msg25, msg25result)

#    msg25 = "This is just a normal sentence. It is not a long sentence!"
#    msg25result = "This is just a normal sentence. It is not a long sentence!"
#    testPass += test(25, "test5.jpg", "test5result5", msg25, msg25result)

#    msg26 = """This is a long sentence *26*
#                 "gugnnfnwfweufnefnfuwefnweufnwefuwnefuwnfwuefnewfuneffuneffwefwfdwefgfvagfafjkjfvbaerhvkbhvbahvbakhvbvkafbvakb
#                 "fnwfnfiaerugnoiugnhfiabnrhygbeargbrehygvbrahfybawfhrbgflahkfbeawlhfbralghabfhlwebfhrlgbalkhfbahlfkabgflhewrfb
#                 "fwnfuirhneiugfhanofabwgbargabwehfbhvbrhfbaweoiufbarhyvbafbebfaovbhavlsdhfvbarhvbahfvbaslhdfvbarhvbaldvhbsadvh
#                 "fjewrugnrigaohifnelhanfadnfaeriufgnarvinafunariuvnarvaerbgaorvbufbaewruifbeadnefu"""
#    msg26result = ""
#    testPass += test(26, "test5.jpg", "test5result6", msg26, msg26result)   


#    print(str(testPass) + " out of " + str(totalTests) + " tests passed")
