#!/usr/bin/env python3

"""
The `api_cons` module creates an anonymous connection to a given social media
file hosting website and provides connection, upload image, and download image
parameters.
"""

from bs4 import BeautifulSoup  # parse XML response
from PIL import Image
from .API_Keys import config
import platform
import subprocess
import requests  # GET and POST requests
from io import BytesIO
if platform.system() == 'Linux':
    torEnabled = subprocess.check_output(['ps',
                                         'aux']).decode().find('/usr/bin/tor')
    if torEnabled > -1:
        import socks
        import socket
        print("Using tor, rerouting connection")
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket


class SendSpace(object):
    """
    The SendSpace class is creates a connection to the SendSpace file
    sharing website.
    """
    sendspace_url = 'http://api.sendspace.com/rest/'  # REST API url (v1.1)

    def __init__(self, proxy):
        """
        The SendSpace constructor.
        """
        self.api_key = config.sendSpaceKey
        self.proxy = proxy
        self.url_size = 6  # length of download URL returned by sendspace
        self.count = 0

    def getRequest(self, _url, _params):
        with requests.Session() as s:
            if self.proxy:
                try:  # #### GET REQUEST WITH PROXY
                    r = s.get(_url,
                              params=_params,
                              proxies=self.proxy,
                              timeout=5)
                except(requests.exceptions.RequestException) as e:
                    if self.count > 5:
                        self.count = 0
                        print("Too many connection failures, " +
                              "proxy or sendspace may be down: {}".format(e))
                        raise RuntimeError("Error connecting to " +
                                           " sendspace from the " +
                                           "proxy (GET)") from e

                    else:
                        print("Error connecting to sendspace" +
                              " from the proxy, retrying...")
                        self.count += 1
                        return self.getRequest(_url, _params)
            else:
                try:  # #### GET REQUEST NO PROXY
                    r = s.get(_url,
                              params=_params,
                              timeout=5)
                except(requests.exceptions.RequestException) as e:
                    if self.count > 5:
                        self.count = 0
                        print("Too many connection failures, " +
                              "sendspace may be down: {}".format(e))
                        raise RuntimeError("Error connecting to " +
                                           "sendspace (GET)") from e

                    else:
                        print("Error connecting to sendspace, retrying...")
                        self.count += 1
                        return self.getRequest(_url, _params)
            if r.status_code == requests.codes.ok:
                return r
            else:
                print("Invalid response code " + str(r.status_code) +
                      "\n" + r.text)

    def postRequest(self, _url, _data, _files):
        with requests.Session() as s:
            if self.proxy:
                try:  # #### POST REQUEST WITH PROXY
                    return s.post(_url,
                                  data=_data,
                                  files=_files,
                                  proxies=self.proxy,
                                  timeout=5)
                except(requests.exceptions.RequestException) as e:
                    if self.count > 5:
                        self.count = 0
                        print("Too many connection failures, " +
                              "proxy or sendspace may be down: {}".format(e))
                        raise RuntimeError("Error posting to " +
                                           "sendspace from the " +
                                           "proxy (POST)") from e

                    else:
                        print("Error posting image to sendspace from the " +
                              "proxy, retrying...")
                        self.count += 1
                        return self.postRequest(_url, _data, _files)

            else:  # #### POST REQUEST NO PROXY
                try:
                    return s.post(_url,
                                  data=_data,
                                  files=_files,
                                  timeout=5)
                except(requests.exceptions.RequestException) as e:
                    if self.count > 5:
                        self.count = 0
                        print("Too many connection failures, " +
                              "sendspace may be down: {}".format(e))
                        raise RuntimeError("Error posting to " +
                                           "sendspace") from e

                    else:
                        print("Error posting image to sendspace, retrying...")
                        self.count += 1
                        return self.postRequest(_url, _data, _files)

    def upload(self, img):
        """
        The upload method uploads an image to SendSpace.
        This method takes an image as a BytesIO object.
        This method returns the download and delete urls as a tuple.
        """
        # create a connection to sendspace
        (upl_url, upl_max_size, upl_id, upl_extra_info) = self.connect()
        # return the (download_url, delete_url) of the image
        return self.uploadImage(upl_url, upl_max_size,
                                upl_id, upl_extra_info, img)

    def connect(self):
        """
        The connect method creates an anonymous connection to SendSpace.
        The connection uses the sendspace API (1.1) and does not require
        authentication or login.
        This method requires no parameters.
        This method returns the URL and the extra info needed for uploading an
        image to SendSpace.
        """
        # parameters for anonymous upload info
        connect_params = {
            'method': 'anonymous.uploadGetInfo',
            'api_key': self.api_key,
            'api_version': 1.1}

        # get request to get info for anonymous upload
        try:
            r = self.getRequest(self.sendspace_url, connect_params)
        except (RuntimeError) as e:
            raise RuntimeError("Error getting info for anonymous " +
                               "upload.") from e

        if r.status_code == requests.codes.ok:
            # parse the response from the connection to sendspace
            parsed_con_r = self.parseXML(r.text)
            # try to parse the response
            try:
                upl_url = parsed_con_r.result.upload["url"]
                upl_max_size = parsed_con_r.result.upload["max_file_size"]
                upl_id = parsed_con_r.result.upload["upload_identifier"]
                upl_extra_info = parsed_con_r.result.upload["extra_info"]
            except ValueError as e:
                # catch errors if response cannot be parsed
                print("Error parsing connection response.\n" +
                      e.value + "\n" + r.text)
        else:
            print("Invalid response code " + str(r.status_code) +
                  "\n" + r.text)
        return (upl_url, upl_max_size, upl_id, upl_extra_info)

    # Parse response as xml
    def parseXML(self, xml):
        """
        This method parses XML data with the BeautifulSoup module.
        """
        return BeautifulSoup(xml, "xml")

    def uploadImage(self, upl_url, max_size, upl_id, upl_extra_info, img):
        """
        The uploadImage method sends an image file for upload to SendSpace.
        This method requires the upload url and extra info from the SendSpace
        connection and the image (BytesIO object) as parameters.
        This method returns the direct download URL and delete URL of the image
        as a tuple.
        """
        # parameters for anonymous image upload
        post_params = {
                        'MAX_FILE_SIZE': max_size,
                        'UPLOAD_IDENTIFIER': upl_id,
                        'extra_info': upl_extra_info
                        }
        # convert the BytesIO img object to a viable file parameter
        # filename for unnamed image is userfile
        files = {'userfile': img.getvalue()}
        # POST request with the parameters for upload to SendSpace
        try:
            r = self.postRequest(upl_url, post_params, files)
        except (RuntimeError) as e:
            raise RuntimeError("Error uploading image to sendspace.") from e

        # TODO:// FIX MaxRetryError, ConnectionError
        # (Caused by ProxyError('Cannot connect to proxy.',
        # BrokenPipeError(32, 'Broken pipe')))
        # A Byte Steam is not closed properly.
        # r = requests.post(upl_url, data=post_params, files=files)

        # parse the response from the upload post request
        parsed_upl_r = self.parseXML(r.text)
        # try to parse the response
        try:
            download_url = parsed_upl_r.download_url.string[-6:]
            delete_url = parsed_upl_r.delete_url.string
        except (ValueError, AttributeError) as e:
            print("Error parsing URLs from response. Retrying...")
            return self.upload(img)

        return download_url

    # Retrieve the direct download URL from the download URL
    def downloadImage(self, file_id):
        """
        The downloadImage method retrieves the direct download URL from the
        download url returned by SendSpace.
        This method take the download url returned by uploadImage as a
        parameter.
        This method returns image as a BytesIO object.
        """
        # check if using full url or partial
        url = "https://www.sendspace.com/file/{}".format(file_id) if len(file_id) == 6 else file_id

        try:
            r = self.getRequest(url, {})  # GET request for image
        except (RuntimeError) as e:
            raise RuntimeError("Error getting download URL for image from " +
                               "sendspace.") from e

        # the download image retrieved from the uploadImage method does not
        # return a direct download URL. This parses the request to download
        # for the direct download URL.
        dd_url = BeautifulSoup(r.text, "lxml").find("a", {"id": "download_button"})['href']

        # download the actual image from the dd_url
        try:
            return BytesIO(self.getRequest(dd_url, {}).content)
        except (RuntimeError) as e:
            raise RuntimeError("Error downloading the image from " +
                               "sendspace.") from e

if __name__ == '__main__':  # running file directly
    """
    This should get an image from genImage, upload the image, and download the
    image.
    """
    from webStegFS.Web_Connection import proxy_list
    s = SendSpace(proxy_list.proxies)
    from webStegFS.Image_Manipulation import genImage
    print("Testing Sendspace...generating img for upload")
    try:
        img = genImage.genCatImage()
    except (RuntimeError) as e:
        print("No cats available :( {}".format(e))
    url = s.upload(img)
    print("Upload success: {}".format(url))
    img_down = s.downloadImage(url)
    print("Download success, opening image")
    # Image.open(img_down).show()
