##
# Created by: Curtis Szmania
# Date: 6/5/2017
# Initial Creation.
###
from lib import Lib
from logging import getLogger
from os import path
from re import IGNORECASE, match
from tools.compressImages import CompressImage, DeleteBackupImage
# from tools import CompressImage, DeleteBackupImage

__author__ = 'szmania'


class CompressImages_Lib(object):
    def __init__(self, log_level='DEBUG'):
        """
        Library for compressImages.py interaction.

        Args:
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        self.__log_level = log_level

        self.__compress_images_obj = CompressImage()
        self.__deleteBackupImageObj = DeleteBackupImage()
        self.__lib = Lib(log_level=self.__log_level)

    def compress_image_file(self, file_path, jpeg_compression_quality_percentage, delete_backup=False,
                            delete_corrupt_images=False):
        """
        Compress images file.

        Args:
            file_path (str): File path of image to compress.
            jpeg_compression_quality_percentage (int): Quality percentage compression for jpeg files.
            delete_backup (bool): Delete backup image file.
            delete_corrupt_images (bool): Delete backup image file.

        Returns:
            Boolean: whether compression operation was successful or not.
        """

        logger = getLogger('CompressImages_Lib.compress_image_file')
        logger.setLevel(self.__log_level)

        logger.debug(' Compressing image file: "%s"' % file_path)
        results = []
        file_ext = file_path.split('.')[-1]
        compressed_any_image = self.__compress_images_obj.processfile(filename=file_path)
        results.append(compressed_any_image)

        if match('jpe{0,1}g', file_ext, IGNORECASE):
            jpeg_compressed = self.compress_jpeg_image_file(file_path=file_path,
                                                            quality_percentage=jpeg_compression_quality_percentage)

            if delete_corrupt_images and not jpeg_compressed:
                logger.debug(' Deleting CORRUPT JPEG or JPG image file: "{}"'.format(file_path))
                self.__lib.delete_local_file(file_path=file_path)

            results.append(jpeg_compressed)

        if delete_backup:
            compress_path_backup = file_path + '.compressimages-backup'
            if path.exists(compress_path_backup):
                logger.debug(' Removing backup image file "{}"!'.format(compress_path_backup))
                self.__lib.delete_local_file(file_path=compress_path_backup)

        if True in results:
            logger.debug(' Success, image file "%s" compressed successfully.' % file_path)
            return True

        logger.debug(' Error, image file "%s" NOT compressed successfully!' % file_path)
        return False

    def compress_jpeg_image_file(self, file_path, quality_percentage):
        """
        Compress images file.

        Args:
            file_path (str): File path of image to compress.
            quality_percentage (int): Percentage to set output jpeg file.

        Returns:
            Boolean: whether compression operation was successful or not.
        """

        logger = getLogger('CompressImages_Lib.compress_jpeg_image_file')
        logger.setLevel(self.__log_level)

        logger.debug(' Compressing JPEG or JPG image file "%s".' % file_path)
        compressed = False
        skipped = False
        result = None
        try:
            result = self.__lib.exec_cmd_and_return_output(command='jpegoptim --max={quality_percentage} "{file_path}"'.format(
                quality_percentage=quality_percentage, file_path=file_path))
        except Exception as e:
            logger.error(' Exception: {}'.format(e))
        if 'optimized' in result[0]:
            logger.debug(' Success, JPEG or JPG image file "%s" compressed successfully.' % file_path)
            return True
        elif 'skipped' in result[0]:
            logger.debug(' JPEG or JPG file already optimized! File was skipped: "{}"'.format(file_path))
            return True
        else:
            logger.debug(' Error, JPEG or JPG image file "%s" NOT compressed successfully!' % file_path)
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
        logger.setLevel(self.__log_level)

        logger.debug(' Deleting compression file backups in dirPath "%s".' % dirPath)

        result = self.__deleteBackupImageObj.processdir(path=dirPath)

        if result:
            logger.debug(' Success, could remove backup image compression files in direcotry "%s"' % dirPath)
            return True
        else:
            logger.error(' Error, could NOT remove backup image compression files in direcotry "%s"' % dirPath)
            return False
