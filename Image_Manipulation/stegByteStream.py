from PIL import Image
from io import BytesIO
import requests
from Web_Connection import proxy_list
from Image_Manipulation import genImage

"""@package stegByteStream

Documentation for the stegByteStream module.
"""

proxies = proxy_list.proxies


class Steg(object):
    def __init__(self, proxy):
        """
        The constructor. Extends the superclass constructor.
        """
        self.SIZE_FIELD_LEN = 64
        self.proxy = proxy

    # https://github.com/adrg/lsbsteg/blob/master/lsbsteg.py
    def encode(self, msg):
        """
        The encode method use the least significant bit stegonography
        technique to encode a message into an image.
        This method takes a message as a string.
        This method returns an image as a BytesIO object.

        """
        def set_bit(target, index, value):
            """
            The set_bit function changes the value of a target bit.
            This function takes a target value as an integer, an index value as an integer, and a value as an integer.
            This function returns an integer.
            """
            mask = 1 << index  # shift 1 to the left by index number of bits
            target &= ~mask  # decrement the target by the value of mask
            return target | mask if value else target  # perform bit wise or of target and mask

        def bits_from_int(i, width=1):
            """
            The bits_from_int method turns an integer into a list of bits values. The width parameter
            determines how many bits with a value of zero to add to the left side of the bit value.
            This function takes an integer and a width as an integer.
            This function returns a list of bit values.
            """
            bits = bin(i)[2:].zfill(width)  # turn i into a binary value, and extend the length of the binary value by width number of zeros
            return [int(b) for b in bits]  # break the binary value into a list, where each list item is a bit. Return the list.

        def embed_message(bits, img):
            """
            The embed_message function implements the least significant bit stegonography technique.
            For each pixel in the image, its value is changed based on the bits that form the message.
            This function takes the message as a list of bits, and an image object.
            This function does not return anythimng.
            """
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
            """
            The bits_from_bytes function turns a bytes object into a list of bits.
            This function takes a bytes object.
            THis function returns a list of bits.
            """
            bits = []  # initialize list of bits
            for b in bytes:  # iterate over
                bits.extend([((b >> i) & 1) for i in range(7, -1, -1)])
            return bits

        def bits_from_str(s):
            """
            The bits_from_str function turns a message into a list of bits.
            This function takes a string.
            This function returns a list of bits.
            """
            return bits_from_bytes(s.encode('utf-8'))  # turn the string into a bytes object, and pass that object into bits_from_bytes

        def embed(msg, input_image, output_image):
            """
            The embed function turns the message into bits, encodes those bits into the input image
            using the least significant bit stegonography technique, and then saves
            the resulting image as an out image. If the message was properly embeded,
            the output image is returned.
            This function takes a message as a string, an input image as BytesIO object,
            and an output image as a BytesIO object.
            This function returns a BytesIO.
            """
            bits = bits_from_str(msg)  # turn the message string into a list of bits.

            embed_message(bits, input_image)  # encode the message bits into the input image
            input_image.save(output_image, format="PNG")  # save the resulting input image as the output image in a .png format
            input_image.close()  # close the input image
            if self.checkImageIntegrity(msg, output_image) is False:  # check is the message was encoded properly
                print("Failed to verify image integrity...trying again.")  # TODO:// log  # if the image was not encoded properly, print this line
                return prepareNewImage()  # try to encode the message again with a new image
            else:  # if the message was properly encoded into the image
                return output_image  # return the output image

        if type(msg) is not str:  # if the message is not string
            raise TypeError("The message being encoded needs to be a string")  # raise error stating that the message needs to be a string

        def prepareNewImage():
            """
            The prepareNewImage function retrieves an image from the Cat API, and embeds the
            message into that image.
            This function does not take any paramters.
            This function returns an image as a BytesIO object.
            """
            image = Image.open(genImage.genCatImage())  # retrieve image from Cat API
            return embed(msg, image, BytesIO())  # embed the message into the cat image, save the result to the BytesIO() object, and return that object.

        return prepareNewImage()  # returns image as BytesIO object

    def checkImageIntegrity(self, msg, img):
        """
        The checkImageIntegrity method checks to see if a message has been properly encoded into an image.
        This method takes a message as string, and an image as a BytesIO object.
        This method returns a boolean.
        """
        if msg == self.decode(img):  # if the message is the same as a message retrieved from a decoded image
            return True  # return true
        else:  # if the message is not the same as a message retrieved from a decoded image
            return False  # return false

    def decodeImageFromURL(self, url):
        """
        The decodeImageFromURL method retrieves an image from a url, and extracts a message from the
        image. The image needs to have been encoded using the stegByteStream.encode(msg) method.
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

    def decode(self, img):
        """
        The decode method use the principles of the least significant bit stegonography
        technique to form an image from a the pixel values in an image.
        This method takes an image as a BytesIO object.
        This method returns a message as a string.
        """
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
            """
            The extract function finds a message inside an image. The message is checked and cleaned of any
            errors that might have occured during the decoding.
            This function takes an image object.
            This function returns a message as a string.
            """
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


def testSteg(testNum, url, newImageName, message, predicted):
    """
    The testSteg function tests the least significant bit stegonography technique.
    """
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

    r = requests.get('http://thecatapi.com/api/images/get?format=src&type=png')
    if r.status_code == requests.codes.ok:
        image_name = BytesIO(r.content)
    else:
        image_name = None

    if image_name is None:
        raise Exception("Failed to assign the image. Error with retrieving the image.")

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

    def embed(msg, image):
        bits = bits_from_str(msg)

        embed_message(bits, image)
        image.save(output_image, format="PNG")

    def bits_from_bytes(bytes):
        bits = []
        for b in bytes:
            bits.extend([((b >> i) & 1) for i in range(7, -1, -1)])
        return bits

    def bits_from_str(s):
        return bits_from_bytes(s.encode('utf-8'))

    image = Image.open(image_name)
    embed(msg, image)
    image.close()
    image_name.close()
    r.close()
    return output_image  # returns image as BytesIO object

    def decode(self, url):
        if self.proxy:
            r = requests.get(url, proxies=proxies)
        else:
            r = requests.get(url)

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