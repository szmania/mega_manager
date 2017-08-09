##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from logging import getLogger
from .lib import Lib
from os import chdir, path, remove, rename
from re import findall, split, sub
from random import randint
from subprocess import PIPE, Popen
from tempfile import gettempdir

__author__ = 'szmania'

MEGATOOLS_LOG = '__megaTools.log'
TEMP_LOGFILE_PATH = gettempdir() + '\\megaManager_error_files_%d.tmp' % randint(0, 9999999999)
SCRIPT_DIR = path.dirname(path.realpath(__file__))

class MegaTools_Lib(object):
    def __init__(self, megaToolsDir, downSpeedLimit=None, upSpeedLimit=None, logLevel='DEBUG', logFilePath=MEGATOOLS_LOG):
        """
        Library for interaction with MegaTools. A tool suite for MEGA.

<<<<<<< HEAD
        Args:
            megaToolsDir (str): Path to megaTools directory which includes megaget.exe, megals.exe, mega.copy.
            downSpeedLimit (int): Max download speed limit.
            upSpeedLimit (int): Max upload speed limit.
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
=======
        :param megaToolsDir: Path to __megaTools directory which includes megaget.exe, megals.exe, mega.copy.
        :type megaToolsDir: string
        :param downSpeedLimit: Max __download speed limit.
        :type downSpeedLimit: Integer.
        :param upSpeedLimit: Max __upload speed limit.
        :type upSpeedLimit: Integer.
        :param logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type logLevel: String.
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd
        """
        self.__megaToolsDir = megaToolsDir
        self.__downSpeedLimit = downSpeedLimit
        self.__upSpeedLimit = upSpeedLimit
        self.__logLevel = logLevel
        self.__megaTools_log = logFilePath

<<<<<<< HEAD
        self.__lib = Lib(logLevel=logLevel)
=======
        self.__megaToolsDir = megaToolsDir
        self.downSpeedLimit = downSpeedLimit
        self.upSpeedLimit = upSpeedLimit
        self.logLevel = logLevel
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

    def download_all_files_from_account(self, username, password, localRoot, remoteRoot):
        """
        Download all account files.

<<<<<<< HEAD
        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            localRoot (str): Local path to __download file to
            remoteRoot (str): Remote path of file to __download
=======
        :param username: username of account to __download file from
        :type username: string
        :param password: password of account to __download file from
        :type password: string
        :param localRoot: Local path to __download file to
        :type localRoot: string
        :param remoteRoot: Remote path of file to __download
        :type remoteRoot: string
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        Returns:
        """

        logger = getLogger('MegaTools_Lib.download_all_files_from_account')
<<<<<<< HEAD
        logger.setLevel(self.__logLevel)
=======
        logger.setLevel(self.logLevel)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        logger.debug(' MEGA downloading directory from account "%s" from "%s" to "%s"' % (username, localRoot, remoteRoot))
        # logFile = open(self.__megaTools_log, 'a')

        # logFile_stdout = open(LOGFILE_STDOUT, 'a')
        temp_logFile_stderr = open(TEMP_LOGFILE_PATH, 'a')

<<<<<<< HEAD
        # chdir('%s' % self.__megaToolsDir)

        if self.__downSpeedLimit:
            cmd = 'start "" /B megacopy --__download -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.__downSpeedLimit, localRoot, remoteRoot)
=======
        chdir('%s' % self.__megaToolsDir)

        if self.downSpeedLimit:
            cmd = 'start "" /B megacopy --__download -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.downSpeedLimit, localRoot,remoteRoot)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd
        else:
            cmd = 'start "" /B megacopy --__download -u %s -p %s --local "%s" --remote "%s"' % (username, password, localRoot,remoteRoot)

        result = self.__lib.exec_cmd(command=cmd, workingDir=self.__megaToolsDir, noWindow=True, outputFile=self.__megaTools_log)

