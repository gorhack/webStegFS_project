#!/usr/bin/env python3

from bs4 import BeautifulSoup  # parse XML response
import requests  # GET and POST requests
from PIL import Image
try:
    from Web_Connection import proxy_list
except:
    import proxy_list  # running file directly

"""@package api_cons

Documentation for the api_cons module.
"""

proxies = proxy_list.proxies


class SendSpace(object):
    """
    The SendSpace class is creates a connection to the SendSpace file
    sharing website.
    """
    sendspace_url = 'http://api.sendspace.com/rest/'  # REST API url (v1.1)

    def __init__(self, key, proxy):
        """
        The SendSpace constructor.
        """
        self.api_key = key
        self.proxy = proxy

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
        if self.proxy:
            r = requests.get(self.sendspace_url,
                             params=connect_params,
                             proxies=proxies)
        else:
            r = requests.get(self.sendspace_url, params=connect_params)
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
        r.close()
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
        files = {'userfile': img.getvalue()}
        # POST request with the parameters for upload to SendSpace
        if self.proxy:
            r = requests.post(upl_url, data=post_params,
                              files=files, proxies=proxies)
            # TODO:// FIX MaxRetryError, ConnectionError
            # (Caused by ProxyError('Cannot connect to proxy.',
            # BrokenPipeError(32, 'Broken pipe')))
            # A Byte Steam is not closed properly.

        else:
            r = requests.post(upl_url, data=post_params, files=files)

        if r.status_code == requests.codes.ok:
            # parse the response from the upload post request
            parsed_upl_r = self.parseXML(r.text)
            # try to parse the response
            try:
                download_url = parsed_upl_r.download_url.string[-6:]
                delete_url = parsed_upl_r.delete_url.string
            except ValueError as e:
                print("Error parsing URLs from response.\n" + e.value + "\n" + r.text)
        else:
            print("Invalid response code " + r.status_code + "\n" + r.text)
        img.close()  # close the BytesIO Image object
        r.close()  # close initial POST request
        return (download_url, delete_url)

    # Retrieve the direct download URL from the download URL
    def downloadImage(self, file_id):
        """
        The downloadImage method retrieves the direct download URL from the
        download url returned by SendSpace.
        This method take the download url returned by uploadImage as a
        parameter.
        This method returns the direct download url.
        """
        # check if using full url or partial
        url = "https://www.sendspace.com/file/{}".format(file_id) if len(file_id) == 6 else file_id
        if self.proxy:  # GET request for image
            r = requests.get(url, proxies=proxies)
        else:
            r = requests.get(url)
        # the download image retrieved from the uploadImage method does not
        # return a direct download URL. This parses the request to download
        # for the direct download URL.
        dd_url = BeautifulSoup(r.text, "lxml").find("a", {"id": "download_button"})['href']
        r.close()  # close the GET request.
        return dd_url

if __name__ == '__main__':  # running file directly
    """
    for testing purposes only!
    """
    from API_Keys import config  # import configuration file
    s = SendSpace(config.sendSpaceKey)
    print(s.downloadImage("https://www.sendspace.com/file/thuzbn"))
