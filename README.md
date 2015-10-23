# covertFS
It's covert and stuff. 
##About: 
  A web-based application that allows users to covertly share files through social media sites while maintaining plausible deniability for both the user(s) and the social media site. 

##Setup: 
  Covert FS is written exclusively in Python 3 due to the vast modules and libraries that support our goals. 
  
  - Dependencies:
    - python3, pip3 `pip3 install -r utls/requirements.txt`
<<<<<<< HEAD
    - config.py file in /Web Connection/ containing `key='API KEY GOES HERE'`
=======
    - config.py file in /Web\ Connection/ containing `key='API KEY GOES HERE'`
>>>>>>> 857ceb0c8608db50a29b263690e12b637cd3e0e8


##Sprints: 

###Sprint 1: Knowledge aquisition
Sprint broken into three sub-goals: 
  1. Implement basic steg module to encode and decode an image in Python 
    - `$ python3 Image\ Manipulation/lsbsteg.py [encode/decode] -i [image_path] -m '[message]'`
    - encode saves a copy of the image_path with a '_1' appended encoded with the message
    - decode prints the encoded message in the image_path
  2. Determine a suitable social media site that meets our requirements (anonymous user upload, no or lossless compression)
    - social media sites investigated:
      - SendSpace
      - Whisper
      - Flickr
      - Yogile
  3. Design and implement basic upload application in Python for the selected social media site 
    - `$ python3 Web Connection/api_cons.py`
    - returns the download url for the uploaded random cat image (stores the delete URL as well)

###Sprint 2: Covert Mapping Structure
Sprint broken into four sub-goals
  1. Design the map structure for the covert file system to allow maximum flexibility and usability. 
  2. Break a large message file into parts to encode across multiple images. 
  3. Begin to add API connection and Encode/Decoder into Application. 
  4. From previous Sprint: 
      - Keep all images in memory
      - Error handling in API connection
      - Enforce restrictions on arguments in encode/decode

###Sprint 3: Beta release
  Basic stand-alone application to encode/decode a local covert file-system that is able to store, open, and delete files from the covert file-system. Command line program will work similar to a unix based directory system. 

##Usage: 
  - View current directory
  - Change current directory
  - View all files in current directory
  - Copy file
  - Move file
  - Rename files
  - Delete files
  - Create folder
  - Delete folder
  - Save file to covert file-system i.e `params: [source data] [destination path]`
  - Open file from file-system

##Testing:
  - 26 tests in lsbsteg.py for varying length text encodings. 
    - Test for encoding with files other than text such as other images, documents, pdf, etc.
  - api_cons.py tested with .png and .jpg and does not hinder encoding/decoding of images uploaded or downloaded. 