<<<<<<< HEAD
        if result:
            logger.debug(' Success, downloadeded all files from account.')
            return True
        else:
            logger.debug(' Error, could not download all files from account!')
            return False
=======
        proc = Popen(cmd, stdout=logFile, stderr=PIPE, shell=True)
        logger.debug(' Executing: %s \n' % (cmd))

        # out, err = proc.communicate()
        # proc.wait()
        while not proc.poll():
            err = proc.stderr.readline()

            # logFile_stderr = open(LOGFILE_STDERR, 'a')

            if err == '':
                break
            logFile.write('%s - %s: %s' % (username, password, err))
            # logFile_stderr.close()

            temp_logFile_stderr.write('%s - %s: %s' % (username, password, err))
            # sleep(10)

        #
        # if self.__removeIncomplete:
        #     self._remove_incomplete_files(TEMP_LOGFILE_PATH)

        output = proc.communicate()[0]
        exitCode = proc.returncode

        # logFile_stderr.close()
        # logFile_stdout.close()
        temp_logFile_stderr.close()
        logFile.close()
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

    def download_file(self, username, password, localFilePath, remoteFilePath):
        """
        Download a remote file from MEGA account.

<<<<<<< HEAD
        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            localFilePath (str): Location to __download file to.
            remoteFilePath (str): Location to __download file from.
=======
        :param username: username of account to __download file from
        :type username: string
        :param password: password of account to __download file from
        :type password: string
        :param localFilePath: Location to __download file to.
        :type localFilePath: String.
        :param remoteFilePath: Location to __download file from.
        :type remoteFilePath: String.
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        Returns:
            bool: whether successful download or not
        """

        logger = getLogger('MegaManager._download_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, password, localFilePath))

<<<<<<< HEAD
        cmd = 'start /B megaget -u %s -p %s --path "%s" "%s"' % (username, password, localFilePath, remoteFilePath)
        result = self.__lib.exec_cmd(command=cmd, workingDir=self.__megaToolsDir,
                                     noWindow=True, outputFile=self.__megaTools_log)
=======
        # chdir('%s' % self.__megaToolsDir)
        cmd = 'start /B megaget -u %s -p %s --path "%s" "%s"' % (username, password, localFilePath, remoteFilePath)
        # proc = Popen(cmd)
        # proc = self._exec_cmd(command=cmd, workingDir=self.__megaToolsDir, noWindow=True)
        proc = Popen(cmd, stdout=logFile, stderr=logFile)

        while not proc.poll():
            pass
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        if result:
            logger.debug(' Successfully downloaded file.')
            return True
        else:
            logger.debug(' Error when trying to download file.')
            return False

    def get_file_extension_from_megals_line_data(self, line):
        """
        Extract file extension from megals line data output.
        example input:
        udtDgR7I    Xz2tWWB5Dmo 0    4405067776 2013-04-10 19:16:02 /Root/bigfile.jpg

        Args:
            line (str): line to extract file extension from.

        Returns:
            string: File extension. ie: "jpg"
        """

        logger = getLogger('MegaTools_Lib.get_file_extension_from_megals_line_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting file extension from "%s"' % line)
        fileExt = None
        try:
            fileExt = path.splitext(split(':\d{2} ', line)[1])[1]
        except Exception as e:
            logger.error('Exception: %s' % str(e))
        finally:
            return fileExt

    def get_file_path_from_megals_line_data(self, line):
        """
        Extract file path from megals line data output.
        example input:
        udtDgR7I    Xz2tWWB5Dmo 0    4405067776 2013-04-10 19:16:02 /Root/bigfile

        Args:
            line (str): line to extract file path from.

        Returns:
            string: File path. ie: "/Root".
        """

        logger = getLogger('MegaTools_Lib.get_file_type_from_megals_line_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting file path from "%s"' % line)
        remote_filePath = None
        try:
            remote_filePath = split(':\d{2} ', line)[1]
        except Exception as e:
            logger.error('Exception: %s' % str(e))
        finally:
            return remote_filePath

    def get_file_type_from_megals_line_data(self, line):
        """
        Extract file type from megals line data output.
        example input:
        udtDgR7I    Xz2tWWB5Dmo 0    4405067776 2013-04-10 19:16:02 /Root/bigfile

        Args:
            line (str): line to extract file type from.

        Returns:
            string: File type as integer. 0 = file, 1 = directory, 2 = MEGA account system file ie: "/Root".
        """

        logger = getLogger('MegaTools_Lib.get_file_type_from_megals_line_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting file type from "%s"' % line)
        remote_type = None
        try:
            remote_type = line.split()[2]
        except Exception as e:
            logger.error('Exception: %s' % str(e))
        finally:
            return remote_type

    def get_account_free_space(self, username, password):
        """
        Get account free space in gigabytes

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account

        Returns:
             int: Free space of account in gigabytes.
        """

        logger = getLogger('MegaTools_Lib.get_account_used_space')
        logger.setLevel(self.__logLevel)

<<<<<<< HEAD
        # chdir('%s' % self.__megaToolsDir)
=======
<<<<<<< HEAD
        chdir('%s' % self.__megaToolsDir)
=======
        chdir('%s' % self.megaToolsDir)
>>>>>>> 94ed4e8ae070cc4ce48651224d63dbccaafc9544
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        cmd = 'start /B megadf --free -h --gb -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if err:
            logger.info(str(err))

        if not out == '':
            freeSpace = out.rstrip()
            # freeSpace = sub('\r', '', out)
            logger.debug(' Success, could get account free space.')
            return freeSpace
        logger.debug(' Error, could NOT get account free space!')
        return 0

    def get_account_used_space(self, username, password):
        """
        Get account used space in gigabytes

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account

        Returns:
             int: Used space of account in gigabytes.
        """

        logger = getLogger('MegaTools_Lib.get_account_used_space')
<<<<<<< HEAD
        logger.setLevel(self.__logLevel)
=======
        logger.setLevel(self.logLevel)

<<<<<<< HEAD
        chdir('%s' % self.__megaToolsDir)
=======
        chdir('%s' % self.megaToolsDir)
>>>>>>> 94ed4e8ae070cc4ce48651224d63dbccaafc9544
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        cmd = 'start /B megadf --used -h --gb -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if err:
            logger.info(str(err))

        if not out == '':
            usedSpace = out.rstrip()
            # usedSpace = sub('\r', '', out)
            logger.debug(' Success, could get account free space.')
            return usedSpace
        logger.debug(' Error, could NOT get account free space!')
        return None

    def get_account_total_space(self, username, password):
        """
        Get account total space in gigabytes

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account

        Returns:
             int: Total space of account in gigabytes.
        """

        logger = getLogger('MegaTools_Lib.get_account_total_space')
        logger.setLevel(self.__logLevel)

        cmd = 'start /B megadf --total -h --gb -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if err:
            logger.info(str(err))

        if not out == '':
            totalSpace = out.rstrip()
            # totalSpace = sub('\r', '', out)
            logger.debug(' Success, could get account total space.')
            return totalSpace
        logger.debug(' Error, could NOT get account total space!')
        return None

    def get_remote_dir_size(self, username, password, localDirPath, localRoot, remoteRoot):
        """
        Get remote directory sizes of equivalent local file path

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            localDirPath (str): Local directory path of remote file size to get
            localRoot (str): Local root path of local account files to map with remote root.
            remoteRoot (str): Remote root path of remote accounts to map with local root.

        Returns:
             tuple: Remote directory size and remote directory path
        """

        logger = getLogger('MegaTools_Lib.get_remote_dir_size')
        logger.setLevel(self.__logLevel)

        remotePath = self.__lib.get_remote_path_from_local_path(localPath=localDirPath, localRoot=localRoot,
                                                                remoteRoot=remoteRoot)

<<<<<<< HEAD
        if remotePath:
=======
            chdir('%s' % self.__megaToolsDir)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

            cmd = 'start /B megals -lR -u %s -p %s "%s"' % (username, password, remotePath)
            out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

<<<<<<< HEAD
=======
            out, err = self._exec_cmd_and_get_output(cmd, workingDir=self.__megaToolsDir)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd
            lines = out.split('\r\n')
            totalRemoteDirSize = 0
            for line in lines:
                line_split = line.split()
                if len(line_split) > 2:
                    remoteFileSize = line_split[3]
                    if remoteFileSize.isdigit():
                        totalRemoteDirSize = totalRemoteDirSize + int(remoteFileSize)

            logger.debug(' Success, could get remote directory size.')
            return totalRemoteDirSize

        logger.debug(' Error, could NOT get remote directory size!')
        return None

    def get_remote_dirs(self, username, password, remoteRoot):
        """
        Get remote directories

        Args:
            username (str): username of account to get remote directories from
            password (str): password of account to get remote directories from
            remoteRoot (str): Remote root path of remote accounts to map with local root.

        Returns:
            list: returns list of directories
        """

        logger = getLogger('MegaTools_Lib.get_remote_dirs')
        logger.setLevel(self.__logLevel)

        logger.debug(' Get remote directories.')

        chdir('%s' % self.__megaToolsDir)
        cmd = ['start', '/B', 'megals', '-u', '%s' % username, '-p', '%s' % password, '"%s"' % remoteRoot]
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        dirs = out.split('\r\n')
        dirList = []

        for dir in dirs:
            dirName = sub('%s' % remoteRoot, '', dir)
            if not dirName == '':
                dirList.append(sub('/', '', dirName))

        return dirList

    def get_remote_file_data_recursively(self, username, password, remotePath='/'):
        """
        Get all remote file data as list. This includes file path, modified date/time, file size, file type (file or dir),

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remotePath (str): root path to get remote files from.
        Returns:
            list of remote file data in given remotePath.
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_data_recursively')
        logger.setLevel(self.__logLevel)

        cmd = 'megals -lR -u %s -p %s "%s"' % (username, password, remotePath)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                logger.debug(' Success, could get remote file data recursievly.')
                return lines

        logger.warning(str(err))
        return None

    def get_remote_file_modified_date(self, username, password, localFilePath, localRoot, remoteRoot):
        """
        Get remote file modified date of equivalent local file path

<<<<<<< HEAD
        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            localFilePath (str): Local file path of remote file size to get
            localRoot (str): Local root path of local account files to map with remote root.
            remoteRoot (str): Remote root path of remote accounts to map with local root.

        Returns:
             tuple: Remote file modified data and remote file path
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_modified_date')
        logger.setLevel(self.__logLevel)

        remotePath = self.__lib.get_remote_path_from_local_path(localPath=localFilePath, localRoot=localRoot,
                                                                remoteRoot=remoteRoot)
        if remotePath:
            cmd = 'start /B megals -ln -u %s -p %s "%s"' % (username, password, remotePath)
            out, err = self.__lib.exec_cmd_and_return_output(cmd, workingDir=self.__megaToolsDir)
=======
            chdir('%s' % self.__megaToolsDir)

            cmd = 'start /B megals -ln -u %s -p %s "%s"' % (username, password, remoteRoot + subPath)
            # proc = Popen(cmd, stdout=PIPE, shell=True)
            out, err = self._exec_cmd_and_get_output(cmd, workingDir=self.__megaToolsDir)
            # (out, err) = proc.communicate()
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd
            line_split = out.split()

            if len(line_split) > 2:
                remoteFileModifiedDate = line_split[4]
                remoteFileModifiedTime = line_split[5]

                remoteFileModifiedDate_time = '%s %s' % (remoteFileModifiedDate, remoteFileModifiedTime)

                logger.debug(' Success, could find remote file modified date.')
                return remoteFileModifiedDate_time

        logger.debug(' Error, could NOT find remote file modified date!')
        return None

    def get_remote_file_size(self, username, password, remotePath):
        """
        Get remote file size in bytes of given remote path.

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            remotePath (str): remote path of file to get size for

        Returns:
             int: remote file size
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_size')
        logger.setLevel(self.__logLevel)

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remotePath)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        line_split = out.split()
        if len(line_split) > 2:
            remoteFileSize = line_split[3]
            logger.debug(' Success, remote file size for path "%s" is "%s"' % (remotePath, remoteFileSize))
            return int(remoteFileSize)
        else:
            logger.error(' Error, could not get remote file size of path "%s"' % remotePath)
            return None


    def get_remote_file_size_from_local_path(self, username, password, localFilePath, localRoot, remoteRoot):
        """
        Get remote file sizes of equivalent local file path

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            localFilePath (str): Local file path of remote file size to get
            localRoot (str): Local root path of local account files to map with remote root.
            remoteRoot (str): Remote root path of remote accounts to map with local root.s

        Returns:
             int: remote file size
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_size_from_local_path')
        logger.setLevel(self.__logLevel)

        remotePath = self.__lib.get_remote_path_from_local_path(localPath=localFilePath, localRoot=localRoot,
                                                                remoteRoot=remoteRoot)
        if remotePath:
            remoteFileSize = self.get_remote_file_size(username=username, password=password, remotePath=remotePath)
            return remoteFileSize

<<<<<<< HEAD
        return None
=======
            chdir('%s' % self.__megaToolsDir)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

    def get_remote_file_paths_recursively(self, username, password, remotePath='/'):
        """
        Get remote files list.

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remotePath (str): root path to get remote files from.
        Returns:
            list of remote files in given remotePath.
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_paths_recursively')
        logger.setLevel(self.__logLevel)

        cmd = 'megals -R -u %s -p %s "%s"' % (username, password, remotePath)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                remoteFiles = []
                for line in lines:
                    if not line == '' and len(findall("\?", line)) == 0:
                        remoteFiles.append(line)
                logger.debug(' Success, could get remote file paths.')
                return remoteFiles

        logger.warning(str(err))
        return None

<<<<<<< HEAD
    def get_remote_files(self, username, password, remotePath='/Root'):
        """
        Get remote files list.

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remotePath (str): root path to get remote files from.
        Returns:
            list of remote files in given remotePath.
        """

        cmd = 'megals -R -u %s -p %s "%s"' % (username, password, remotePath)

        out, err = self._exec_cmd_and_get_output(command=cmd, workingDir=self.__megaToolsDir)
        # proc = Popen(cmd, stdout=PIPE, shell=True)
        #
        # (out, err) = proc.communicate()
        lines = out.split('\r\n')

        remoteFiles = []
        for line in lines:
            if not line == '' and len(findall("\?", line)) == 0:
                remoteFiles.append(line)

        return remoteFiles

=======
>>>>>>> 94ed4e8ae070cc4ce48651224d63dbccaafc9544
    def get_remote_subdir_names_only(self, username, password, remotePath):
        """
        Get remote sub directory names only.
        Only the subdirectories immediately under remotePath are gotten.

        Args:
            username (str): username of account to get remote directories from
            password (str): password of account to get remote directories from
            remotePath (str): Remote root path of remote accounts to map with local root.

        Returns:
            list: sub directory names.
        """

        logger = getLogger('MegaTools_Lib.get_remote_subdir_names_only')
        logger.setLevel(self.__logLevel)

        remote_root = remotePath + '/'
        cmd = 'start /B megals -n -u %s -p %s "%s"' % (username, password, remote_root)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                logger.debug(' Success, could get remote sub directory names.')
                return lines

        logger.warning(str(err))
        return None

    def remove_local_incomplete_files(self, username, password, localRoot, remoteRoot):
        """
        Delete incomplete files from account.

<<<<<<< HEAD
        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            localRoot (str): Local path to __download file to
            remoteRoot (str): Remote path of file to __download
=======
        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string
        :param localRoot: Local path to __download file to
        :type localRoot: string
        :param remoteRoot: Remote path of file to __download
        :type remoteRoot: string
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        Returns:
        """

        logger = getLogger('MegaManager._delete_local_incomplete_files_from_account')
<<<<<<< HEAD
        logger.setLevel(self.__logLevel)
=======
        logger.setLevel(self.logLevel)

        chdir('%s' % self.__megaToolsDir)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        cmd = 'start /B megals -ln -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                for line in lines:
                    line_split = line.split()
                    if len(line_split) > 2:
                        remoteFileSize = line_split[3]
                        if remoteFileSize.isdigit():
                            line_split = line.split('/')
                            if len(line_split) > 1:
                                remoteFilePath = '/' + '/'.join(line_split[1:])
                                if remoteRoot in remoteFilePath:
                                    remote_root = remoteRoot.replace('/', '\\')
                                    local_root = localRoot
                                    conv_remoteFilePath = remoteFilePath.replace('/', '\\')
                                    localFilePath = conv_remoteFilePath.replace(remote_root, local_root)
                                    if path.exists(localFilePath) and path.isfile(localFilePath):
                                        localFileSize = path.getsize(localFilePath)
                                        if localFileSize < int(remoteFileSize):
                                            logger.debug(' File incomplete. Deleting file "%s"' % localFilePath)
                                            try:
                                                rename(localFilePath, localFilePath)
                                                remove(localFilePath)
                                            except OSError as e:
                                                logger.debug(' Access-error on file "' + localFilePath + '"! \n' + str(e))

                logger.debug(' Success, removed local incomplete files.')
                return True
        logger.warning(str(err))
        return False

    def remove_remote_file(self, username, password, remoteFilePath):
        """
        Remove remote file.

        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            remoteFilePath (str): remote file path to remove

<<<<<<< HEAD
        Returns:
            boolean: whether successful or not.
=======
        for line in lines:
            line_split = line.split()
            if len(line_split) > 2:
                remoteFileSize = line_split[3]
                if remoteFileSize.isdigit():
                    line_split = line.split('/')
                    if len(line_split) > 1:
                        remoteFilePath = '/' + '/'.join(line_split[1:])
                        if remoteRoot in remoteFilePath:
                            remote_root = remoteRoot.replace('/', '\\')
                            local_root = localRoot
                            conv_remoteFilePath = remoteFilePath.replace('/', '\\')
                            localFilePath = conv_remoteFilePath.replace(remote_root, local_root)
                            if path.exists(localFilePath) and path.isfile(localFilePath):
                                localFileSize = path.getsize(localFilePath)
                                if localFileSize < int(remoteFileSize):
                                    logger.debug(' File incomplete. Deleting file "%s"' % localFilePath)
                                    try:
                                        rename(localFilePath, localFilePath)
                                        remove(localFilePath)
                                    except OSError as e:
                                        logger.debug(' Access-error on file "' + localFilePath + '"! \n' + str(e))

    def remove_remote_file(self, username, password, remoteFilePath):
        """
        Remove remote file.

        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            remoteFilePath (str): remote file path to remove
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd
        """

        logger = getLogger('MegaTools_Lib.remove_remote_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' %s - %s: Removing remote file "%s"!' % (username, password, remoteFilePath))

        cmd = 'megarm -u %s -p %s "%s"' % (username, password, remoteFilePath)

<<<<<<< HEAD
        result = self.__lib.exec_cmd(command=cmd, workingDir=self.__megaToolsDir)

        if result:
            logger.debug(' Success, could remove remote file.')
            return True
        else:
            logger.debug(' Error, could NOT remove remote file!')
            return False
=======
        out, err = self._exec_cmd(command=cmd, workingDir=self.__megaToolsDir)
        # proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)

        # (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        # logFile.close()

>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

    def upload_local_dir(self, username, password, localDir, remoteDir):
        """
        Upload directory.

<<<<<<< HEAD
            username (str): username of account to upload to
            password (str): password of account to upload to
            localDir (str): Local directory to upload
            remoteDir (str): Remote directory to upload to
=======
        :param username: username of account to __upload to
        :type username: string
        :param password: password of account to __upload to
        :type password: string
        :param localDir: Local directory to __upload
        :type localDir: string
        :param remoteDir: Remote directory to __upload to
        :type remoteDir: string
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.upload_local_dir')
        logger.setLevel(self.__logLevel)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (username, password, localDir))

<<<<<<< HEAD
        if self.__upSpeedLimit:
            cmd = 'megacopy -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.__upSpeedLimit, localDir, remoteDir)
=======
        chdir('%s' % self.__megaToolsDir)
        if self.upSpeedLimit:
            cmd = 'megacopy -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.upSpeedLimit, localDir, remoteDir)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd
        else:
            cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (username, password, localDir, remoteDir)


        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir, outputFile=self.__megaTools_log)
        # proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)
        # proc = Popen(cmd)
        # proc = Popen(cmd, stdout=logFile, stderr=logFile)

        # (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        # logFile.close()

        if not err:
            logger.debug(' Success, uploaded local dir.')
            return True

        logger.warning(str(err))
        return False

    def upload_to_account(self, username, password, localRoot, remoteRoot):
        """
        Upload all files to account.

<<<<<<< HEAD
        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            localRoot (str): Local root path of local account files to map with remote root.
            remoteRoot (str): Remote root path of remote accounts to map with local root.
=======
        :param username: username of account to __upload to
        :type username: string
        :param password: password of account to __upload to
        :type password: string
        :param localRoot: Local root path of local account files to map with remote root.
        :type localRoot: String.
        :param remoteRoot: Remote root path of remote accounts to map with local root.
        :type remoteRoot: String.
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.upload_to_account')
        logger.setLevel(self.__logLevel)

        logger.debug(' Starting uploading for %s - %s' % (username, password))

        localRoot_adj = sub('\\\\', '/', localRoot)
<<<<<<< HEAD
=======
        chdir('%s' % self.__megaToolsDir)
>>>>>>> b35cd581f1b922abdb239ce8e6e4edd74ffb48cd

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remoteRoot)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__megaToolsDir, outputFile=self.__megaTools_log)

        if not err:
            lines = out.split('\r\n')
            for line in lines:
                if not line == '':
                    if len(split(':\d{2} ', line)) > 1:
                        remote_filePath = split(':\d{2} ', line)[1]
                        dir_subPath = sub(remoteRoot, '', remote_filePath)
                        local_dir = localRoot_adj + '/' + dir_subPath
                        remote_dir = remoteRoot + '/' + dir_subPath
                        if path.exists(local_dir):
                            self.upload_local_dir(username, password, local_dir, remote_dir)

            logger.debug('Success, could upload files to account.')
            return True

        logger.warning(str(err))
        logger.debug(' Error, could NOT upload files to account!')
        return False


class MegaToolsFile(object):
    def __init__(self, mtFileDetails, logLevel='DEBUG', logFilePath=MEGATOOLS_LOG):
        """
        Class for Mega Tools files and extracting data about file given mega tools file output using "megals --long".
        For more info: https://megatools.megous.com/man/megals.html

        Args:
            mtFileDetails(str): File details line as shown using "megals --long".
                ie: 2FFSiaKZ    Xz2tWWB5Dmo 0          2686 2013-04-15 08:33:47 /Root/directory/file.txt
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
            logFilePath (str): Logging file path.

        """
        self.__logLevel = logLevel
        self.__megaToolsFile_log = logFilePath



