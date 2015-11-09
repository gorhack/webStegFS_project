from bs4 import BeautifulSoup # parse XML response
import pycurl # send requests
from urllib.parse import urlencode # encode parameters for get request
from urllib.request import urlopen
from io import BytesIO # read post response 
import os # TODO:// delete temp image
import requests # GET requests
try: # needed if running directly, otherwise main imports
  from API_Keys import config
except:
  pass

class SendSpace(object):
  # class variables
  sendspace_url = 'http://api.sendspace.com/rest/'
  #image_data = {}

  def __init__(self, key):
    self.api_key = key

  ###
  ### User facing upload
  ###
  def upload(self):
    (upl_url, upl_extra_info) = self.connect()
    return self.uploadImage(upl_url, upl_extra_info)
  
  ###
  ### Connect to SendSpace as anonymous user
  ###
  def connect(self):
    # parameters for anonymous upload info
    connect_params = {'method':'anonymous.uploadGetInfo', 'api_key':self.api_key, 'api_version':1.0}
    
    # get request to get info for anonymous upload
    r = requests.get(self.sendspace_url, params=connect_params)
    parsed_con_r = self.parseXML(r.text)
    try:
      upl_url = parsed_con_r.result.upload["url"]
      upl_extra_info = parsed_con_r.result.upload["extra_info"]
    except Exception as e:
      print("Error parsing connection response.\n" + r.text)
    
    return (upl_url, upl_extra_info)
  
  ###
  ### parse response as xml
  ###
  def parseXML(self, xml):
    return BeautifulSoup(xml, "lxml")

  ###
  ### Send file for upload
  ###
  def uploadImage(self, upl_url, upl_extra_info):
    # initialize post request parameter values or exit
    encodedImageName = 'tmp.png'

    # parameters for anonymous image upload
    post_params = {'extra_info':upl_extra_info} 
    files = {'userfile':open(encodedImageName, 'rb')} #image} #requests.get('http://thecatapi.com/api/images/get?format=src&type=png').content}
    r = requests.post(upl_url, data=post_params, files=files)

    # # delete image file
    if os.path.exists(encodedImageName):
      os.remove(encodedImageName)
    else:
      print("Cannot remove tmp image")

    parsed_upl_r = self.parseXML(r.text)
      
    download_url=''
    delete_url=''
    try:
      download_url = self.downloadImage(parsed_upl_r.download_url.string)
      delete_url = parsed_upl_r.delete_url.string
    except Exception as e:
      print("Error parsing upload response.\n" + r.text)
      exit()
    
    return (download_url, delete_url)

  def downloadImage(self, file_id):
    r = requests.get(file_id)
    return BeautifulSoup(r.text, "lxml").find("a", {"id": "download_button"})['href']
    
### automatically generate an image and upload
# sendSpace = SendSpace(config.sendSpaceKey)
# (upl_url, upl_extra_info) = sendSpace.connect()
# upl_r = sendSpace.uploadImage(image, upl_url, upl_extra_info)
# print(upl_r)
