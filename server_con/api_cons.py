import config
import requests # connect to server
from bs4 import BeautifulSoup # parse XML response
import pycurl # send post request
from io import BytesIO # read post response 
from os.path import realpath # get absolute path for image upload TODO:// remove, use cat API

sendspace_url = 'http://api.sendspace.com/rest/'
api_key = config.key

###
### Connect to SendSpace as anonymous user
###

connect_data = {'method':'anonymous.uploadGetInfo', 'api_key':api_key, 'api_version':1.0}
# get request to get info for anonymous upload
con_r = requests.get(sendspace_url, params=connect_data)
# error handling
if con_r.status_code != 200:
	# not OK connection
	print('Status: ', con_r.status_code, 'Problem with the request. Exiting.')
	exit()
###
### parse response as xml
###

xml_con=BeautifulSoup(con_r.text, "lxml").result.upload

#connection response: url=[upload url], progress_url=[real-time progress information]
#                     max_file_size=[max size curent user can upload], upload_identifier=[], extra_info=[]
con_url = xml_con["url"]
print(con_url)
con_progress_url = xml_con["progress_url"]
con_max_file_size = int(xml_con["max_file_size"])
con_upload_identifier = xml_con["upload_identifier"]
con_extra_info = xml_con["extra_info"]

###
### Send file for upload
###
# prep image for upload

# TODO:// generate image from cat API
filename = realpath('duca2.jpg')

# prep xml post request 

"""<form method="post" action="[url value received in response]" enctype="multipart/form-data">
      <!-- MUST FIELDS -->
      <input type="hidden" name="MAX_FILE_SIZE" value="[max_file_size value received in response]">
      <input type="hidden" name="UPLOAD_IDENTIFIER" value="[upload_identifier value received in response]">
      <input type="hidden" name="extra_info" value="[extra_info value received in response]">
      <input type="file" name="userfile">
    </form>"""
#post_data['MAX_FILE_SIZE'] = con_max_file_size # already in url
#post_data['UPLOAD_IDENTIFIER'] = con_upload_identifier # already in url
post_data = [
  ('extra_info', con_extra_info),
  ('userfile', (pycurl.FORM_FILE, filename,)),
]


c = pycurl.Curl()
c.setopt(c.URL, con_url)
c.setopt(c.HTTPPOST, post_data)
b = BytesIO()
c.setopt(pycurl.WRITEDATA, b)
c.perform()
c.close()

post_r = b.getvalue().decode('utf-8')

# post response: download_url, delete_url, file_id
print(post_r)

