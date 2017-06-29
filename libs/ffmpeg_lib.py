##
# Created by: Curtis Szmania
# Date: 6/5/2017
# Initial Creation.
###

from logging import getLogger
from os import chdir, path
from subprocess import call

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))


class FFMPEG_Lib(object):
    def __init__(self, ffmpegExePath, logLevel='DEBUG'):
        """
        Library for __ffmpeg converter and encoder interaction.

        :param ffmpegExePath: Path to __ffmpeg.exe
        :type ffmpegExePath: String.
        :param logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type logLevel: String.
        """

        self.ffmpegExePath = ffmpegExePath
        self.logLevel = logLevel

    def compress_video_file(self, filePath, targetPath):
        """
        Compress video file.
    
        :param filePath: File path of video to __compressAll.
        :type filePath: string
        :param targetPath: File path of video to be compressed into.
        :type targetPath: string
    
        :return: subprocess object
        """
    
        logger = getLogger('__lib.compress_video_file')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Compressing video file: "%s"' % filePath)
    
        cmd = '"%s" -i "%s" -vf "scale=\'if(gte(iw,720), 720, iw)\':-2" -preset medium -__threads 1 "%s"' % (self.ffmpegExePath, filePath, targetPath)
    
        proc1 = self._exec_cmd(command=cmd, noWindow=True)
    
        return proc1


    def _exec_cmd(self, command, workingDir=None, noWindow=False):
        """
        Execute given command.

        :param command: Command to execute.
        :type command: String
        :param workingDir: Working directory.
        :type workingDir: String.
        :param noWindow: No window will be created if set to True.
        :type noWindow: Boolean

        :return: subprocess object
        """

        logger = getLogger('FFMPEG_Lib._exec_cmd')
        logger.setLevel(self.logLevel)

        logger.debug(' Executing command: "%s"' % command)

        if workingDir:
            chdir(workingDir)

        if noWindow:
            CREATE_NO_WINDOW = 0x08000000
            proc = call(command, creationflags=CREATE_NO_WINDOW)
        else:
            proc = call(command)

        return proc

