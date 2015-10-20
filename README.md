# covertFS
It's covert and stuff. 
##About: 
  A web-based application that allows users to covertly share files through social media sites while maintaining plausible deniability for both the user(s) and the social media site. 

##Sprints: 

###Sprint 1: Knowledge aquisition
Sprint broken into three sub-goals: 
  1. Implement basic step module to encode and decode an image in Python.
  2. Determine a suitable social media site that meets our requirements (anonymous user upload, no or lossless compression).
  3. Design and implement basic upload application in Python for the selected social media site.

###Sprint 2: Covert Mapping Structure
  Design the map structure for the covert file system to allow maximum flexibility and usability. Break large files into parts to encode in a large file across multiple images. 

###Sprint 3: Beta release
  Basic stand-alone application to encode/decode a local covert file-system using the The Cat API as a source of images that is able to store, open, and delete files from the covert file-system. 
    
##Setup: Python 3, pip3 (pip3 install -r utls/requirements.txt)

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
  - Save file to covert file-system `params: [source data] [destination path]`
  - Open file from file-system

##Testing:
