from PIL import Image
from io import BytesIO
import requests
from Web_Connection import proxy_list
from Image_Manipulation import genImage

proxies = proxy_list.proxies


class Steg(object):
    def __init__(self, proxy):
        self.SIZE_FIELD_LEN = 64
        self.proxy = proxy

    # https://github.com/adrg/lsbsteg/blob/master/lsbsteg.py
    def encode(self, msg):
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
                raise ValueError('The message you are trying to embed is too long')

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

        def bits_from_bytes(bytes):
            bits = []
            for b in bytes:
                bits.extend([((b >> i) & 1) for i in range(7, -1, -1)])
            return bits

        def bits_from_str(s):
            return bits_from_bytes(s.encode('utf-8'))

        def embed(msg, input_image, output_image):
            bits = bits_from_str(msg)

            embed_message(bits, input_image)
            input_image.save(output_image, format="PNG")
            input_image.close()
            if self.checkImageIntegrity(msg, output_image) is False:
                print("Failed to verify image integrity...trying again.")  #TODO:// log
                return prepareNewImage()
            else:
                return output_image

        if type(msg) is not str:
            raise TypeError("The message being encoded needs to be a string")

        def prepareNewImage():
            image = Image.open(genImage.genCatImage())
            return embed(msg, image, BytesIO())

        return prepareNewImage()  # returns image as BytesIO object

    def checkImageIntegrity(self, msg, img):
        if msg == self.decode(img):
            return True
        else:
            return False

    def decodeImageFromURL(self, url):
        if self.proxy:
            r = requests.get(url, proxies=proxies)
        else:
            r = requests.get(url)

        if r.status_code == requests.codes.ok:
            return self.decode(BytesIO(r.content))
        else:
            raise FileNotFoundError("Could not retrieve image at {}.".format(url))

    def decode(self, img):
        if img is None:
            raise FileNotFoundError("Could not load image...image None")

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
            try:
                decodedMsg = message.decode('utf-8', 'strict')
            except UnicodeError as e:
                decodedMsg = message.decode('utf-8', 'ignore')

            return decodedMsg

        image = Image.open(img)
        decodedMsg = extract(image)
        image.close()
        return decodedMsg


def test(testNum, url, newImageName, message, predicted):
    steg = Steg()
    newImageName = newImageName + ".png"
    steg.assignImage(url)
    steg.encode(message, newImageName)
    actual = steg.decode()
    if actual is None:
        print("TEST " + str(testNum) + " FAILED: returned 'None'")
        return -1

    elif predicted == actual:
        print("TEST " + str(testNum) + " PASSED")
        return 1

    else:
        print("TEST " + str(testNum) + " FAILED: " + predicted + " does not equal '" + actual + "'")
        return -1

# if __name__ == '__main__':
#     url1 = "http://thecatapi.com/api/images/get?format=src&type=png"
#     newImageName1 = "test1.png"
#     message1 = "This is a basic test"
#     predicted1 = "This is a basic test"
#     test(1, url1, newImageName1, message1, predicted1)

#     url2 = "http://animalia-life.com/data_images/cat/cat2.jpg"
#     newImageName2 = "test2.png"
#     message2 = "This is a slightly longer message. It should pass despite this longer length, LOL"
#     predicted2 = "This is a slightly longer message. It should pass despite this longer length, LOL"
#     test(2, url2, newImageName2, message2, predicted2)

#     url3 = "http://thecatapi.com/api/images/get?format=src&type=png"
#     newImageName3 = "test3.png"
#     message3 = "This is another test with different symbols. *#*_#$@#$#::>{<?.;,[;.]l;..;,"
#     predicted3 = "This is another test with different symbols. *#*_#$@#$#::>{<?.;,[;.]l;..;,"
#     test(3, url3, newImageName3, message3, predicted3)

#     url4 = "http://thecatapi.com/api/images/get?format=src&type=png"
#     newImageName4 = "test4.png"
#     message4 = "So a message that is one hundred fifty one characters was a little too long Let's try one that is about one hundred"
#     predicted4 = "So a message that is one hundred fifty one characters was a little too long Let's try one that is about one hundred"
#     test(4, url4, newImageName4, message4, predicted4)

#     url5 = "http://thecatapi.com/api/images/get?format=src&type=png"
#     newImageName5 = "test5.png"
#     message5 = "A message with one hundred fifteen char worked. Let's make it 120 with symbols 239580(*)(&#$>.;.[].e32(&*)Hfefwegfwfwref"
#     predicted5 = "A message with one hundred fifteen char worked. Let's make it 120 with symbols 239580(*)(&#$>.;.[].e32(&*)Hfefwegfwfwref"
#     test(5, url5, newImageName5, message5, predicted5)

#     url6 = "http://thecatapi.com/api/images/get?format=src&type=png"
#     newImageName6 = "test6.png"
#     message6 = "One hundred twenty characters worked. I will test a message with 125 characters and symbols fg)&*feufbwfwef';.];'fwefaggarrg4"
#     predicted6 = "One hundred twenty characters worked. I will test a message with 125 characters and symbols fg)&*feufbwfwef';.];'fwefaggarrg4"
#     test(6, url6, newImageName6, message6, predicted6)