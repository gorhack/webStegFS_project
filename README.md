# covertFS
It's covert and stuff.
##About:
  A web-based application that allows users to covertly share files through social media sites while maintaining plausible deniability for both the user(s) and the social media site.

##Setup:
  Covert FS is written exclusively in Python 3 due to the vast modules and libraries that support our goals.

  - Dependencies:
    - python3, pip3 `$ pip3 install -r utls/requirements.txt`
    - config.py file in /Web_Connection/API_Keys/ containing `sendSpaceKey='API KEY GOES HERE'`

##Sprints:

###Sprint 1: Knowledge aquisition
Sprint broken into three sub-goals:

1. Implement basic steg module to encode and decode an image in Python
  - `$ python3 Image_Manipulation/lsbsteg.py [encode/decode] -i [image_path] -m '[message]'`
  - encode saves a copy of the image_path with a '_1' appended encoded with the message
  - decode prints the encoded message in the image_path
2. Determine a suitable social media site that meets our requirements (anonymous user upload, no or lossless compression)
  - social media sites investigated:
    - SendSpace
    - Whisper
    - Flickr
    - Yogile
3. Design and implement basic upload application in Python for the selected social media site
  - `$ python3 Web_Connection/api_cons.py`
  - returns the download url for the uploaded random cat image (stores the delete URL as well)

###Sprint 2: Covert Mapping Structure
Sprint broken into four sub-goals

1. Design the map structure for the covert file system to allow maximum flexibility and usability.
2. Break a large message file into parts to encode across multiple images.
  - Analysis of how much data can be encoded using LSB
  - Determine file system overhead in each image
3. Begin to add API connection and Encode/Decoder into Application.
  - `$ python3 main.py [url]`<sup>[*](#option)</sup> // url can be the full url path or the file id (6 character ending, i.e xvdmcn)
  - `covertFS$ [command]`
4. Functional Design Documents
5. From previous Sprint:
  - Keep all images in memory
  - Error handling in API connection
  - Enforce restrictions on arguments in encode/decode

###Sprint 3: Beta release
Basic stand-alone application to encode/decode a local covert file-system that is able to store, open, and delete files from the covert file-system. Command line program will work similar to a unix based directory system. Using these commands will require breaking the file structure across multiple encoded images. Everything is seamless to the user who only needs to keep track of the /root image URL and then navigate the file system with ease.

###Sprint 4: Publication start and alpha release
Sprint broken down into 5 sub-goals:

1. Basic draft of paper for publication using LaTEX.
2. Create a backlog of things required to implement covertFS into a live operating system such as Tails.
3. Publish documentation using apidocs.
4. Create a FUSE module for covertFS.
5. Change steg technique to allow storage of larger files with dynamic sizes.

##Usage:
  - `$ python3 main.py [url of folder/root]`<sup>[*](#option)</sup>
  - `covertFS$ [command]`
  - documented commands:
    - `newfs` uploads the old fs and returns the url. loads a new covert file system.
    - `loadfs [url]` load a covert file system
    - `ls [path]`<sup>[*](#option)</sup> list directory contents
    - `cd [path]` change directory in the covert file system to the path
    - `cat [file]` concatenate and print files
    - `upload [local path] [covert path]` upload a file to the covert file system
    - `rm [path]` remove a file from the covert file system
    - `mkfile [name] [text] [path]` create a text file in the covert file system at the path
    - `mkdir [path]` make directories in the covert file system at the given path
    - `rmdir [path]` remove directories in the covert file system at the given path
    - `download [covert path] [local path]` download a file on the covert file system to disk
    - `uploadfs [url]` save the covert file system, returns URL to the root image. To load the same file system this URL must be retained.
    - `encodeimage [msg]` encode an image with a message, returns the URL to the image
    - `decodeimage [msg]` decode an image, returns the message
    - `hist` show the history of previous commands
    - `shell [cmd]` run shell commands
    -  `help [cmd]`<sup>[*](#option)</sup> show list of commands or documentation for a specific command
    - `exit` exit the covert file system
    - `proxy / noproxy` turns the built in proxy on/off respectively

##Testing:
  - 26 tests in lsbsteg.py for varying length text encodings.
    - Test for encoding with files other than text such as other images, documents, pdf, etc.
  - api_cons.py tested with .png and .jpg and does not hinder encoding/decoding of images uploaded or downloaded.
  - built in test cases for each encode/decode prior to upload


<a name="option">*</a>optional parameter
