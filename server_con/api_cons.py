import config # api keys
from bs4 import BeautifulSoup # parse XML response
import pycurl # send requests
from urllib.parse import urlencode # encode parameters for get request
from urllib.request import urlopen
from io import BytesIO # read post response 
import os # TODO:// delete temp image

class SendSpace(object):
  # class variables
  sendspace_url = 'http://api.sendspace.com/rest/'
  api_key = config.key
  image_data = {}
  def __init__(self, file):
    self.file = file
  
  ###
  ### Connect to SendSpace as anonymous user
  ###
  def connect(self):
    # parameters for anonymous upload info
    connect_params = {'method':'anonymous.uploadGetInfo', 'api_key':self.api_key, 'api_version':1.0}
    
    # get request to get info for anonymous upload
    c = pycurl.Curl()
    c.setopt(c.URL, self.sendspace_url + '?' + urlencode(connect_params))
    c.setopt(c.HTTPGET, 1)
    b = BytesIO()
    c.setopt(pycurl.WRITEDATA, b)
    c.perform()
    response_code = c.getinfo(pycurl.HTTP_CODE)
    if (response_code != 200): 
      print("Error getting info for upload: " + response_code)
      c.close()
      exit()
    c.close()

    con_r = b.getvalue().decode('utf-8')
    return con_r
  
  ###
  ### parse response as xml
  ###
  def parseXML(self, xml):
    return BeautifulSoup(xml, "lxml")

  ###
  ### Send file for upload
  ###
  def uploadImage(self, xml_data):
    # initialize post request parameter values or exit
    try:
      upl_url = xml_data.result.upload["url"]
      upl_progress_url = xml_data.result.upload["progress_url"]
      upl_max_file_size = int(xml_data.result.upload["max_file_size"])
      upl_upload_identifier = xml_data.result.upload["upload_identifier"]
      upl_extra_info = xml_data.result.upload["extra_info"]
      #post_data['MAX_FILE_SIZE'] = con_max_file_size # already in url
      #post_data['UPLOAD_IDENTIFIER'] = con_upload_identifier # already in url
    except Exception as e:
        try: 
          print("Error parsing info for upload: " + str(xml_data.body.error))
          exit()
        except Exception as e2:
          print("Error: " + str(e) + ' ' + str(e2))
          exit()
    # generate image from cat API: http://thecatapi.com
    fd = urlopen('http://thecatapi.com/api/images/get?format=src&type=jpg')

    f = open('image.jpg', 'wb') # TODO:// currently saves image to local dir. use only in memory. 
    f.write(fd.read())
    f.close()
        
    # parameters for anonymous image upload
    post_params = [
      ('extra_info', upl_extra_info),
      ('userfile', (pycurl.FORM_FILE, 'image.jpg',)),
    ]

    # post request to upload image
    c = pycurl.Curl()
    c.setopt(c.URL, upl_url)
    c.setopt(c.HTTPPOST, post_params)
    b = BytesIO()
    c.setopt(pycurl.WRITEDATA, b)
    c.perform()
    c.close()

    # delete image file
    if os.path.exists('image.jpg'):
      os.remove('image.jpg')
    else:
      print("Cannot remove tmp image: image.jpg")

    return b.getvalue().decode('utf-8')

sendSpace = SendSpace("") # TODO:// send filename to encrypt inside image
try:
  con_r = sendSpace.connect()
  parsed_con_r = sendSpace.parseXML(con_r)
  upl_r = sendSpace.uploadImage(parsed_con_r)
  parsed_upl_r = sendSpace.parseXML(upl_r)

  try:
    sendSpace.image_data['download_url'] = parsed_upl_r.download_url.string
    sendSpace.image_data['delete_url'] = parsed_upl_r.delete_url.string
  except Exception as e:
    try: 
      print("Error parsing info for upload: " + str(parsed_upl_r.body))
      exit()
    except Exception as e2:
      print("Error: " + str(e) + ' ' + str(e2))
      exit()
  print(sendSpace.image_data['download_url'])
except Exception as e: 
  print("Cannot upload at this time: " + str(e))
