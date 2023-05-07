##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from .lib import Lib
from logging import getLogger
from os import linesep, path, sep
from platform import system
from re import findall, split, sub

__author__ = 'szmania'

HOME_DIRECTORY = "~"
MEGA_MANAGER_CONFIG_DIR = path.join("{HOME_DIRECTORY}".format(HOME_DIRECTORY=HOME_DIRECTORY),".mega_manager")
MEGATOOLS_LOG_PATH = path.join("{MEGA_MANAGER_CONFIG_DIR}".format(
    MEGA_MANAGER_CONFIG_DIR=MEGA_MANAGER_CONFIG_DIR), "logs","mega_tools.log")


class MegaTools_Lib(object):
    def __init__(self, down_speed_limit=None, up_speed_limit=None, log_level='DEBUG', log_file_path=MEGATOOLS_LOG_PATH):
        """
        Library for interaction with MegaTools. A tool suite for MEGA.

        Args:
            log_file_path (str): Log file path for MEGATools
            down_speed_limit (int): Max download speed limit.
            up_speed_limit (int): Max upload speed limit.
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
        """
        self.__mega_tools_log = log_file_path
        self.__downSpeedLimit = down_speed_limit
        self.__up_speed_limit = up_speed_limit
        self.__log_level = log_level

        self.__lib = Lib(log_level=log_level)

    def create_remote_dir(self, username, password, remote_path, process_priority_class, process_set_priority_timeout):
        """
        Create remote MEGA directory

        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            remote_path (str): Path to remote directory.
            process_priority_class (str): Priority level to set process to. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
            Bool: Whether successful or not.
        """
        logger = getLogger('MegaTools_Lib.create_remote_dir')
        logger.setLevel(self.__log_level)

        logger.debug(' Creating remote directory for account "{}" in MEGA: "{}"'.format(username, remote_path))
        try:
            cmd = 'megamkdir -u {} -p {} "{}"'.format(username, password, remote_path)

            process_name = 'megamkdir.exe' if system() == 'Windows' else 'megamkdir'
            result = self.__lib.exec_cmd(command=cmd, no_window=True, output_file=self.__mega_tools_log,
                                         process_name=process_name, process_priority_class=process_priority_class,
                                         process_set_priority_timeout=process_set_priority_timeout)
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

    def download_all_files_from_account(self, username, password, local_root, remote_root, process_set_priority_timeout):
        """
        Download all account files.

        Args:
            username (str): username of account to __download file from
            password (str): password of account to __download file from
            local_root (str): Local path to __download file to
            remote_root (str): Remote path of file to __download
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
        """

        logger = getLogger('MegaTools_Lib.download_all_files_from_account')
        logger.setLevel(self.__log_level)

        logger.debug(' MEGA downloading directory from account "%s" from "%s" to "%s"' % (username, local_root, remote_root))

        if self.__downSpeedLimit:
            cmd = 'megacopy --download -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (
                username, password, self.__downSpeedLimit, local_root, remote_root)

        else:
            cmd = 'megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (
                username, password, local_root, remote_root)

        process_name = 'megacopy.exe' if system() == 'Windows' else 'megacopy'
        result = self.__lib.exec_cmd(command=cmd, no_window=True, output_file=self.__mega_tools_log,
                                     process_priority_class='NORMAL_PRIORITY_CLASS', process_name=process_name,
                                     process_set_priority_timeout=process_set_priority_timeout)

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
        logger.setLevel(self.__log_level)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, password, localFilePath))

        cmd = 'megaget -u %s -p %s --path "%s" "%s"' % (username, password, localFilePath, remoteFilePath)
        process_name = 'megaget.exe' if system() == 'Windows' else 'megaget'
        result = self.__lib.exec_cmd(command=cmd, no_window=True, output_file=self.__mega_tools_log,
                                     process_priority_class='NORMAL_PRIORITY_CLASS', process_name=process_name,
                                     process_set_priority_timeout=self.__process_set_priority_timeout)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)
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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

        remotePath = self.__lib.get_remote_path_from_local_path(localPath=localDirPath, localRoot=localRoot,
                                                                remoteRoot=remoteRoot)

        if remotePath:

            cmd = 'megals -lR -u %s -p %s "%s"' % (username, password, remotePath)
            out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

            lines = out.split(linesep)
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

    def get_remote_dirs(self, username, password, remote_path):
        """
        Get remote directories

        Args:
            username (str): username of account to get remote directories from
            password (str): password of account to get remote directories from
            remote_path (str): Remote root path of remote accounts to map with local root.

        Returns:
            list: returns list of directories
        """

        logger = getLogger('MegaTools_Lib.get_remote_dirs')
        logger.setLevel(self.__log_level)

        logger.debug(' Get remote directories.')

        cmd = ['start', '/B', 'megals', '-u', '%s' % username, '-p', '%s' % password, '"%s"' % remote_path]
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        dirs = out.split(linesep)
        dirList = []

        for dir in dirs:
            dirName = sub('%s' % remote_path, '', dir)
            if not dirName == '':
                dirList.append(sub('/', '', dirName))

        return dirList

    def get_remote_file_data_recursively(self, username, password, remote_path='/', remove_blank_lines=False):
        """
        Get all remote file data as list. This includes file path, modified date/time, file size, file type (file or dir),

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remote_path (str): root path to get remote files from.
            remove_blank_lines (bool): If set to true output list will not contain empty strings.
        Returns:
            List: list of remote file data in given remote_path.
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_data_recursively')
        logger.setLevel(self.__log_level)

        cmd = 'megals -lR -u %s -p %s "%s"' % (username, password, remote_path)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, output_file=self.__mega_tools_log)

        if not err:
            if not out == '':
                lines = out.split(linesep)
                if remove_blank_lines:
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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

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
        logger.setLevel(self.__log_level)

        remotePath = self.__lib.get_remote_path_from_local_path(localPath=localFilePath, localRoot=localRoot,
                                                                remoteRoot=remoteRoot)
        if remotePath:
            remoteFileSize = self.get_remote_file_size(username=username, password=password, remotePath=remotePath)
            return remoteFileSize

        return None

    def get_remote_file_paths_recursively(self, username, password, remote_path='/', process_priority_class=None,
                                          process_set_priority_timeout=60):
        """
        Get remote files list.

        Args:
            username (str): username of MEGA account.
            password (str): password of MEGA account.
            remote_path (str): root path to get remote files from.
            process_priority_class (str): Priority level to set process to. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
            List: list of remote files in given remote_path.
        """
        logger = getLogger('MegaTools_Lib.get_remote_file_paths_recursively')
        logger.setLevel(self.__log_level)

        cmd = 'megals -R -u %s -p %s "%s"' % (username, password, remote_path)

        # out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, output_file=self.__mega_tools_log)

        if not err:
            if not out == '':
                lines = out.split(linesep)
                remote_files = []
                for line in lines:
                    if not line == '' and len(findall("\?", line)) == 0:
                        remote_files.append(line)
                logger.debug(' Success, could get remote file paths.')
                return remote_files

        self.create_remote_dir(username=username, password=password, remote_path=remote_path,
                               process_priority_class=process_priority_class, process_set_priority_timeout=process_set_priority_timeout)
        logger.warning(' Warning: {}'.format(err))
        logger.warning(' Error in megals output. Returning "None".')
        return None

    def get_remote_subdir_names_only(self, username, password, remote_path):
        """
        Get remote sub directory names only.
        Only the subdirectories immediately under remote_path are gotten.

        Args:
            username (str): username of account to get remote directories from
            password (str): password of account to get remote directories from
            remote_path (str): Remote root path of remote accounts to map with local root.

        Returns:
            list: sub directory names.
        """

        logger = getLogger('MegaTools_Lib.get_remote_subdir_names_only')
        logger.setLevel(self.__log_level)

        remote_root = remote_path + '/'
        cmd = 'start /B megals -n -u %s -p %s "%s"' % (username, password, remote_root)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd)

        if not err:
            if not out == '':
                lines = out.split(linesep)
                logger.debug(' Success, could get remote sub directory names.')
                return lines

        logger.warning(str(err))
        return None

    def is_remote_dir(self, username, password, remote_dir_path):
        """
        Determines if remote path is an existing remote direcotry.

        Args:
            username (str): MEGA profile username.
            password (str): MEGA profile password.
            remote_dir_path (str): MEGA profile remote directory path to check for existance.

        Returns:
            Bool: Whether true or not.
        """
        logger = getLogger('MegaTools_Lib.is_remote_dir')
        logger.setLevel(self.__log_level)
        logger.info(' Determining if remote directory path exists: "{}"'.format(remote_dir_path))
        remote_dirs = self.get_remote_dirs(username=username, password=password, remote_path=remote_dir_path)
        if len(remote_dirs) < 1:
            logger.info(' Remote directory path does NOT exist! "{}"'.format(remote_dir_path))
            return False
        logger.info(' Remote directory path does exist: "{}"'.format(remote_dir_path))
        return True

    def is_temp_mega_file(self, file_path):
        """
        Determines if file is temp MEGA file.

        Args:
            file_path (str): File path.

        Returns:
            Bool: Whether successful or not.
        """
        logger = getLogger('MegaTools_Lib.remove_temp_mega_files')
        logger.setLevel(self.__log_level)
        logger.info(' Determining if file is temp mega file: "{}"'.format(file_path))
        try:
            if len(findall('^.*\.megatmp\..*$', file_path)) > 0:
                logger.info(' File is temp mega file: "{}"'.format(file_path))
                return True

            logger.info(' File is NOT temp mega file: "{}"'.format(file_path))
            return False

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def remove_remote_path(self, username, password, remote_file_path, process_priority_class="NORMAL_PRIORITY_CLASS", process_set_priority_timeout=60):
        """
        Remove remote file or directory.

        Args:
            username (str): username of account to upload to
            password (str): password of account to upload to
            remote_file_path (str): remote file path to remove.
            process_priority_class (str): Priority level to set for process. ie: "NORMAL_PRIORITY_CLASS".
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.remove_remote_path')
        logger.setLevel(self.__log_level)

        logger.debug(' %s - %s: Removing remote file "%s".' % (username, password, remote_file_path))

        cmd = 'megarm -u %s -p %s "%s"' % (username, password, remote_file_path)

        process_name = 'megarm.exe' if system() == 'Windows' else 'megarm'
        result = self.__lib.exec_cmd(command=cmd, process_name=process_name, process_priority_class=process_priority_class,
                                     process_set_priority_timeout=process_set_priority_timeout)

        if result:
            logger.debug(' Success, could remove remote file: "{}"'.format(remote_file_path))
            return True
        else:
            logger.debug(' Error, could NOT remove remote file! "{}"'.format(remote_file_path))
            return False

    def upload_local_dir(self, username, password, local_dir, remote_path, process_priority_class=None,
                                          process_set_priority_timeout=60):
        """
        Upload directory.

            username (str): username of account to upload to
            password (str): password of account to upload to
            local_dir (str): Local directory to upload
            remote_path (str): Remote directory to upload to
            process_priority_class (str): Priority level to set process to. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.upload_local_dir')
        logger.setLevel(self.__log_level)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (username, password, local_dir))

        if not self.is_remote_dir(username=username, password=password, remote_dir_path=remote_path):
            self.create_remote_dir(username=username, password=password, remote_path=remote_path,
                                   process_priority_class=process_priority_class,
                                   process_set_priority_timeout=process_set_priority_timeout)

        if self.__up_speed_limit:
            cmd = 'megacopy -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password,
                                                                                        self.__up_speed_limit, local_dir, remote_path)
        else:
            cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (username, password, local_dir, remote_path)

        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, output_file=self.__mega_tools_log)

        if out and not err:
            logger.debug(' Success, uploaded local directory: {}'.format(local_dir))
            return True

        logger.warning(' Warning: {}'.format(err))
        return False

    def upload_to_account(self, username, password, local_root, remote_root, process_priority_class=None,
                                          process_set_priority_timeout=60):
        """
        Upload all files to account.

        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            local_root (str): Local root path of local account files to map with remote root.
            remote_root (str): Remote root path of remote accounts to map with local root.
            process_priority_class (str): Priority level to set process to. ie: "NORMAL_PRIORITY_CLASS"
            process_set_priority_timeout (int): Timeout in seconds to wait for process to start after setting priority.

        Returns:
            boolean: whether successful or not.
        """

        logger = getLogger('MegaTools_Lib.upload_to_account')
        logger.setLevel(self.__log_level)

        logger.debug(' Starting uploading for %s - %s' % (username, password))

        self.upload_local_dir(username=username, password=password, local_dir=local_root, remote_path=remote_root,
                              process_priority_class=process_priority_class,
                              process_set_priority_timeout=process_set_priority_timeout)

        localRoot_adj = sub('\\\\', '/', local_root)

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remote_root)
        out, err = self.__lib.exec_cmd_and_return_output(command=cmd, output_file=self.__mega_tools_log)

        if not err:
            lines = out.split(linesep)
            for line in lines:
                if not line == '':
                    if len(split(':\d{2} ', line)) > 1:
                        remote_filePath = split(':\d{2} ', line)[1]
                        dir_subPath = sub(remote_root, '', remote_filePath)
                        local_dir = localRoot_adj + '/' + dir_subPath
                        remote_dir = remote_root + '/' + dir_subPath
                        if path.exists(local_dir):
                            self.upload_local_dir(username, password, local_dir, remote_dir)

            logger.debug('Success, could upload files to account.')
            return True

        logger.warning(str(err))
        logger.debug(' Error, could NOT upload files to account!')
        return False


class MegaToolsFile(object):
    def __init__(self, file_details, log_level='DEBUG', log_file_path=MEGATOOLS_LOG_PATH):
        """
        Class for Mega Tools files and extracting data about file given mega tools file output using "megals --long".
        For more info: https://megatools.megous.com/man/megals.html

        Args:
            file_details(str): File details line as shown using "megals --long".
                ie: 2FFSiaKZ    Xz2tWWB5Dmo 0          2686 2013-04-15 08:33:47 /Root/directory/file.txt
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
            log_file_path (str): MEGATools log file path.

        """
        self.__log_level = log_level
        self.__mega_tools_file_log = log_file_path



