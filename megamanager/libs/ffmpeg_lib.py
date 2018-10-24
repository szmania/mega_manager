##
# Created by: Curtis Szmania
# Date: 6/5/2017
# Initial Creation.
###

from .lib import Lib
from logging import getLogger
from os import path, remove


__author__ = 'szmania'

HOME_DIRECTORY = path.expanduser("~")
MEGA_MANAGER_CONFIG_DIR = HOME_DIRECTORY + "\\.mega_manager"

FFMPEG_LOG = MEGA_MANAGER_CONFIG_DIR + '\\logs\\ffmpeg.log'

SCRIPT_DIR = path.dirname(path.realpath(__file__))

class FFMPEG_Lib(object):
    def __init__(self, log_level='DEBUG', log_file_path=FFMPEG_LOG):
        """
        Library for __ffmpeg converter and encoder interaction.

        Args:
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
            log_file_path (str): Log file path for ffmpeg.
        """

        self.__log_level = log_level
        self.__ffmpeg_log = log_file_path

        self.__lib = Lib(logLevel=log_level)


    def compress_video_file(self, source_path, target_path, compression_preset="medium", overwrite=False):
        """
        Compress video file.

        Args:
            source_path (str): File path of video to __compress_all.
            target_path (str): File path of video to be compressed into.
            compression_preset (str): Compression preset. ie: "fast" or "slow"
            overwrite (bool): Overwrite target file if it exists.

        Returns:
            subprocess object:
        """
    
        logger = getLogger('FFMPEG_Lib.compress_video_file')
        logger.setLevel(self.__log_level)
    
        logger.debug(' Compressing video file: "%s"' % source_path)

        if overwrite:
            logger.debug(' Overwrite set to "True". Removing target file: "%s"' % target_path)
            if path.exists(target_path):
                try:
                    remove(target_path)
                except Exception as e:
                    print(' Exception: %s' % str(e))
                    pass

        cmd = 'ffmpeg -i "{source_path}" -vf "scale=\'if(gte(iw,720), 720, iw)\':-2" -preset {preset} -threads 1 ' \
              '-max_muxing_queue_size 9999 "{target_path}"'.format(
            source_path=source_path, preset=compression_preset, target_path=target_path)

        result = self.__lib.exec_cmd(command=cmd, noWindow=True, output_file=self.__ffmpeg_log, low_priority=True)

        if result:
            logger.debug(' Success, could compress video file "%s" to "%s".' % (source_path, target_path))
        else:
            logger.error(' Error, could NOT compress video file "%s"!' % source_path)
        return result

