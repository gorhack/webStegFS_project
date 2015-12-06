from bs4 import BeautifulSoup  # parse XML response
import requests  # GET and POST requests
from PIL import Image
from Web_Connection import proxy_list

proxies = proxy_list.proxies


class SendSpace(object):
    sendspace_url = 'http://api.sendspace.com/rest/'

    def __init__(self, key, proxy=True):
        self.api_key = key
        self.proxy = proxy

    # User facing upload
    def upload(self, img):
        (upl_url, upl_extra_info) = self.connect()
        return self.uploadImage(upl_url, upl_extra_info, img)

    # Connect to SendSpace as anonymous user
    # Returns the URL and the extra info needed for uploading an image
    def connect(self):
        # parameters for anonymous upload info
        connect_params = {
            'method': 'anonymous.uploadGetInfo',
            'api_key': self.api_key,
            'api_version': 1.0}

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
                upl_extra_info = parsed_con_r.result.upload["extra_info"]
            except ValueError as e:
                print("Error parsing connection response.\
                    \n" + e.value + "\n" + r.text)
                exit()
        else:
            print("Invalid response code \
                " + str(r.status_code) + "\n" + r.text)
            exit()
        r.close()
        return (upl_url, upl_extra_info)

    # Parse response as xml
    def parseXML(self, xml):
        return BeautifulSoup(xml, "xml")

    # Send file for upload
    # Returns the direct download URL and delete URL
    def uploadImage(self, upl_url, upl_extra_info, img):
        # parameters for anonymous image upload
        post_params = {'extra_info': upl_extra_info}
        files = {'userfile': img.getvalue()}
        if self.proxy:
            r = requests.post(upl_url, data=post_params,
                              files=files, proxies=proxies)
        else:
            r = requests.post(upl_url, data=post_params, files=files)

        if r.status_code == requests.codes.ok:
            # parse the response from the upload post request
            parsed_upl_r = self.parseXML(r.text)
            # try to parse the response
            try:
                download_url = parsed_upl_r.download_url.string
                delete_url = parsed_upl_r.delete_url.string
            except ValueError as e:
                print("Error parsing URLs from response.\
                    \n" + e.value + "\n" + r.text)
                exit()
        else:
            print("Invalid response code " + r.status_code + "\n" + r.text)
            exit()
        r.close()
        return (download_url, delete_url)

    # Retrieve the direct download URL from the download URL
    def downloadImage(self, file_id):
        # check if using full url or partial
        url = "https://www.sendspace.com/file/{}".format(file_id) if len(file_id) == 6 else file_id
        if self.proxy:
            r = requests.get(url, proxies=proxies)
        else:
            r = requests.get(url)
        dd_url = BeautifulSoup(r.text, "lxml").find("a", {"id": "download_button"})['href']
        r.close()
        return dd_url

if __name__ == '__main__':
    from API_Keys import config
    s = SendSpace(config.sendSpaceKey)
    print(s.downloadImage("https://www.sendspace.com/file/thuzbn"))
