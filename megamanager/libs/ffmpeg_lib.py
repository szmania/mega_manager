##
# Created by: Curtis Szmania
# Date: 6/5/2017
# Initial Creation.
###

from .lib import Lib
from .mega_tools_lib import MEGA_MANAGER_CONFIG_DIR
from logging import getLogger
from os import path, remove, sep
from platform import system

__author__ = 'szmania'

HOME_DIRECTORY = "~"
FFMPEG_LOG_PATH = path.join("{MEGA_MANAGER_CONFIG_DIR}".format(
    MEGA_MANAGER_CONFIG_DIR=MEGA_MANAGER_CONFIG_DIR),"logs","ffmpeg.log")



class FFMPEG_Lib(object):
    def __init__(self, log_level='DEBUG', log_file_path=FFMPEG_LOG_PATH):
        """
        Library for ffmpeg converter and encoder interaction.

        Args:
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
            log_file_path (str): Log file path for ffmpeg.

        """

        self.__log_level = log_level
        self.__ffmpeg_log = log_file_path
        self.__lib = Lib(log_level=log_level)

    def compress_video_file(self, source_path, target_path, compression_max_width=1280, compression_preset="medium",
                            ffmpeg_threads=1, overwrite=False,
                            process_priority_class="NORMAL_PRIORITY_CLASS", process_set_priority_timeout=60):
        """
        Compress video file.

        Args:
            source_path (str): File path of video to __compress_all.
            target_path (str): File path of video to be compressed into.
            compression_max_width (int): Compression for video, max width. eg. 1280 or 1920
            compression_preset (str): Compression preset. ie: "fast" or "slow"
            ffmpeg_threads (int): Number of threads to use when running ffmpeg.
            overwrite (bool): Overwrite target file if it exists.
            process_priority_class (str): Priority level to set for process. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

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

        cmd = ('ffmpeg -i "{source_path}" -vf "scale=\'if(lte(iw,{compression_max_width}), {compression_max_width}, iw)\':-2" '
               '-preset {preset} -threads {ffmpeg_threads} -max_muxing_queue_size 9999 "{target_path}"').format(
            source_path=source_path, compression_max_width=compression_max_width, preset=compression_preset,
            ffmpeg_threads=ffmpeg_threads, target_path=target_path)

        process_name = 'ffmpeg.exe' if system() == 'Windows' else 'ffmpeg'
        result = self.__lib.exec_cmd(command=cmd, no_window=True, output_file=self.__ffmpeg_log, process_priority_class=process_priority_class,
                                     process_name=process_name, process_set_priority_timeout=process_set_priority_timeout)

        if result:
            logger.debug(' Success, could compress video file "%s" to "%s".' % (source_path, target_path))
        else:
            logger.error(' Error, could NOT compress video file "%s"!' % source_path)
        return result

