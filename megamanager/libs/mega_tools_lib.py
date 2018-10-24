##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from .lib import Lib
from logging import getLogger
from os import chdir, path, remove, rename, walk
from re import findall, split, sub
from random import randint
from tempfile import gettempdir

__author__ = 'szmania'

HOME_DIRECTORY = path.expanduser("~")
MEGA_MANAGER_CONFIG_DIR = HOME_DIRECTORY + "\\.mega_manager"

MEGATOOLS_LOG = MEGA_MANAGER_CONFIG_DIR + '\\logs\\mega_tools.log'
TEMP_LOGFILE_PATH = gettempdir() + '\\megaManager_error_files_%d.tmp' % randint(0, 9999999999)
SCRIPT_DIR = path.dirname(path.realpath(__file__))

class MegaTools_Lib(object):
    def __init__(self, down_speed_limit=None, up_speed_limit=None, log_level='DEBUG', log_file_path=MEGATOOLS_LOG):
        """
        Library for interaction with MegaTools. A tool suite for MEGA.

        Args:
            down_speed_limit (int): Max download speed limit.
            up_speed_limit (int): Max upload speed limit.
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
        """
        self.__downSpeedLimit = down_speed_limit
        self.__up_speed_limit = up_speed_limit
        self.__logLevel = log_level
        self.__mega_tools_log = log_file_path

        self.__lib = Lib(logLevel=log_level)

    def create_remote_dir(self, username, password, remote_path):
        """
        Create remote MEGA directory

        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            remote_path (str): Path to remote directory.

        Returns:
            Bool: Whether successful or not.
        """
        logger = getLogger('MegaTools_Lib.create_remote_dir')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating remote directory for account "{}" in MEGA: "{}"'.format(username, remote_path))
        try:
            cmd = 'megamkdir -u {} -p {} "{}"'.format(username, password, remote_path)

            result = self.__lib.exec_cmd(command=cmd, noWindow=True,
                                         output_file=self.__mega_tools_log)
            # result = self.__lib.exec_cmd(command=cmd, working_dir=self.__mega_tools_dir, noWindow=True,
            #                              output_file=self.__mega_tools_log)
            if not result:
                logger.debug(' Error, could not make directory "{}" for account "{}"!'.format(remote_path, username))
                return False

            logger.debug(' Success, could make directory "{}" for account "{}"!'.format(remote_path, username))
            return True

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def download_all_files_from_account(self, username, password, localRoot, remoteRoot):
        """
        Download all account files.

        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            localRoot (str): Local path to __download file to
            remoteRoot (str): Remote path of file to __download

        Returns:
        """

        logger = getLogger('MegaTools_Lib.download_all_files_from_account')
        logger.setLevel(self.__logLevel)

        logger.debug(' MEGA downloading directory from account "%s" from "%s" to "%s"' % (username, localRoot, remoteRoot))
        # logFile = open(self.__mega_tools_log, 'a')

        # logFile_stdout = open(LOGFILE_STDOUT, 'a')
        temp_logFile_stderr = open(TEMP_LOGFILE_PATH, 'a')

        # chdir('%s' % self.__mega_tools_dir)

        if self.__downSpeedLimit:
            # cmd = 'start "" /B megacopy --download -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.__downSpeedLimit, localRoot, remoteRoot)
            cmd = 'megacopy --download -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (
            username, password, self.__downSpeedLimit, localRoot, remoteRoot)

        else:
            # cmd = 'start "" /B megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (username, password, localRoot,remoteRoot)
            cmd = 'megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (
            username, password, localRoot, remoteRoot)

        result = self.__lib.exec_cmd(command=cmd, noWindow=True, output_file=self.__mega_tools_log)
        # out, err = self.__lib.exec_cmd_and_return_output(command=cmd, workingDir=self.__mega_tools_dir, outputFile=self.__mega_tools_log)

        if result:
            logger.debug(' Success, downloadeded all files from account.')
            return True
        else:
            logger.debug(' Error, could not download all files from account!')
            return False

    def download_file(self, username, password, localFilePath, remoteFilePath):
        """
        Download a remote file from MEGA account.

        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            localFilePath (str): Location to __download file to.
            remoteFilePath (str): Location to __download file from.

        Returns:
            bool: whether successful download or not
        """

        logger = getLogger('MegaManager._download_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, password, localFilePath))

        cmd = 'megaget -u %s -p %s --path "%s" "%s"' % (username, password, localFilePath, remoteFilePath)
        result = self.__lib.exec_cmd(command=cmd, noWindow=True, output_file=self.__mega_tools_log)

        if result:
            logger.debug(' Successfully downloaded file.')
            return True
        else:
            logger.debug(' Error when trying to download file.')
            return False

    def get_file_date_from_megals_line_data(self, line):
        """
        Extract file date from megals line data output.
        example input:
        udtDgR7I    Xz2tWWB5Dmo 0    4405067776 2013-04-10 19:16:02 /Root/bigfile

        Args:
            line (str): line to extract file date from.

        Returns:
            string: File date as string. ie: "2013-04-10 19:16:02"
        """

        logger = getLogger('MegaTools_Lib.get_file_date_from_megals_line_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting file date from "%s"' % line)

        line_split = line.split()

        if len(line_split) > 2:
            remoteFileModifiedDate = line_split[4]
            remoteFileModifiedTime = line_split[5]

            remoteFileModifiedDate_time = '%s %s' % (remoteFileModifiedDate, remoteFileModifiedTime)

            logger.debug(' Success, could find remote file modified date.')
            return remoteFileModifiedDate_time

        logger.warning(' Error, could NOT find remote file modified date!')
        return None

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

        logger = getLogger('MegaTools_Lib.get_file_path_from_megals_line_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting file path from "%s"' % line)
        remote_filePath = None
        try:
            remote_filePath = split(':\d{2} ', line)[1]
        except Exception as e:
            logger.error('Exception: %s' % str(e))
        finally:
            return remote_filePath

    def get_file_size_from_megals_line_data(self, line):
        """
        Extract file size from megals line data output.
        example input:
        udtDgR7I    Xz2tWWB5Dmo 0    4405067776 2013-04-10 19:16:02 /Root/bigfile

        Args:
            line (str): Line to extract file path from.

        Returns:
            string: File size. ie: "4405067776".
        """

        logger = getLogger('MegaTools_Lib.get_file_size_from_megals_line_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting file size from "%s"' % line)

        line_split = line.split()
        if len(line_split) > 2:
            remoteFileSize = line_split[3]
            logger.debug(' Success, remote file size of line "%s" is "%s"' % (line, remoteFileSize))
            return remoteFileSize
        else:
            logger.error(' Error, could not get remote file size from line "%s"' % line)
            return None

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

        # chdir('%s' % self.__mega_tools_dir)

        cmd = 'megadf --free -h --gb -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if err:
            logger.info(str(err))

        if not out == '':
            freeSpace = sub('\r', '', out).rstrip()
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
        logger.setLevel(self.__logLevel)

        cmd = 'megadf --used -h --gb -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if err:
            logger.info(str(err))

        if not out == '':
            usedSpace = sub('\r', '', out).rstrip()
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

        cmd = 'megadf --total -h --gb -u %s -p %s' % (username, password)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if err:
            logger.info(str(err))

        if not out == '':
            totalSpace = sub('\r', '', out).rstrip()
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

        if remotePath:

            cmd = 'megals -lR -u %s -p %s "%s"' % (username, password, remotePath)
            out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

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

        cmd = ['start', '/B', 'megals', '-u', '%s' % username, '-p', '%s' % password, '"%s"' % remoteRoot]
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        dirs = out.split('\r\n')
        dirList = []

        for dir in dirs:
            dirName = sub('%s' % remoteRoot, '', dir)
            if not dirName == '':
                dirList.append(sub('/', '', dirName))

        return dirList

    def get_remote_file_data_recursively(self, username, password, remotePath='/', removeBlankLines=False):
        """
        Get all remote file data as list. This includes file path, modified date/time, file size, file type (file or dir),

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remotePath (str): root path to get remote files from.
            removeBlankLines (bool): If set to true output list will not contain empty strings.
        Returns:
            List: list of remote file data in given remote_path.
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_data_recursively')
        logger.setLevel(self.__logLevel)

        cmd = 'megals -lR -u %s -p %s "%s"' % (username, password, remotePath)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                if removeBlankLines:
                    lines = list(filter(None, lines))  # fastest
                logger.debug(' Success, could get remote file data recursievly.')
                return lines

        logger.warning(str(err))
        return None

    def get_remote_file_modified_date(self, username, password, remotePath):
        """
        Get remote file modified date of equivalent local file path

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            remotePath (str): Remote file path of remote file size to get

        Returns:
             Tuple: Remote file modified data and remote file path
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_modified_date')
        logger.setLevel(self.__logLevel)

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remotePath)
        out, err = self.__lib.exec_cmd_and_return_output(cmd)
        line_split = out.split()

        if len(line_split) > 2:
            remoteFileModifiedDate = line_split[4]
            remoteFileModifiedTime = line_split[5]

            remoteFileModifiedDate_time = '%s %s' % (remoteFileModifiedDate, remoteFileModifiedTime)

            logger.debug(' Success, could find remote file modified date.')
            return remoteFileModifiedDate_time

        logger.warning(' Error, could NOT find remote file modified date!')
        return None

    def get_remote_file_size(self, username, password, remotePath='/'):
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
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

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

        return None

    def get_remote_file_paths_recursively(self, username, password, remote_path='/'):
        """
        Get remote files list.

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remote_path (str): root path to get remote files from.
        Returns:
            List: list of remote files in given remote_path.
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_paths_recursively')
        logger.setLevel(self.__logLevel)

        cmd = 'megals -R -u %s -p %s "%s"' % (username, password, remote_path)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                remote_files = []
                for line in lines:
                    if not line == '' and len(findall("\?", line)) == 0:
                        remote_files.append(line)
                logger.debug(' Success, could get remote file paths.')
                return remote_files

        self.create_remote_dir(username=username, password=password, remote_path=remote_path)
        logger.warning('Warning: {}'.format(err))
        logger.warning('Error in megals output. Returning "None".')
        return None

    def get_remote_subdir_names_only(self, username, password, remotePath):
        """
        Get remote sub directory names only.
        Only the subdirectories immediately under remote_path are gotten.

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
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if not err:
            if not out == '':
                lines = out.split('\r\n')
                logger.debug(' Success, could get remote sub directory names.')
                return lines

        logger.warning(str(err))
        return None

    def remove_remote_file(self, username, password, remoteFilePath):
        """
        Remove remote file.

        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            remoteFilePath (str): remote file path to remove

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.remove_remote_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' %s - %s: Removing remote file "%s"!' % (username, password, remoteFilePath))

        cmd = 'megarm -u %s -p %s "%s"' % (username, password, remoteFilePath)

        result = self.__lib.exec_cmd(command=cmd)

        if result:
            logger.debug(' Success, could remove remote file.')
            return True
        else:
            logger.debug(' Error, could NOT remove remote file!')
            return False

    def upload_local_dir(self, username, password, local_dir, remote_dir):
        """
        Upload directory.

            username (str): username of account to upload to
            password (str): password of account to upload to
            local_dir (str): Local directory to upload
            remote_dir (str): Remote directory to upload to

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.upload_local_dir')
        logger.setLevel(self.__logLevel)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (username, password, local_dir))

        if self.__up_speed_limit:
            cmd = 'megacopy -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.__up_speed_limit, local_dir, remote_dir)
        else:
            cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (username, password, local_dir, remote_dir)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, output_file=self.__mega_tools_log)

        if not err:
            logger.debug(' Success, uploaded local directory: {}'.format(local_dir))
            return True

        logger.warning('Warning: {}'.format(err))
        return False

    def upload_to_account(self, username, password, localRoot, remoteRoot):
        """
        Upload all files to account.

        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            localRoot (str): Local root path of local account files to map with remote root.
            remoteRoot (str): Remote root path of remote accounts to map with local root.

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.upload_to_account')
        logger.setLevel(self.__logLevel)

        logger.debug(' Starting uploading for %s - %s' % (username, password))


        self.upload_local_dir(username=username, password=password, local_dir=localRoot, remote_dir=remoteRoot)
        # for subdir, dirs, files in walk(localRoot):
        #     for file in files:
        #         filePath = path.join(subdir, file)
        #         if path.exists(filePath):
        #             localDirSize = localDirSize + path.getsize(filePath)


        localRoot_adj = sub('\\\\', '/', localRoot)

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remoteRoot)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, output_file=self.__mega_tools_log)

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



