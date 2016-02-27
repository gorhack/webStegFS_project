Image_Manipulation package
**************************


Submodules
==========

stegByteStream module
---------------------

The basic idea of the algorithm is to take each individual bit of the message and set it as the least significant bit of each component of each pixel of the image. Usually, a pixel has Red, Green, Blue components and sometimes an Alpha component. Because the values of these components change very little if the least significant bit is changed, the color difference is not particularly noticeable, if at all.


.. automodule:: Image_Manipulation.lsbsteg
    :members:
    :undoc-members:
    :show-inheritance:


genImage module
---------------

The `genImage` module returns an image on request as a `BytesIO` object.


.. automodule:: Image_Manipulation.genImage
    :members:
    :undoc-members:
    :show-inheritance:
