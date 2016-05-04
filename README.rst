About the Project
=================

This project was completed in fulfillment of the requirements for XE 402 at the United States Military Academy for AY2016. This Covert File System, called WebStegFS, is a web-based application that allows users to covertly share files through social media sites while maintaining plausible deniability for both the user(s) and the social media site. 

The purpose of this project is to provide the framework for users to fully customize a web based covert file system. The steganography technique, encryption, and online service are modular and allow developers to drop in their own custom modules so that webStegFS suits their specific needs. 

License
=======

This project is released under the MIT License. 

Setup
=====

- Clone the project from GitHub ``git clone https://github.com/gorhack/webStegFS.git``

Covert File System is written exclusively in Python 3 due to the vast modules and libraries that support our goals. Currently `webStegFS` only supports using `sendspace` for upload on the web.

- Dependencies:

  - Install `Pillow <https://pillow.readthedocs.org/en/3.0.0/installation.html>`_ dependencies
  - python3, pip3 ``$ pip3 install -r utls/requirements.txt``
  - On OS X install `FUSE <https://osxfuse.github.io>`_ (Read-Only file system due to lack of ntfs support on OS X)
  - Get a sendspace API key `here <https://www.sendspace.com/dev_apikeys.html>`_
  - Copy your sendspace API key and create a file in /Web_Connection/API_Keys/ containing ``sendSpaceKey='API KEY GOES HERE'``
  - ``$ sudo python3 setup.py install``

Usage
=====
- From source: ``$ python3 -m webStegFS [url to fs] [options]`` [1]_
- From wheel: ``$ webStegFS [url to fs] [options]``

  - -c command loop, run webStegFS shell
  - -w social media site to upload/download images [default: sendspace]
  - -p use built in proxy
  - -e encryption type [default: xor]
  - -m mount point [default: covertMount]
  - -s steganography [default: LSBsteg]

- ``webStegFS$ [command]`` basic application usage.

  - ``mount`` mounts the file system using FUSE
  - ``proxy`` / ``noproxy`` turns the built in proxy on/off respectively
  - ``loadfs [url]`` load a covert file system
  - ``newfs`` uploads the old fs and returns the url. loads a new covert file system.
  - ``encodeimage [file]`` encode an image with a file, returns the URL to the image
  - ``decodeimage [url]`` decode an image, returns the file
  - ``uploadfs [url]`` save the covert file system, returns URL to the root image. To load the same file system this URL must be retained.
  - ``mkdir [path]`` make directories in the covert file system at the given path
  - ``rmdir [path]`` remove directories in the covert file system at the given path
  - ``mkfile [name] [text] [path]`` create a text file in the covert file system at the path
  - ``upload [local path] [covert path]`` upload a file to the covert file system
  - ``download [covert path] [local path]`` download a file on the covert file system to disk
  - ``ls [path]`` list directory contents
  - ``cd [path]`` change directory in the covert file system to the path
  - ``cat [file]`` concatenate and print files
  - ``rm [path]`` remove a file from the covert file system
  - ``hist`` show the history of previous commands
  - ``shell [cmd]`` run shell commands
  - ``help [cmd]`` show list of commands or documentation for a specific command
  - ``exit`` exit the covert file system

Sprints
=======

We created this project for a Capstone class for Computer Science at the United States Military Academy, West Point. This project was broken up into the seven sprints over the course of one year. Below you can find the progress we have made during each sprint.

Sprint 1: Knowledge acquisition
+++++++++++++++++++++++++++++++
Sprint broken into three sub-goals:

1. Implement basic steg module to encode and decode an image in Python

   - ``$ python3 Image_Manipulation/lsbsteg.py [encode/decode] -i [image_path] -m '[message]'``
   - encode saves a copy of the image_path with a '_1' appended encoded with the message
   - decode prints the encoded message in the image_path

2. Determine a suitable social media site that meets our requirements (anonymous user upload, no or lossless compression)

   - social media sites investigated:
     - SendSpace
     - Whisper
     - Flickr
     - Yogile

3. Design and implement basic upload application in Python for the selected social media site

   - ``$ python3 Web_Connection/api_cons.py``
   - returns the download url for the uploaded random cat image (stores the delete URL as well)


Sprint 2: Covert Mapping Structure
++++++++++++++++++++++++++++++++++
Sprint broken into four sub-goals

1. Design the map structure for the covert file system to allow maximum flexibility and usability.
2. Break a large message file into parts to encode across multiple images.

   - Analysis of how much data can be encoded using LSB
   - Determine file system overhead in each image

3. Begin to add API connection and Encode/Decoder into Application.

   - ``$ python3 main.py [url]`` url can be the full url path or the file id (6 character ending, i.e xvdmcn)
     - enter no url for an empty file system
   - ``webStegFS$ [command]``

4. Functional Design Documents
5. From previous Sprint:

   - Keep all images in memory
   - Error handling in API connection
   - Enforce restrictions on arguments in encode/decode

Sprint 3: Beta release
++++++++++++++++++++++
Basic stand-alone application to encode/decode a local covert file-system that is able to store, open, and delete files from the covert file-system. Command line program will work similar to a unix based directory system. Using these commands will require breaking the file structure across multiple encoded images. Everything is seamless to the user who only needs to keep track of the /root image URL and then navigate the file system with ease.

Sprint 4: Publication start and alpha release
+++++++++++++++++++++++++++++++++++++++++++++
Sprint broken down into 5 sub-goals:

1. Basic draft of paper for publication using LaTEX.
2. Create a backlog of things required to implement webStegFS into a live operating system such as Tails.
3. Publish documentation using apidocs.
4. Create a FUSE module for webStegFS.
5. Change steg technique to allow storage of larger files with dynamic sizes.

Sprint 5: Publication draft and beta release
++++++++++++++++++++++++++++++++++++++++++++
Sprint broken down into 6 sub-goals:

1. Encode/decode any file
2. Background process/thread for uploading and downloading images
3. Modularize classes
4. Rough draft (80%) publication
5. Working implementation of webStegFS on Tails OS
6. Modular encryption class

Sprint 6: Prepare for projects day
++++++++++++++++++++++++++++++++++
Spring broken down into 6 sub-goals:

1. Prepare Project's day materials
2. Integrate WebStegFS into TAILS
3. Finalize paper
4. Complete packaging of WebStegFS for distribution
5. Prepare and conduct prototype day rehearsal
6. Complete Wiki and user manual for hand off
