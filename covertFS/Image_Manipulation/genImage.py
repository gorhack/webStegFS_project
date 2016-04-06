#!/usr/bin/env python3

"""
The `genImage` module returns an image on request as a `BytesIO` object.
"""

import requests  # requests module for getting images
from io import BytesIO  # return type of genImage


def genCatImage():
    """
    The genCatImage function returns an image from The Cat API.
    This function does not take any parameters.
    This function returns a BytesIO object.
    """
    r = requests.get('http://thecatapi.com/api/images/get?format=src&type=png')
    if r.status_code == requests.codes.ok:  # image returned OK
        # DEBUG ONLY TO COMPARE ORIG IMG TO ENCODED IMG
        # with open("image.png", 'wb') as f:
        #     for chunk in r:
        #         f.write(chunk)
        img = BytesIO(r.content)  # create BytesIO object from the request
        r.close()  # close the get request
        return img  # return the BytesIO object
    else:  # request failed to retrieve the image
        r.close()  # close the get request
        return genCatImage()  # try to return another image

if __name__ == '__main__':
    """
    Opens a random image
    """
    from PIL import Image
    print("Opening image")
    Image.open(genCatImage()).show()
    print("Success")
