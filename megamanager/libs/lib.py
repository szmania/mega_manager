##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###
import psutil
import shlex
import shutil
from hashlib import md5
from logging import getLogger
from numpy import array, load, save
from os import chdir, kill, listdir, path, remove, rename, sep
from platform import system
from re import split, sub
from signal import SIGTERM
from subprocess import call, PIPE, Popen
from threading import Thread
from time import localtime, sleep, strftime, time

__author__ = 'szmania'


class Lib(object):
    def __init__(self, log_level='DEBUG'):
        """
        MegaManager library.

        Args:
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        self.__log_level = log_level


    def _find_procs_by_name(self, name, timeout=None):
        """
        Return a list of processes matching 'name'
        Args:
            name (str): Process name to find.
            timeout (int): timeout in seconds to wait for process to start.

        Returns:
            List: Processes matching name.
        """
        logger = getLogger('Lib._find_procs_by_name')
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
            pass

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            pass

        return found_procs

    def _set_priority_once_proc_starts(self, process_name, priority_class, process_set_priority_timeout):
        """
        Wait for process to start then set priority.
        Args:
            process_name (str): Process name to set priority.
            priority_class (str): priority level. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:

        """
        logger = getLogger('Lib._set_priority_once_proc_starts')
        logger.setLevel(self.__log_level)

        sleep(1)
        t = Thread(target=self._thread_set_priority_once_proc_starts, args=(process_name, priority_class,
                                                                            process_set_priority_timeout, ),
                   name='thread_set_priority_{}'.format(process_name))
        t.start()

    def _set_proc_priority(self, proc, priority_class):
        """
        Set process priority.
        Args:
            proc: psutils process object.
            priority_class (str): Priority level. ie: "BELOW_NORMAL_PRIORITY_CLASS"

        Returns:
            Boolean: Whether successful or not.
        """
        logger = getLogger('Lib._set_proc_priority')
        logger.setLevel(self.__log_level)
        logger.debug(' Setting process "{}" to priority class "{}"'.format(proc.name(), priority_class))

        try:
            if priority_class == 'IDLE_PRIORITY_CLASS':
                if system() == 'Windows':
                    proc.nice(psutil.IDLE_PRIORITY_CLASS)
                else:
                    proc.nice(20)
            elif priority_class == 'BELOW_NORMAL_PRIORITY_CLASS':
                if system() == 'Windows':
                    proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                else:
                    proc.nice(10)
            elif priority_class == 'NORMAL_PRIORITY_CLASS':
                if system() == 'Windows':
                    proc.nice(psutil.NORMAL_PRIORITY_CLASS)
                else:
                    proc.nice(0)
            elif priority_class == 'ABOVE_NORMAL_PRIORITY_CLASS':
                if system() == 'Windows':
                    proc.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
                else:
                    proc.nice(-5)
            elif priority_class == 'HIGH_PRIORITY_CLASS':
                if system() == 'Windows':
                    proc.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    proc.nice(-10)
            elif priority_class == 'REALTIME_PRIORITY_CLASS':
                if system() == 'Windows':
                    proc.nice(psutil.REALTIME_PRIORITY_CLASS)
                else:
                    proc.nice(-20)
            else:
                logger.warning('Error, invalid priority class: {}'.format(priority_class))
                return False

            logger.debug(' Success, set process priority_class to "{}"'.format(priority_class))
            return True

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _thread_set_priority_once_proc_starts(self, process_name, priority_class, process_set_priority_timeout):
        """
        Wait for process to start then set priority.
        Args:
            process_name (str): Process name to set priority.
            priority_class (): priority level. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        """
        logger = getLogger('Lib._thread_set_priority_once_proc_starts')
        logger.setLevel(self.__log_level)

        procs = self._find_procs_by_name(name=process_name, timeout=process_set_priority_timeout)

        for proc in procs:
            self._set_proc_priority(proc=proc, priority_class=priority_class)

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
            for retry in range(10):
                try:
                    remove(file_path)
                    logger.debug(' File deleted!')
                    return True

                except Exception as e:
                    logger.exception(' Exception: {}'.format(e))
                    logger.debug(' Removing of file "{}" FAILED, retrying...'.format(file_path))
        else:
            logger.error(' Cannot delete! Path does not exist: "{}"'.format(file_path))

        return False

    def dump_set_into_numpy_file(self, item_set, file_path):
        """
        Dump set into file for each item on a new line.

        Args:
            item_set (set): Set to dump into file.
            file_path (str): File to dump to.

        Returns:
            Boolean: boolean of whether successful or not
        """

        logger = getLogger('MegaManager_lib.dump_set_into_numpy_file')
        logger.setLevel(self.__log_level)

        logger.debug(' Dumping set into "%s".' % file_path)

        try:
            np_list = array(list(item_set))
            # savez_compressed(file_path, list=npList)
            # savez(file_path, list=npList)
            save(file_path, np_list)
            return True
        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
            return False

    def exec_cmd(self, command, working_dir=None, no_window=False, output_file=None, process_name=None,
                 process_priority_class=None, process_set_priority_timeout=60):
        """
        Execute given command.

        Args:
            command (str): Command to execute.
            working_dir (str): Working directory.
            no_window (bool): No window will be created if true.
            output_file (str): file path to output program output to.
            process_name (str): Process name to set priority level.
            process_priority_class (str): Priority level to set process to. ie: "BELOW_NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
            subprocess object
        """
        logger = getLogger('Lib.exec_cmd')
        logger.setLevel(self.__log_level)
        logger.debug(' Executing command: "%s"' % command)

        try:
            if working_dir:
                chdir(working_dir)

            if process_priority_class:
                self._set_priority_once_proc_starts(process_name=process_name, priority_class=process_priority_class,
                                                    process_set_priority_timeout=process_set_priority_timeout)
            with open(output_file, 'a') as out_file:
                if no_window and system() == 'Windows':
                    CREATE_NO_WINDOW = 0x08000000
                    exit_code = call(shlex.split(command), stdout=out_file, stderr=out_file, creationflags=CREATE_NO_WINDOW)

                else:
                    exit_code = call(shlex.split(command),  stdout=out_file, stderr=out_file)

            if exit_code == 0:
                logger.debug(' Successfully executed command "%s".' % command)
                return True

        except Exception as e:
            logger.warning(' Exception: {}'.format(e))

        logger.error(' Error when running command "%s".' % command)
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

        out = None
        err = None
        if working_dir:
            chdir(working_dir)

        try:
            # out = check_output(shlex.split(command), stderr=STDOUT)
            proc = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)
            (out, err) = proc.communicate()
            if output_file:
                with open(output_file, 'a') as out_file:
                    out_file.write(out)
        except Exception as e:
            logger.warning(' Exception: %s' % str(e))
            return None, None
        return out, err

    def get_file_md5_hash(self, file_path):
        """
        Gets file md5 hash.

        ArgsL
            file_path (str): File path to get md5 has of.

        Returns:
             Str: md5 hash of file.
        """
        logger = getLogger('Lib.get_file_md5_hash')
        logger.setLevel(self.__log_level)
        logger.debug(' Getting md5 hash of file: "{}"'.format(file_path))

        try:
            hash_md5 = md5()
            with open(file_path, "rb") as f:  # Open the file in binary mode
                for chunk in iter(lambda: f.read(4096), b""):  # Read file in chunks of 4096 bytes
                    hash_md5.update(chunk)
            file_md5_hash = hash_md5.hexdigest()
            # file_md5_hash = md5(file_path).hexdigest()
            logger.debug(' md5 hash of file is: "{}"'.format(file_md5_hash))
            return file_md5_hash
        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
            return False

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

    def get_remote_path_from_local_path(self, localPath, localRoot="{sep}".format(sep=sep), remoteRoot="\\"):
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

    def get_items_in_list_with_sub_string(self, list, sub_string):
        """
        Return sub list of list that contain substring.

        :param list: List to find substrings in.
        :type list: List.
        :param sub_string: Substring to find.
        :type sub_string: String.

        :return: List of items that contain subString.
        """

        logger = getLogger('Lib.get_items_in_list_with_sub_string')
        logger.setLevel(self.__log_level)

        subList = []
        for item in list:
            if sub_string in item:
                subList.append(item)
        return subList

    def kill_running_processes_with_name(self, proc_name):
        """
        Kill processes with name.

        Args:
            proc_name (str): Process name.

        :return:
        """

        logger = getLogger('megaManager_lib.kill_running_processes_with_name')
        logger.setLevel(self.__log_level)

        logger.info(' Killing processes with name "%s"' % proc_name)
        try:
            # p = Popen(['ps', '-a'], stdout=PIPE)
            p = Popen(['tasklist', '/v'], stdout=PIPE)
            out, err = p.communicate()

            for line in out.splitlines():
                if line.startswith(proc_name):
                    pid = int(line.split()[1])
                    kill(pid, SIGTERM)

            logger.debug(' Success, all "%s" processes have been killed.' % proc_name)
            return True

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def load_numpy_file_as_set(self, file_path):
        """
        Load file as set splitting each line into a new item.

        Args:
            file_path (str): File to lead.

        Returns:
            Lines in file as a set.
        """
        logger = getLogger('Lib.load_numpy_file_as_set')
        logger.setLevel(self.__log_level)

        items = set()
        if path.isfile(file_path):
            logger.debug(' Loading file as set: {}'.format(file_path))

            try:
                data = load(file=file_path, allow_pickle=False)
                items = set(data.tolist())
            except Exception as e:
                logger.debug(' Exception: %s' % str(e))
            finally:
                return items

        else:
            logger.debug(' Filepath "%s" does NOT exist. Using empty set.' % file_path)
            return items

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
                shutil.move(old_name, new_name)
                logger.debug(' Rename succeeded!')
                return True

            except Exception as e:
                logger.error(' Exception: {}'.format(e))
                logger.debug(" Rename failed, retrying...")
                if 'Cannot create a file when that file already exists' in e:
                    self.delete_local_file(file_path=new_name)
        return False

    def size_of_dir(self, dir_path):
        """
        Walks through the directory, getting the cumulative size of the directory

        :param dir_path: Directory to walk through to get size.
        :type dir_path: String.

        :return: Size in bytes as integer.
        """

        logger = getLogger('Lib.size_of_dir')
        logger.setLevel(self.__log_level)

        logger.debug(' Getting size of directory "%s"' % dir_path)

        sum = 0
        for file in listdir(dir_path):
            sum += path.getsize(path.join(dir_path,file))
        return sum



class ProcessNameNotFound(Exception):
    pass
