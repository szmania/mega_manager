##
# Created by: Curtis Szmania
# Date: 6/5/2017
# Initial Creation.
###

from .lib import Lib
from logging import getLogger
from os import path

__author__ = 'szmania'

FFMPEG_LOG = 'ffmpeg.log'
SCRIPT_DIR = path.dirname(path.realpath(__file__))

class FFMPEG_Lib(object):
    def __init__(self, ffmpegExePath, logLevel='DEBUG', logFilePath=FFMPEG_LOG):
        """
        Library for __ffmpeg converter and encoder interaction.

        Args:
            ffmpegExePath (str): Path to ffmpeg.exe
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        self.__ffmpegExePath = ffmpegExePath
        self.__logLevel = logLevel
        self.__ffmpegLog = logFilePath

        self.__lib = Lib(logLevel=logLevel)


    def compress_video_file(self, filePath, targetPath):
        """
        Compress video file.

        Args:
            filePath (str): File path of video to __compressAll.
            targetPath (str): File path of video to be compressed into.

        Returns:
            subprocess object:
        """
    
        logger = getLogger('FFMPEG_Lib.compress_video_file')
        logger.setLevel(self.__logLevel)
    
        logger.debug(' Compressing video file: "%s"' % filePath)
    
        cmd = '"%s" -i "%s" -vf "scale=\'if(gte(iw,720), 720, iw)\':-2" -preset medium -threads 1 "%s"' % \
              (self.__ffmpegExePath, filePath, targetPath)

        result = self.__lib.exec_cmd(command=cmd, noWindow=True, outputFile=self.__ffmpegLog)

        if result:
            logger.debug(' Success, could compress video file "%s" to "%s".' % (filePath, targetPath))
        else:
            logger.error(' Error, could NOT compress video file "%s"!' % filePath)
        return result

