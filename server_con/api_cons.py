import config
import requests # connect to server
from bs4 import BeautifulSoup # parse XML response
import pycurl # send post request
from io import BytesIO # read post response 
from os.path import realpath # get absolute path for image upload TODO:// remove, use cat API

class SendSpace(object):
  # class variables
  sendspace_url = 'http://api.sendspace.com/rest/'
  api_key = config.key

  def __init__(self, file):
    self.file = file
  
  ###
  ### Connect to SendSpace as anonymous user
  ###
  def connect(self):
    connect_data = {'method':'anonymous.uploadGetInfo', 'api_key':self.api_key, 'api_version':1.0}
    # get request to get info for anonymous upload
    con_r = requests.get(self.sendspace_url, params=connect_data)
    # error handling
    if con_r.status_code != 200:
    	# not OK connection
    	print('Status: ', con_r.status_code, 'Problem with the request. Exiting.')
    	exit()
    else: return con_r
  ###
  ### parse response as xml
  ###
  def parseXML(self, xml):
    return BeautifulSoup(xml, "lxml")

  ###
  ### Send file for upload
  ###
  def uploadImage(self, xml_data):
    # prep image for upload

    # TODO:// generate image from cat API
    filename = realpath('duca2.jpg')

    # prep xml post request 
    #connection response: url=[upload url], progress_url=[real-time progress information]
    #                     max_file_size=[max size curent user can upload], upload_identifier=[], extra_info=[]
    upl_url = xml_data["url"]
    upl_progress_url = xml_data["progress_url"]
    upl_max_file_size = int(xml_data["max_file_size"])
    upl_upload_identifier = xml_data["upload_identifier"]
    upl_extra_info = xml_data["extra_info"]
    #post_data['MAX_FILE_SIZE'] = con_max_file_size # already in url
    #post_data['UPLOAD_IDENTIFIER'] = con_upload_identifier # already in url
    post_data = [
      ('extra_info', upl_extra_info),
      ('userfile', (pycurl.FORM_FILE, filename,)),
    ]


    c = pycurl.Curl()
    c.setopt(c.URL, upl_url)
    c.setopt(c.HTTPPOST, post_data)
    b = BytesIO()
    c.setopt(pycurl.WRITEDATA, b)
    c.perform()
    c.close()

    post_r = b.getvalue().decode('utf-8')

    # post response: download_url, delete_url, file_id
    return post_r

sendSpace = SendSpace("")
con_r = sendSpace.connect()
parsed_con_r = sendSpace.parseXML(con_r.text).result.upload
upl_r = sendSpace.uploadImage(parsed_con_r)
parsed_upl_r = sendSpace.parseXML(upl_r)

download_url = parsed_upl_r.download_url.string
delete_url = parsed_upl_r.delete_url.string

print(download_url)
