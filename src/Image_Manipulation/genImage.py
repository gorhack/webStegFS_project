#!/usr/bin/env python3

import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket

import requests  # requests module for getting images
from io import BytesIO  # return type of genImage

"""@package genImage

Documentation for the genImage module.
The genImage module returns an image on request as a BytesIO object.
"""


def genCatImage():
    """
    The genCatImage function returns an image from The Cat API.
    This function does not take any parameters.
    This function returns a BytesIO object.
    """
    r = requests.get('http://thecatapi.com/api/images/get?format=src&type=png')
    if r.status_code == requests.codes.ok:  # image returned OK
        img = BytesIO(r.content)  # create BytesIO object from the request
        r.close()  # close the get request
        return img  # return the BytesIO object
    else:  # request failed to retrieve the image
        r.close()  # close the get request
        return genCatImage()  # try to return another image
