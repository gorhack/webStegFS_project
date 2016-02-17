#!/usr/bin/env python3

from PIL import Image
from io import BytesIO
import binascii
import requests
from Image_Manipulation import genImage
from main import Console
# import socks
# import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
# socket.socket = socks.socksocket

"""@package lsbsteg

Documentation for the lsbsteg module.
The lsbsteg module has two primary functions, encode and decode.
Encode takes a message as a bytearray object and returns a url to the
encoded image using the desired social media site.
DecodeFromURL takes a url from the social media site, downloads the image,
and then decodes the image. Decode takes a BytesIO object and returns a
binary string containing the binary of the decoded message.
"""

# Constants
# URLLIB-> in bits
NEXT_IMAGE = '0101010101010010010011000100110001001001010000100010110100111110'
NEXT_IMAGE_HEX = bytearray.fromhex('%08X' % int(NEXT_IMAGE, 2))

URL_LENGTH_IN_BINARY = 48  # the length of 6 characters in binary

# END_OF_FILE in bits
SPECIAL_EOF = '01000101010011100100010001011111010011110100' + \
                '01100101111101000110010010010100110001000101'
SPECIAL_EOF_HEX = bytearray.fromhex('%08X' % int(SPECIAL_EOF, 2))


class Steg(object):
    def __init__(self, proxy):
        """
        The constructor. Extends the superclass constructor.
        """
        self.SIZE_FIELD_LEN = 64
        self.proxy = proxy
        # TODO:// need to use main.Console functions to upload files and
        # download files for modularity. Currently hardcoded an instance of
        # the Console class.
        self.cons = Console('sendspace', 'lsbsteg', 'covertMount', '',
                            'noproxy', False)

    # prepare message and image for encoding
    # returns url
    def encode(self, message):
        """
        The encode function encodes up to 1 byte of data per pixel.
        This function takes a message as a bytearray object as a parameter.
        This function returns a url as a string to the encoded message.
        """
        def prepareNewImage():
            """
            The prepareNewImage function retrieves an image from the Cat API.
            This function does not take any paramters.
            This function returns an image as a BytesIO object.
            """
            print("preparing new image")
            return Image.open(genImage.genCatImage())

        # takes the full msg as bytearray and size_available to image as int
        # returns a tuple (msg that will fit, rest of msg)
        def prepareMessage(msg, size_available):
            """
            The prepare message function splits the message based on the
            maximum size available to the steg function based on the number of
            pixels.
            """
            print("preparing message")
            return msg[:-size_available], msg[-size_available:]

        msg = message

        # append EOF to image
        msg.extend(SPECIAL_EOF_HEX)

        # create image
        image = prepareNewImage()
        width, height = image.size

        # for logging purposes
        print("bytes in message: {}".format(len(msg)))
        print("pixels in image:  {}".format(height * width))

        # prepare the message
        rest, msg = prepareMessage(msg, width * height)
        # encode the message
        url = self.encodeSteg(msg, image)

        # encode rest of message if necessary
        if len(rest) > 0:
            # append the next image identifier and the previous url to
            # the next message
            rest.extend(NEXT_IMAGE_HEX)
            rest.extend(str.encode(url))
            # change url to the most recently uploaded url
            url = self.encode(rest)

        return url

    def encodeSteg(self, msg, image):
        """
        The encodeSteg function modifies the image and encodes the binary
        message into the image using least significant bit stegenography.
        This function takes a message as a byte array and an image as a
        PIL Image object.
        This function returns the url as a str.
        """
        pix = image.load()

        curwidth = 0
        curheight = 0

        for byte in msg:
            current_byte = format(byte, '#010b')[2:]  # keeps 0s in formatting
            # splits byte into 3 groups ('111', '111', '11')
            # for encoding to pixels
            bits = (current_byte[0:3], current_byte[3:6], current_byte[6:8])

            pixel = pix[curwidth, curheight]  # gets the current pixel

            # having lots of issues with red, green, blue = pixel
            # TypeError: 'int' object is not subscriptable
            # ValueError: too many values to unpack (expected 3)

            # initialize RGB values
            red, green, blue = 0, 0, 0
            try:
                # splits pixel into RGB values
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]
            except Exception as e:
                print("pixel may contain alpha value or not enough? " +
                      str(e))
                print(pixel)

            '''
            encodes a byte into a pixel's colors
            1) first 3 bits encoded into red's least significant bits
            2) next 3 bits encoded into green's least significant bits
            3) last 2 bits encoded into blue's least significant bits

            max change of 7 to color component
            '''
            red = format(red, '#010b')[2:]
            red = '0b' + red[0:5] + bits[0]
            red = int(red, 2)

            green = format(green, '#010b')[2:]
            green = '0b' + green[0:5] + bits[1]
            green = int(green, 2)

            blue = format(blue, '#010b')[2:]
            blue = '0b' + blue[0:5] + bits[2]
            blue = int(blue, 2)

            # sets the current pixel to encoded values
            pix[curwidth, curheight] = (red, green, blue)

            # go to next pixel
            curwidth += 1
            if (curwidth >= image.width):
                curwidth = 0
                curheight += 1

        # save the image to BytesIO object
        output_image = BytesIO()
        image.save(output_image, format="PNG")
        image.close()

        # upload the image
        contents, downlink = self.cons.uploadfile(output_image)
        contents.close()

        return downlink

    def decodeImageFromURL(self, file_id):
        """
        The decodeImageFromURL method retrieves an image from a url,
        and extracts a message from the image. The image needs to have
        been encoded using the stegByteStream.encode(msg) method.
        This method takes a url as a string.
        This method returns the decoded message as a string.
        """
        url = self.cons.downloadImage(file_id)
        if self.proxy:  # if the application is using proxies
            #r = requests.get(url, proxies=self.proxy)  # open a url using the proxies
            r = requests.get(url)
        else:  # if the application is not using proxies
            r = requests.get(url)  # open the url without proxies

        if r.status_code == requests.codes.ok:  # if the url was successfully opened
            print("decoding URL")
            return self.decode(BytesIO(r.content))  # decode the image found in the url
        else:  # if the url was not successfully opened
            raise FileNotFoundError("Could not retrieve image at {}.".format(url))  # raise an exception that shows the faulty url

    # takes image as BytesIO object
    # returns a BytesIO
    def decode(self, img):
        """
        The decode function decodes the message from an image.
        This function takes an image as a BytesIO object and returns a string
        representing the bits of the message. To decode the bits:
        `bytearray.fromhex('%08X' % int(message, 2))`
        """

        # convert BytesIO image to PIL Image object
        img.seek(0)
        image = Image.open(img)
        pixels = image.load()

        # initialize message
        msg = ''

        for h in range(image.height):
            for w in range(image.width):
                # haven't had problems with pixels in decode because if it
                # works in encode it will work in decode...
                red = pixels[w, h][0]
                green = pixels[w, h][1]
                blue = pixels[w, h][2]

                # add padding
                red = format(red, '#010b')[2:]
                green = format(green, '#010b')[2:]
                blue = format(blue, '#010b')[2:]

                # assemble the message
                decodeMsg = red[-3:] + green[-3:] + blue[-2:]

                # see if the eof bytes have been found
                # subtract 8 for current byte
                special_ending = msg[-(len(SPECIAL_EOF) - 8):] + decodeMsg

                if special_ending == SPECIAL_EOF:
                    msg += decodeMsg
                    print("reached end of image")

                    # remove EOF signature
                    msg = msg[:-len(SPECIAL_EOF)]

                    length_of_url = len(NEXT_IMAGE) + URL_LENGTH_IN_BINARY

                    if msg[-length_of_url:-URL_LENGTH_IN_BINARY] == NEXT_IMAGE:
                        print("found another image to decode")
                        url_bin = msg[-URL_LENGTH_IN_BINARY:]

                        # converts binary string of url to ascii
                        url = int(url_bin, 2)
                        url = url.to_bytes((url.bit_length() +
                                            7) // 8, 'big').decode()

                        # remove URL and identifier
                        msg = msg[:-length_of_url]

                        # append next image's message
                        next_msg = self.decodeImageFromURL(url)

                        msg += next_msg

                    return msg
                else:
                    msg += decodeMsg

        return ("Something messed up... " + msg[-50:])

    def bytesarray2BytesIO(self, data):
        """
        The bytesarray2BytesIO function converts a bytesarray to BytesIO
        object. This may be more useful in converting the string representing
        the bits to a BytesIO object.
        """
        return BytesIO(data)
