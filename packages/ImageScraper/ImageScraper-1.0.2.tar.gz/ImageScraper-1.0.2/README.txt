ImageScraper
============
First python app :D
A simple python script which downloads all images in the given webpage.


Download
--------
tar file:
Grab the latest build using https://pypi.python.org/pypi/ImageScraper 

pip install:
$pip install ImageScraper

 
Usage
-----
Using the tar file:

Extract the contents of the tar file.
Note that ``ImageScraper`` depends on ``lxml``. and ``requests``. 
If you run into problems in the compilation of ``lxml`` through ``pip``, install the ``libxml2-dev`` and ``libxslt-dev`` packages on your system.


$cd ImageScraper/image_scraper/
$python __init__.py
$ Enter URL to scrap: https://github.com
$ Found 6 images:
$ How many images to you want ? : 6
$ Done.

If installed using pip:

Open python in terminal.

$python
>>>import image_scraper
 Enter URL to scrap: https://github.com
 Found 6 images:
 How many images to you want ? : 6
 Done. 

A new folder called "images" will be created in the same place, containing all the downloaded images.

Todo
----
Create and run tests on travis-ci.org
