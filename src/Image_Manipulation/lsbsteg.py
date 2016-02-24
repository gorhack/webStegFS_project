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

# URLLIB->
NEXT_IMAGE = '0101010101010010010011000100110001001001010000100010110100111110'
NEXT_IMAGE_HEX = bytearray.fromhex('%08X' % int(NEXT_IMAGE, 2))

URL_LENGTH_IN_BINARY = 48  # 6 characters
# END_OF_FILE
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
        self.cons = Console('sendspace', 'lsbsteg', 'covertMount', '', 'noproxy', False)

    def createImage():
        img_file = open("S1940016.PNG", 'rb')
        # img = Image.open(img_file)  # image would be created in steg from cats
        # img_file.close()
        img = BytesIO(img_file.read())
        return img

    # prepare message and image for encoding
    # returns url
    def encode(self, message):
        """
        Encodes up to 1 byte of data per pixel.
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
            The prepare message function splits the message based on the maximum
            size available to the steg function based on the number of pixels.
            """
            print("preparing message")
            return msg[:-size_available], msg[-size_available:]

        msg = message

        # append EOF to image
        msg.extend(SPECIAL_EOF_HEX)

        # create image
        image = prepareNewImage()
        # converts BytesIO to Image
        #img.seek(0)
        #image = Image.open(img)
        #img.close()
        width, height = image.size

        print("bytes in message: {}".format(len(msg)))
        print("pixels in image:  {}".format(height * width))

        # prepare the message
        rest, msg = prepareMessage(msg, width * height)
        url = self.encodeSteg(msg, image)

        # encode rest of message if necessary
        if len(rest) > 0:
            rest.extend(NEXT_IMAGE_HEX)
            rest.extend(str.encode(url))
            url = self.encode(rest)

        return url

    # takes msg as bytearray and image as BytesIO
    # returns url to image as string
    def encodeSteg(self, msg, image):
        pix = image.load()

        curwidth = 0
        curheight = 0

        for byte in msg:
            # print("byte before {} {}: {}".format(curwidth, curheight, str(byte)))

            current_byte = format(byte, '#010b')[2:]  # keeps 0s in formatting
            # splits byte into 3 groups ('111', '111', '11') for encoding to pixels
            bits = (current_byte[0:3], current_byte[3:6], current_byte[6:8])

            # print(bits)

            pixel = pix[curwidth, curheight]  # gets the current pixel
            #print(pixel)  # having lots of issues...
            # TypeError: 'int' object is not subscriptable
            #
            # splits pixel into RGB values
            red, green, blue = 0, 0, 0
            try:
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]
            except Exception as e:
                print("pixels fucked up")
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

            pix[curwidth, curheight] = (red, green, blue)  # set current pixel

            # go to next pixel
            curwidth += 1
            if (curwidth >= image.width):
                curwidth = 0
                curheight += 1

        image_bytes = BytesIO(image.tobytes())

        output_image = BytesIO()
        image.save(output_image, format="PNG")
        image.close()
        #print(image_bytes.getvalue()[-50:])
        print("sending to upload")
        contents, downlink = self.cons.uploadfile(output_image)
        contents.close()
        print(downlink)
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
        img.seek(0)
        image = Image.open(img)
        #image = img
        pixels = image.load()

        msg = ''

        for h in range(image.height):
            for w in range(image.width):
                red = pixels[w, h][0]
                green = pixels[w, h][1]
                blue = pixels[w, h][2]

                red = format(red, '#010b')[2:]
                green = format(green, '#010b')[2:]
                blue = format(blue, '#010b')[2:]

                decodeMsg = red[-3:] + green[-3:] + blue[-2:]
                # print("decodedMsg {} {}: {}".format(w, h, decodeMsg))

                # see if the eof bytes have been found, subtract 8 for current byte
                special_ending = msg[-(len(SPECIAL_EOF) - 8):] + decodeMsg


                # print(ending)

                if special_ending == SPECIAL_EOF:
                    msg += decodeMsg
                    print("reached end of image")
                    #print(msg[-50:])

                    # remove EOF signature
                    msg = msg[:-len(SPECIAL_EOF)]
                    #print(msg[-50:])

                    length_of_url = len(NEXT_IMAGE) + URL_LENGTH_IN_BINARY

                    if msg[-length_of_url:-URL_LENGTH_IN_BINARY] == NEXT_IMAGE:
                        print("found another image to decode")
                        url_bin = msg[-URL_LENGTH_IN_BINARY:]

                        # converts binary string to ascii
                        url = int(url_bin, 2)
                        url = url.to_bytes((url.bit_length() + 7) // 8, 'big').decode()

                        # remove URL
                        msg = msg[:-length_of_url]

                        # append next image's message
                        next_msg = self.decodeImageFromURL(url)

                        msg += next_msg
                    # convert to BytesIO object
                    # msg_ba = bytearray.fromhex('%08X' % int(msg, 2))
                    # return BytesIO(msg_ba)

                    return msg
                else:
                    msg += decodeMsg

        return ("Something messed up... " + msg[-50:])

    def bytesarray2BytesIO(self, data):
        return BytesIO(data)
# tmp_image = createImage()
# encoded_image = encodeSteg(msg, tmp_image)
# # tmp_image.close()

# output_image = BytesIO()
# encoded_image.save(output_image, format="PNG")
# # encoded_image.close()
# output_image.seek(0)
# showEncodedImage = Image.open(output_image)
# #showEncodedImage.show()

# # print(output_image.getvalue()[50:])
# out_msg = decodeSteg(output_image)
# #out_msg.seek(0)
# #showImage = Image.open(out_msg)
# #showImage.show()
# print(out_msg.getvalue()[-50:])

# # output_image.close()
