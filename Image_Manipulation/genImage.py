import requests
from io import BytesIO


def genCatImage():
    r = requests.get('http://thecatapi.com/api/images/get?format=src&type=png')
    if r.status_code == requests.codes.ok:
        img = BytesIO(r.content)
        r.close()
        return img
    else:
        r.close()
        return genCatImage()
