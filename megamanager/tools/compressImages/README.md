CompressImages
==============

Python script for automatically reducing size of all JPEG and PNG images in a directory.

Usage: `compressimages.py [-h] [--mode {compress,restorebackup,deletebackup}] path`

Positional arguments:  
  `path`                File or directory name

Optional arguments:  
  `-h, --help`          show this help message and exit  
  `--mode {compress,restorebackup,deletebackup}` Mode to solve with (default: compress)
  * `compress`: Compress the image(s).  
  * `restorebackup`: Restore the backup images (valid for directory path only).  
  * `deletebackup`: Delete the backup images (valid for directory path only).  

Python 2.7 or later is required.

See [Using Python to Reduce JPEG and PNG Image File Sizes Without Loss of Quality (Softwariness.com)](https://www.softwariness.com/articles/reduce-image-file-sizes-using-python/) for more information.
