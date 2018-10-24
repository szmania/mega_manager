##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from logging import getLogger
from numpy import array, load, savez_compressed
from os import chdir, kill, listdir, path, remove, rename
import psutil
from re import split, sub
from signal import SIGTERM
from subprocess import call, PIPE, Popen
from threading import Thread
from time import localtime, sleep, strftime, time

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))
PROCESS_SET_PRIORITY_TIMEOUT = 60

class Lib(object):
    def __init__(self, logLevel='DEBUG'):
        """
        MegaManager library.

        Args:
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        self.__log_level = logLevel

    def _find_procs_by_name(self, name, timeout=PROCESS_SET_PRIORITY_TIMEOUT):
        """
        Return a list of processes matching 'name'
        Args:
            name (str): Process name to find.
            timeout (int): timeout in seconds to wait for process to start.

        Returns:
            List: Processes matching name.
        """
        logger = getLogger('Lib._set_proc_priority')
        logger.setLevel(self.__log_level)

        found_procs = []
        time_started = time()
        try:
            while True:
                for p in psutil.process_iter():
                    if p.name() == name:
                        found_procs.append(p)

                now = time()
                if len(found_procs) > 0:
                    logger.debug(' Success, found process "{}"'.format(name))
                    break
                elif now - time_started > timeout:
                    raise ProcessNameNotFound
            return found_procs

        except ProcessNameNotFound as e:
            logger.warning(' ProcessNameNotFound Exception: Process name "{}" not found!'.format(name))
        except Exception as e:
            logger.error(' Exception: {}'.format(e))

        return found_procs

    def _set_priority_once_proc_starts(self, process_name, priority):
        """
        Wait for process to start then set priority.
        Args:
            process_name (str): Process name to set priority.
            priority (): priority level. ie: "low"

        Returns:

        """
        logger = getLogger('Lib._set_priority_once_proc_starts')
        logger.setLevel(self.__log_level)

        sleep(1)
        t = Thread(target=self._thread_set_priority_once_proc_starts, args=(process_name, priority,),
                   name='thread_set_priority_{}'.format(process_name))

        t.start()

    def _set_proc_priority(self, proc, priority):
        """
        Set process priority.
        Args:
            proc: psutils process object.
            priority (str): Priority level. ie: PROCESS_MODE_BACKGROUND_BEGIN

        Returns:
            Boolean: Whether successful or not.
        """
        logger = getLogger('Lib._set_proc_priority')
        logger.setLevel(self.__log_level)

        try:
            if priority == 'low':
                proc.nice(psutil.IDLE_PRIORITY_CLASS)
                logger.debug(' Success, set process priority to IDLE_PRIORITY_CLASS.')
            return True
        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _thread_set_priority_once_proc_starts(self, process_name, priority):
        """
        Wait for process to start then set priority.
        Args:
            process_name (str): Process name to set priority.
            priority (): priority level. ie: "low"

        """
        logger = getLogger('Lib._thread_set_priority_once_proc_starts')
        logger.setLevel(self.__log_level)

        procs = self._find_procs_by_name(name=process_name)

        for proc in procs:
            self._set_proc_priority(proc=proc, priority=priority)

    def convert_epoch_to_mega_time(self, epoch_time):
        """
        Convert epoch time to time format used by MEGA.
            ie: 1247547145.65 to '2017-08-18 22:37:50'

        Args:
            epoch_time (str): Epoch time to convert.

        Returns:
            datetime: Converted datetime object. ie: '%Y-%m-%d %H:%M:%S'
        """
        return strftime('%Y-%m-%d %H:%M:%S', localtime(epoch_time))

    def delete_local_file(self, file_path):
        """
        Delete local file.

        Args:
            file_path (str): File path to delete.

        Returns:
            Boolean: boolean of whether successful or not
        """

        logger = getLogger('Lib.delete_local_file')
        logger.setLevel(self.__log_level)

        logger.debug(' Deleting local file: {}'.format(file_path))
        if path.exists(file_path):
            for retry in range(100):
                try:
                    remove(file_path)
                    logger.debug('File deleted!')
                    return True

                except Exception as e:
                    logger.exception(' Exception: {}'.format(e))
                    logger.debug(' Removing of file "{}" FAILED, retrying...'.format(file_path))
        else:
            logger.error('Cannot delete! Path does not exist: "{}"'.format(file_path))

        return False

    def dump_set_into_file(self, item_set, file_path):
        """
        Dump set into file for each item on a new line.

        Args:
            item_set (set): Set to dump into file.
            file_path (str): File to dump to.

        Returns:
            Boolean: boolean of whether successful or not
        """
    
        logger = getLogger('MegaManager_lib.dump_set_into_file')
        logger.setLevel(self.__log_level)
    
        logger.debug(' Dumping list into %s source_path.' % file_path)

        try:
            npList = array(list(item_set))
            savez_compressed(file_path, list=npList)
            return True
        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
            return False

    def exec_cmd(self, command, working_dir=None, noWindow=False, output_file=None, low_priority=False):
        """
        Execute given command.

        Args:
            command (str): Command to execute.
            working_dir (str): Working directory.
            noWindow (bool): No window will be created if true.
            output_file (str): file path to output program output to.
            low_priority (bool): If low priority task.

        Returns:
            subprocess object
        """
    
        logger = getLogger('Lib.exec_cmd')
        logger.setLevel(self.__log_level)
    
        logger.debug(' Executing command: "%s"' % command)

        try:
            if output_file:
                out_file = open(output_file, 'a')
            else:
                out_file=None

            if working_dir:
                chdir(working_dir)

            if low_priority:
                self._set_priority_once_proc_starts(process_name='ffmpeg.exe', priority='low')

            if noWindow:
                CREATE_NO_WINDOW = 0x08000000
                exitCode = call(command, stdout=out_file, stderr=out_file, creationflags=CREATE_NO_WINDOW)

            else:
                exitCode = call(command,  stdout=out_file, stderr=out_file)

            if exitCode == 0:
                logger.debug(' Successfully executed command "%s".' % command)
                return True

        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
        logger.warning(' Error when running command "%s".' % command)
        return False

    def exec_cmd_and_return_output(self, command, working_dir=None, output_file=None):
        """
        Execute given command and return stdout and stderr.

        Args:
            command (str): Command to execute.
            working_dir (str): Working directory.
            output_file (str): File to pipe process output to.

        Returns:
            Tuple: of stdout and stderr.
        """

        logger = getLogger('MegaTools_Lib.exec_cmd_and_return_output')
        logger.setLevel(self.__log_level)

        logger.debug(' Executing command: "%s"' % command)

        if working_dir:
            chdir(working_dir)

        try:
            # if output_file:
            #     outFile = open(output_file, 'a')
            #     proc = Popen(command, stdout=outFile, stderr=outFile)
            # else:
            proc = Popen(command, stdout=PIPE, shell=True)

            (out, err) = proc.communicate()
        except Exception as e:
            logger.warning(' Exception: %s' % str(e))
            return None, None
        # finally:
        #     if output_file:
        #         outFile.close()

        return out, err

    def get_mb_size_from_bytes(self, bytes):
        """
        Convert bytes to size in MegaBytes.

        Args:
            bytes (int): Size in bytes.

        Returns:
            string: Size in MegaBytes converted from bytes.
        """
    
        logger = getLogger('Lib.get_mb_size_from_bytes')
        logger.setLevel(self.__log_level)
    
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

    def get_remote_path_from_local_path(self, localPath, localRoot="\\", remoteRoot="\\"):
        """
        Get remote path given local path.

        Args:
            localPath (str): Local path.
            localRoot (str): Local root
            remoteRoot (str): Remote root.
        Returns:
            string: Remote path.
        """

        logger = getLogger('Lib.get_remote_path_from_local_path')
        logger.setLevel(self.__log_level)

        logger.debug(' Getting remote path from local path')

        localRoot_adj = sub('\\\\', '/', localRoot)
        localFilePath_adj = sub('\\\\', '/', localPath)
        postfix = split(localRoot_adj, localFilePath_adj)

        if len(postfix) > 1:
            subPath = postfix[1]

            logger.debug(' Success, could get remote path from local path.')
            return remoteRoot + subPath
        else:
            logger.debug(' Error, could NOT get remote path from local path!')
            return None

    def get_sleep_time(self):
            """
            Get time in seconds to sleep. Function is used to pace program speed during iterations.
    
            :return: Time in seconds to sleep as integer.
            """
    
            logger = getLogger('megaManager_lib.get_sleep_time')
            logger.setLevel(self.__log_level)
    
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

        logger = getLogger('Lib.get_items_in_list_with_subString')
        logger.setLevel(self.__log_level)

        subList = []
        for item in list:
            if subString in item:
                subList.append(item)
        return subList

    def kill_running_processes_with_name(self, procName):
        """
        Kill processes with name.

        Args:
            procName (str): Process name.

        :return:
        """
    
        logger = getLogger('megaManager_lib.kill_running_processes_with_name')
        logger.setLevel(self.__log_level)
    
        logger.info(' Killing processes with name "%s"' % procName)
        try:
            # p = Popen(['ps', '-a'], stdout=PIPE)
            p = Popen(['tasklist', '/v'], stdout=PIPE)
            out, err = p.communicate()


            for line in out.splitlines():
                if line.startswith(procName):
                    pid = int(line.split()[1])
                    kill(pid, SIGTERM)

            logger.debug(' Success, all "%s" processes have been killed.' % procName)
            return True

        except Exception as e:
            logger.error('Exception: {}'.format(e))
            return False

    def load_file_as_set(self, file_path):
        """
        Load file as set splitting each line into a new item.

        Args:
            file_path (str): File to lead.

        Returns:
            Lines in file as a set.
        """

        logger = getLogger('Lib.load_file_as_set')
        logger.setLevel(self.__log_level)

        items = []
        if path.isfile(file_path):
            logger.debug(' Loading this file as a set: {}'.format(file_path))

            items = []
            try:
                data = load(file=file_path, allow_pickle=False)
                items = data.f.list.tolist()

            except Exception as e:
                logger.debug(' Exception: %s' % str(e))
            finally:
                return set(items)

        else:
            logger.debug(' Error, filepath "%s" does NOT exist!' % file_path)
            return set(items)

    def rename_file(self, old_name, new_name):
        """
        Renames file.

        Args:
            old_name (str): Old file name.
            new_name (str): New file name.

        Returns:
            bool: Whether successful or not.
        """

        logger = getLogger('Lib.rename_file')
        logger.setLevel(self.__log_level)

        logger.debug(' Renaming file "{}" to "{}."'.format(old_name, new_name))
        for retry in range(100):
            try:
                rename(old_name, new_name)
                logger.debug(' Rename succeeded!')
                return True

            except Exception as e:
                logger.error(' Exception: {}'.format(e))
                logger.debug(" Rename failed, retrying...")
                if 'Cannot create a file when that file already exists' in e:
                    self.delete_local_file(file_path=new_name)

        return False

    def size_of_dir(self, dirPath):
        """
        Walks through the directory, getting the cumulative size of the directory
    
        :param dirPath: Directory to walk through to get size.
        :type dirPath: String.
    
        :return: Size in bytes as integer.
        """
    
        logger = getLogger('Lib.size_of_dir')
        logger.setLevel(self.__log_level)
    
        logger.debug(' Getting size of directory "%s"' % dirPath)
    
        sum = 0
        for file in listdir(dirPath):
            sum += path.getsize(dirPath + '\\' + file)
        return sum



class ProcessNameNotFound(Exception):
    pass