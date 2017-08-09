##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from logging import getLogger
from numpy import array, load, savez_compressed
from os import chdir, kill, listdir, path
from signal import SIGTERM
from subprocess import call, PIPE, Popen
from tools import CompressImage

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))


class MegaManager_Lib(object):
    def __init__(self, workingDir, logLevel='DEBUG'):
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
    
        :param filePath: File path of image to __compressAll.
        :type filePath: string

        :return: Boolean of whether compression operation was successful or not.
        """
    
        logger = getLogger('megaManager_lib._compress_image_file')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Compressing image file "%s".' % filePath)
    
        # cmd = 'D:\\Python\\Python27\\python.exe "%s\\libs\\__compressImages\\__compressImages.py" --mode __compressAll "%s"' % (
        #     self.workingDir, filePath)
        # cmd = 'python "%s\\libs\\__compressImages\\__compressImages.py" --mode __compressAll "%s"' % (
        #     self.workingDir, filePath)
        # proc1 = self.exec_cmd(command=cmd, noWindow=True)
        #
        # return proc1

        compressImageObj = CompressImage()
        result = compressImageObj.processfile(filename=filePath)

        if result:
            logger.debug(' Success, file "%s" compressed successfully.' % filePath)
            return True
        else:
            logger.debug(' Error, file "%s" NOT compressed successfully!' % filePath)
            return False


    def dump_list_into_file(self, itemList, filePath):
        """
        Dump list into file for each item on a new line.
    
        :param itemList: List to dump into file.
        :type itemList: list
        :param filePath: File to dump to.
        :type filePath: string
    
        :return: boolean of whether successful or not
        """
    
        logger = getLogger('MegaManager_lib.dump_list_into_file')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Dumping list into %s filePath.' % filePath)

        try:
            npList = array(itemList)
            savez_compressed(filePath, list=npList)
        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
    
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
    
        logger = getLogger('MegaManager_Lib.exec_cmd')
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
    
            :return: Time in seconds to sleep as integer.
            """
    
            logger = getLogger('megaManager_lib.get_sleep_time')
            logger.setLevel(self.logLevel)
    
            sleepTime = 0
    
            return sleepTime

    def get_items_in_list_with_subString(self, list, subString):
        """
        Return sub list of list that contain substring.

        :param list: List to find substrings in.
        :type list: List.
        :param subString: Substring to find.
        :type subString: String.

        :return: List of items that contain subString.
        """

        logger = getLogger('MegaManager_Lib.get_items_in_list_with_subString')
        logger.setLevel(self.logLevel)

        subList = []
        for item in list:
            if subString in item:
                subList.append(item)
        return subList

    def kill_running_processes_with_name(self, procName):
        """
        Kill processes with name.
    
        :param procName: Process name.
        :type procName: String.
    
        :return:
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

    def load_file_as_list(self, filePath):
        """
        Load file as list splitting each line into a new item.

        :param filePath: File to lead.
        :type filePath: String.

        :return: Lines in file as list.
        """

        logger = getLogger('MegaManager_Lib.load_file_list_as_list')
        logger.setLevel(self.logLevel)

        logger.debug(' Loading %s filePath.' % filePath)

        items = []
        if path.isfile(filePath):
            try:
                data = load(file=filePath, allow_pickle=False)
                items = data.f.list.tolist()

            except Exception as e:
                logger.debug(' Exception: %s' % str(e))
            finally:
                return items

        else:
            logger.debug(' Error, filepath "%s" does NOT exist!' % filePath)
            return items

    def size_of_dir(self, dirPath):
        """
        Walks through the directory, getting the cumulative size of the directory
    
        :param dirPath: Directory to walk through to get size.
        :type dirPath: String.
    
        :return: Size in bytes as integer.
        """
    
        logger = getLogger('megaManager_lib.size_of_dir')
        logger.setLevel(self.logLevel)
    
        logger.debug(' Getting size of directory "%s"' % dirPath)
    
        sum = 0
        for file in listdir(dirPath):
            sum += path.getsize(dirPath + '\\' + file)
        return sum
    


