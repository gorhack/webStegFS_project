#!/usr/bin/env python3

"""
The basic idea of the algorithm is to take each individual bit of the message
and set it as the least significant bit of each component of each pixel of the
image. A pixel has Red, Green, Blue components and sometimes an Alpha
component. Because the values of these components change very little if the
least significant bit is changed, the color difference is not particularly
noticeable, if at all.
"""

from PIL import Image
from io import BytesIO
try:
    from Image_Manipulation import genImage
except ImportError:
    from src.Image_Manipulation import genImage
import platform
import subprocess
import requests
if platform.system() == 'Linux':
    torEnabled = subprocess.check_output(['ps', 'aux']).decode().find('/usr/bin/tor')
    if torEnabled > -1:
        import socks
        import socket
        print("Using tor, rerouting connection")
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket


def ascii2bits(message):
    """
    The ascii2bits function converts a string of ascii characters to a
    padded string of bits.
    """
    msg = bin(int.from_bytes(message.encode(), 'big'))[2:]
    return msg.zfill(8 * ((len(msg) + 7) // 8))

# Constants
NEXT_IMAGE = 'URLLIB->'
NEXT_IMAGE_BITS = ascii2bits(NEXT_IMAGE)
NEXT_IMAGE_HEX = bytearray(NEXT_IMAGE.encode())

SPECIAL_EOF = 'END_OF_FILE'
SPECIAL_EOF_BITS = ascii2bits(SPECIAL_EOF)
SPECIAL_EOF_HEX = bytearray(SPECIAL_EOF.encode())


class Steg(object):
    """
    Documentation for the lsbsteg module.
    The lsbsteg module has two primary functions, encode and decode.
    Encode takes a message as a bytearray object and returns a url to the
    encoded image using the desired social media site.
    DecodeFromURL takes a url from the social media site, downloads the image,
    and then decodes the image. Decode takes a BytesIO object and returns a
    binary string containing the binary of the decoded message.
    """
    def __init__(self, proxy, online_file_store):
        """
        The constructor. Extends the superclass constructor.
        """
        self.SIZE_FIELD_LEN = 64
        self.proxy = proxy
        self.cons = online_file_store
        self.URL_LENGTH_IN_BINARY = self.cons.url_size * 8

    def encode(self, message):
        """
        The encode method encodes up to 1 byte of data per pixel in an image.
        This method takes a message as a bytearray object as a parameter.
        This method returns a url as a string to the encoded message.
        """
        def prepareNewImage():
            """
            The prepareNewImage function retrieves an image from the Cat API.
            This function does not take any parameters.
            This function returns an image as a BytesIO object.
            """
            return Image.open(genImage.genCatImage())

        def prepareMessage(msg, size_available):
            """
            The prepare message function splits the message based on the
            maximum size available to the steg function based on the number of
            pixels. Returns a tuple (rest of message, message that will fit)
            """
            return msg[:-size_available], msg[-size_available:]

        msg = message

        # append EOF to image
        msg.extend(SPECIAL_EOF_HEX)

        # create image
        image = prepareNewImage()
        width, height = image.size

        # for logging purposes
        # print("bytes in message: {}".format(len(msg)))
        # print("pixels in image:  {}".format(height * width))

        # prepare the message
        rest, msg = prepareMessage(msg, width * height)
        # encode the message
        url = self.encodeSteg(msg, image)

        # encode rest of message if necessary
        if len(rest) > 0:
            # append the next image identifier and the previous url to
            # the next message
            rest.extend(NEXT_IMAGE_HEX)
            print(url)
            rest.extend(str.encode(url))
            # change url to the most recently uploaded url
            url = self.encode(rest)
        return url

    def encodeSteg(self, msg, image):
        """
        The encodeSteg method modifies the image and encodes the binary
        message into the image using least significant bit stegenography.
        This method takes a message as a byte array and an image as a
        PIL Image object.
        This method returns the url as a str.
        """
        pix = image.load()

        curwidth = 0
        curheight = 0

        for byte in msg:
            current_byte = format(byte, '08b')  # keeps 0s in formatting
            # splits byte into 3 groups ('111', '111', '11')
            # for encoding to pixels
            bits = (current_byte[0:3], current_byte[3:6], current_byte[6:8])

            pixel = pix[curwidth, curheight]  # gets the current pixel

            # initialize RGB values
            red, green, blue = 0, 0, 0
            try:
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]
            except TypeError as e:
                print("Error {}: {}".format(e, pixel))

            '''
            encodes a byte into a pixel's colors
            1) first 3 bits encoded into red's least significant bits
            2) next 3 bits encoded into green's least significant bits
            3) last 2 bits encoded into blue's least significant bits

            max change of 7 to color component
            '''
            red = format(red, '08b')
            red = red[0:5] + bits[0]
            red = int(red, 2)

            green = format(green, '08b')
            green = green[0:5] + bits[1]
            green = int(green, 2)

            blue = format(blue, '08b')
            blue = blue[0:6] + bits[2]
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
        downlink = self.cons.upload(output_image)

        return downlink

    def decodeImageFromURL(self, file_id):
        """
        The decodeImageFromURL method retrieves an image from a url,
        and extracts a message from the image. The image needs to have
        been encoded using the Steg.encode(msg) method.
        This method takes a url as a string.
        This method returns the decoded message as a bytearray.
        """
        url = self.cons.downloadImage(file_id)
        if self.proxy:  # if the application is using proxies
            # open a url using the proxies
            r = requests.get(url, proxies=self.proxy)
        else:  # if the application is not using proxies
            r = requests.get(url)  # open the url without proxies

        # if the url was successfully opened
        if r.status_code == requests.codes.ok:
            # decode the image found in the url
            return self.decode(BytesIO(r.content))
        else:  # if the url was not successfully opened
            # raise an exception that shows the faulty url
            raise FileNotFoundError("Could not retrieve image at {}.".format(url))

    def decode(self, img):
        """
        The decode method decodes the message from an image.
        This method takes an image as a BytesIO object and returns a bytearray
        object containing the decoded data.
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
                # format adds padding
                red = format(pixels[w, h][0], '08b')
                green = format(pixels[w, h][1], '08b')
                blue = format(pixels[w, h][2], '08b')

                # assemble the message
                decodeMsg = red[-3:] + green[-3:] + blue[-2:]

                # see if the eof bytes have been found
                # subtract 8 for current byte
                special_ending = msg[-(len(SPECIAL_EOF_BITS) - 8):] + decodeMsg

                if special_ending == SPECIAL_EOF_BITS:
                    msg += decodeMsg

                    # remove EOF signature
                    msg = msg[:-len(SPECIAL_EOF_BITS)]

                    length_of_url = len(NEXT_IMAGE_BITS) + self.URL_LENGTH_IN_BINARY

                    msg_array = bytearray()
                    # URL ID found
                    if msg[-length_of_url:-self.URL_LENGTH_IN_BINARY] == NEXT_IMAGE_BITS:
                        url_bin = msg[-self.URL_LENGTH_IN_BINARY:]

                        # converts binary string of url to ascii
                        url = int(url_bin, 2)
                        url = url.to_bytes((url.bit_length() +
                                            7) // 8, 'big').decode()

                        # remove URL and identifier
                        msg = msg[:-length_of_url]
                        msg_array = bytearray.fromhex('%08X' % int(msg, 2))

                        # append next image's message
                        next_msg = self.decodeImageFromURL(url)

                        msg_array += next_msg
                    else:
                        msg_array = bytearray.fromhex('%08X' % int(msg, 2))

                    return msg_array

                else:
                    msg += decodeMsg

        print("Something messed up... " + msg[-50:])
        return bytearray()

if __name__ == '__main__':
    # python3 -m src.Image_Manipulation.lsbsteg [file]

    import sys
    from src.Web_Connection import api_cons
    from src.Web_Connection import proxy_list
    stego = Steg(proxy_list.proxies, api_cons.SendSpace(proxy_list.proxies))

    file_name = sys.argv[1]
    print("Opening {}.".format(file_name))
    my_msg = bytearray()
    try:
        msg_file = open(file_name, 'rb')
        my_msg = bytearray(msg_file.read())
        msg_file.close()
    except FileNotFoundError:
        print("File not found, encoding \"{}\".".format(file_name))
        my_msg = bytearray(file_name.encode())

    print("Encoding file.")
    # TODO:// adding EOF to local my_msg var...why?
    download_url = stego.encode(my_msg)
    print("Encoded image: {}.".format(download_url))
    print("Decoding file.")
    decoded_file = stego.decodeImageFromURL(download_url)

    print("Writing output to orig.txt and dec.txt")
    with open("orig.txt", 'w') as orig_file, open("dec.txt", 'w') as dec_file:
        orig_file.write(str(my_msg))
        dec_file.write(str(decoded_file))

    # shouldn't need [:], something wrong with encode()
    if decoded_file == my_msg[:-len(SPECIAL_EOF)]:
        print("Encode and decode success!")
    else:
        print("Decode different than encoded data, FAIL.")
