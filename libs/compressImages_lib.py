##
# Created by: Curtis Szmania
# Date: 6/5/2017
# Initial Creation.
###

from logging import getLogger
from os import path
from tools import CompressImage, DeleteBackupImage

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))


class CompressImages_Lib(object):
    def __init__(self, logLevel='DEBUG'):
        """
        Library for compressImages.py interaction.

        Args:
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        self.__logLevel = logLevel

        self.__compressImagesObj = CompressImage()
        self.__deleteBackupImageObj = DeleteBackupImage()


    def compress_image_file(self, filePath):
        """
        Compress images file.

        Args:
            filePath (str): File path of image to __compressAll.

        Returns:
            Boolean: whether compression operation was successful or not.
        """

        logger = getLogger('CompressImages_Lib.compress_image_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' Compressing image file "%s".' % filePath)

        result = self.__compressImagesObj.processfile(filename=filePath)

        if result:
            logger.debug(' Success, file "%s" compressed successfully.' % filePath)
            return True
        else:
            logger.debug(' Error, file "%s" NOT compressed successfully!' % filePath)
            return False

    def delete_backup_file(self, filePath):
        """
        Delete backup file.

        Args:
            filePath (str): File path of image backup to delete

        Returns:
             Boolean: whether compression operation was successful or not.
        """

        logger = getLogger('CompressImages_Lib.delete_backup_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' Deleting compression file backup "%s".' % filePath)

        result = self.__deleteBackupImageObj.processfile(file=filePath)

        if result:
            logger.debug(' Success, could remove backup image compression files in direcotry "%s"' % filePath)
            return True
        else:
            logger.error(' Error, could NOT remove backup image compression files in direcotry "%s"' % filePath)
            return False

    def delete_backups_in_dir(self, dirPath):
        """
        Delete backup files in directory

        Args:
            dirPath (str): Directory path of image backups to delete

        Returns:
             Boolean: whether compression operation was successful or not.
        """

        logger = getLogger('CompressImages_Lib.delete_backups_in_dir')
        logger.setLevel(self.__logLevel)

        logger.debug(' Deleting compression file backups in dirPath "%s".' % dirPath)

        result = self.__deleteBackupImageObj.processdir(path=dirPath)

        if result:
            logger.debug(' Success, could remove backup image compression files in direcotry "%s"' % dirPath)
            return True
        else:
            logger.error(' Error, could NOT remove backup image compression files in direcotry "%s"' % dirPath)
            return False
