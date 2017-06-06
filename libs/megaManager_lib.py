##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from logging import DEBUG, getLogger, FileHandler, Formatter, StreamHandler
from os import chdir, getpid, kill, listdir, path, remove, rename, walk
from re import findall, split, sub
from signal import SIGTERM
from subprocess import call, PIPE, Popen

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))

class MegaManager_Lib(object):
    def __init__(self, workingDir, logLevel):
        """
        :param workingDir: Working directory of megaManager script
        :type workingDir: String.
        :param logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type logLevel: String.
        """

        self.workingDir = workingDir
        self.logLevel = logLevel
    
    
    def compress_image_file(self, filePath):
        """
        Compress images file.
    
        :param filePath: File path of image to compress.
        :type filePath: string
        :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type self.logLevel: String.
    
        :return: subprocess object
        """
    
        logger = getLogger('megaManager_lib._compress_image_file')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Compressing image file "%s".' % filePath)
    
        cmd = 'D:\\Python\\Python27\\python.exe "%s\\libs\\compressImages\\compressImages.py" --mode compress "%s"' % (
        self.workingDir, filePath)
        cmd = 'python "%s\\libs\\compressImages\\compressImages.py" --mode compress "%s"' % (
        self.workingDir, filePath)
        proc1 = self.exec_cmd(command=cmd, noWindow=True)
    
        return proc1
    
    def compress_video_file(self, filePath, targetPath):
        """
        Compress video file.
    
        :param filePath: File path of video to compress.
        :type filePath: string
        :param targetPath: File path of video to be compressed into.
        :type targetPath: string
        :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type self.logLevel: String.
    
        :return: subprocess object
        """
    
        logger = getLogger('lib.compress_video_file')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Compressing video file: "%s"' % filePath)
    
        cmd = '"%s\\tools\\compressVideos\\ffmpeg.exe" -i "%s" -vf "scale=\'if(gte(iw,720), 720, iw)\':-2" -preset medium -threads 1 "%s"' % (self.workingDir, filePath, targetPath)
    
        proc1 = self.exec_cmd(command=cmd, noWindow=True)
    
        return proc1
    
    def dump_list_into_file(self, itemList, file):
        """
        Dump list into file for each item on a new line.
    
        :param itemList: List to dump into file.
        :type itemList: list
        :param file: File to dump to.
        :type file: string
        :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type self.logLevel: String.
    
        :return: boolean of whether successful or not
        """
    
        logger = getLogger('megaManager_lib.dump_list_into_file')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Dumping list into %s file.' % file)
    
        fileObj = open('%s' % (file), 'w')
    
        for item in itemList:
            fileObj.write("%s\n" % item)
    
    def exec_cmd(self, command, workingDir=None, noWindow=False):
        """
        Execute given command.
    
        :param command: Command to execute.
        :type command: String
        :param workingDir: Working directory.
        :type workingDir: String
        :param noWindow: No window will be created if true.
        :type noWindow: Boolean
    
        :return: subprocess object
        """
    
        logger = getLogger('lib._exec_cmd')
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
    
    def get_mb_size_from_bytes(self, bytes):
        """
        Convert bytes to size in MegaBytes.
    
        :param bytes: Size in bytes.
        :type bytes: Integer.
        :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type self.logLevel: String.
    
        :return: Size in MegaBytes from bytes.
        """
    
        logger = getLogger('MegaManager.get_mb_size_from_bytes')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Converting kilobytes to megabytes.')
    
        result = ''
        if bytes < 1000:
            result = '%i' % bytes + 'B'
        elif 1000 <= bytes < 1000000:
            result = '%.1f' % float(bytes / 1000) + 'KB'
        elif 1000000 <= bytes < 1000000000:
            result = '%.1f' % float(bytes / 1000000) + 'MB'
        elif 1000000000 <= bytes < 1000000000000:
            result = '%.1f' % float(bytes / 1000000000) + 'GB'
        elif 1000000000000 <= bytes:
            result = '%.1f' % float(bytes / 1000000000000) + 'TB'
    
        return result
    
    def get_sleep_time(self):
            """
            Get time in seconds to sleep. Function is used to pace program speed during iterations.
    
            :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
            :type self.logLevel: String.
    
            :return: time in seconds to sleep
            :type: integer or decimal
            """
    
            logger = getLogger('megaManager_lib.get_sleep_time')
            logger.setLevel(self.logLevel)
    
            sleepTime = 0
    
            return sleepTime
    
    def kill_running_processes_with_name(self, procName):
        """
        Kill processes with name.
    
        :param procName: Process name.
        :type procName: String.
        :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type self.logLevel: String.
    
        :return:
        :type:
        """
    
        logger = getLogger('megaManager_lib.kill_running_processes_with_name')
        logger.setLevel(self.logLevel)
    
        logger.info(' Killing processes with name "%s"' % procName)
        # p = Popen(['ps', '-a'], stdout=PIPE)
        p = Popen(['tasklist', '/v'], stdout=PIPE)
        out, err = p.communicate()
    
        for line in out.splitlines():
            if line.startswith(procName):
                pid = int(line.split()[1])
                kill(pid, SIGTERM)
    
        logger.debug(' Success, all "%s" process have been killed.' % procName)
    
    def size_of_dir(self, dirPath):
        """
        Walks through the directory, getting the cumulative size of the directory
    
        :param dirPath: Directory to walk through to get size.
        :type dirPath: String.
        :param self.logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type self.logLevel: String.
    
        :return sum: Size in bytes.
        """
    
        logger = getLogger('megaManager_lib.size_of_dir')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Getting size of directory "%s"' % dirPath)
    
        sum = 0
        for file in listdir(dirPath):
            sum += path.getsize(dirPath + '\\' + file)
        return sum
    


