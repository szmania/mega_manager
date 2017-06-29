##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from logging import getLogger
from os import chdir, path, remove, rename
from re import findall, split, sub
from random import randint
from subprocess import call, PIPE, Popen
from tempfile import gettempdir

__author__ = 'szmania'

MEGATOOLS_LOG = '__megaTools.log'
TEMP_LOGFILE_PATH = gettempdir() + '\\megaManager_error_files_%d.tmp' % randint(0, 9999999999)
SCRIPT_DIR = path.dirname(path.realpath(__file__))

class MegaTools_Lib(object):
    def __init__(self, megaToolsDir, downSpeedLimit=None, upSpeedLimit=None, logLevel='DEBUG'):
        """
        Library for interaction with MegaTools. A tool suite for MEGA.

        :param megaToolsDir: Path to __megaTools directory which includes megaget.exe, megals.exe, mega.copy.
        :type megaToolsDir: string
        :param downSpeedLimit: Max __download speed limit.
        :type downSpeedLimit: Integer.
        :param upSpeedLimit: Max __upload speed limit.
        :type upSpeedLimit: Integer.
        :param logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type logLevel: String.
        """
        self.megaTools_log = MEGATOOLS_LOG

        self.__megaToolsDir = megaToolsDir
        self.downSpeedLimit = downSpeedLimit
        self.upSpeedLimit = upSpeedLimit
        self.logLevel = logLevel

    def download_all_files_from_account(self, username, password, localRoot, remoteRoot):
        """
        Download all account files.

        :param username: username of account to __download file from
        :type username: string
        :param password: password of account to __download file from
        :type password: string
        :param localRoot: Local path to __download file to
        :type localRoot: string
        :param remoteRoot: Remote path of file to __download
        :type remoteRoot: string

        :return :
        """

        logger = getLogger('MegaTools_Lib.download_all_files_from_account')
        logger.setLevel(self.logLevel)

        logger.debug(' MEGA downloading directory from account "%s" from "%s" to "%s"' % (username, localRoot, remoteRoot))
        logFile = open(self.megaTools_log, 'a')

        # logFile_stdout = open(LOGFILE_STDOUT, 'a')
        temp_logFile_stderr = open(TEMP_LOGFILE_PATH, 'a')

        chdir('%s' % self.__megaToolsDir)

        if self.downSpeedLimit:
            cmd = 'start "" /B megacopy --__download -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.downSpeedLimit, localRoot,remoteRoot)
        else:
            cmd = 'start "" /B megacopy --__download -u %s -p %s --local "%s" --remote "%s"' % (username, password, localRoot,remoteRoot)


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

    def download_file(self, username, password, localFilePath, remoteFilePath):
        """
        Download a remote file from MEGA account.

        :param username: username of account to __download file from
        :type username: string
        :param password: password of account to __download file from
        :type password: string
        :param localFilePath: Location to __download file to.
        :type localFilePath: String.
        :param remoteFilePath: Location to __download file from.
        :type remoteFilePath: String.

        :return :
        """

        logger = getLogger('MegaManager._download_file')
        logger.setLevel(self.logLevel)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, password, localFilePath))
        logFile = open(self.megaTools_log, 'a')

        # chdir('%s' % self.__megaToolsDir)
        cmd = 'start /B megaget -u %s -p %s --path "%s" "%s"' % (username, password, localFilePath, remoteFilePath)
        # proc = Popen(cmd)
        # proc = self._exec_cmd(command=cmd, workingDir=self.__megaToolsDir, noWindow=True)
        proc = Popen(cmd, stdout=logFile, stderr=logFile)

        while not proc.poll():
            pass

        logFile.close()

    def _exec_cmd(self, command, workingDir=None, noWindow=False):
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

        logger = getLogger('MegaTools_Lib._exec_cmd')
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

    def _exec_cmd_and_get_output(self, command, workingDir=None):
        """
        Execute given command and return stdout and stderr.

        :param command: Command to execute.
        :type command: String
        :param workingDir: Working directory.
        :type workingDir: String

        :return: Tuple of output and error: stdout and stderr
        """

        logger = getLogger('MegaTools_Lib._exec_cmd')
        logger.setLevel(self.logLevel)

        logger.debug(' Executing command: "%s"' % command)

        if workingDir:
            chdir(workingDir)

        proc = Popen(command, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()

        return out, err

    def get_account_free_space(self, username, password):
        """
        Get account free space in gigabytes

        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string

        :return tuple: Remote directory size and remote directory path
        """

        logger = getLogger('MegaTools_Lib.get_account_used_space')
        logger.setLevel(self.logLevel)

<<<<<<< HEAD
        chdir('%s' % self.__megaToolsDir)
=======
        chdir('%s' % self.megaToolsDir)
>>>>>>> 94ed4e8ae070cc4ce48651224d63dbccaafc9544

        cmd = 'start /B megadf --free -h --gb -u %s -p %s' % (username, password)
        proc = Popen(cmd, stdout=PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info(str(err))

        if not out == '':
            usedSpace = sub('\r', '', out)
            return usedSpace

        return 0

    def get_account_used_space(self, username, password):
        """
        Get account used space in gigabytes

        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string

        :return tuple: Remote directory size and remote directory path
        """

        logger = getLogger('MegaTools_Lib.get_account_used_space')
        logger.setLevel(self.logLevel)

<<<<<<< HEAD
        chdir('%s' % self.__megaToolsDir)
=======
        chdir('%s' % self.megaToolsDir)
>>>>>>> 94ed4e8ae070cc4ce48651224d63dbccaafc9544

        cmd = 'start /B megadf --used -h --gb -u %s -p %s' % (username, password)
        proc = Popen(cmd, stdout=PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info(str(err))

        if not out == '':
            usedSpace = sub('\r', '', out)
            return usedSpace

        return 0

    def get_remote_dir_size(self, username, password, localDirPath, localRoot, remoteRoot):
        """
        Get remote directory sizes of equivalent local file path

        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string
        :param localDirPath: Local directory path of remote file size to get
        :type localDirPath: string
        :param localRoot: Local root path of local account files to map with remote root.
        :type localRoot: String.
        :param remoteRoot: Remote root path of remote accounts to map with local root.
        :type remoteRoot: String.

        :return tuple: Remote directory size and remote directory path
        """

        logger = getLogger('MegaTools_Lib.get_remote_dir_size')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = sub('\\\\', '/', localRoot)
        localFilePath_adj = sub('\\\\', '/', localDirPath)
        postfix = split(LOCAL_ROOT_adj, localFilePath_adj)
        if len(postfix) > 1:
            subPath = postfix[1]

            chdir('%s' % self.__megaToolsDir)

            cmd = 'start /B megals -lnR -u %s -p %s "%s"' % (username, password, remoteRoot + subPath)

            out, err = self._exec_cmd_and_get_output(cmd, workingDir=self.__megaToolsDir)
            lines = out.split('\r\n')
            totalRemoteDirSize = 0
            for line in lines:
                line_split = line.split()
                if len(line_split) > 2:
                    remoteFileSize = line_split[3]
                    if remoteFileSize.isdigit():
                        totalRemoteDirSize = totalRemoteDirSize + int(remoteFileSize)

            return totalRemoteDirSize, remoteRoot + subPath

        return 0, ''

    def get_remote_dirs(self, username, password, remoteRoot):
        """
        Get remote directories

        :param username: username of account to get remote directories from
        :type username: string
        :param password: password of account to get remote directories from
        :type password: string
        :param remoteRoot: Remote root path of remote accounts to map with local root.
        :type remoteRoot: String.

        :return: returns list of directories
        """

        logger = getLogger('MegaTools_Lib.get_remote_dirs')
        logger.setLevel(self.logLevel)

        logger.debug(' Get remote directories.')

        chdir('%s' % self.__megaToolsDir)
        cmd = ['start', '/B', 'megals', '-u', '%s' % username, '-p', '%s' % password, '"%s"' % remoteRoot]
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()

        dirs = out.split('\r\n')
        dirList = []
        for dir in dirs:
            dirName = sub('%s' % remoteRoot, '', dir)
            if not dirName == '':
                dirList.append(sub('/', '', dirName))

        return dirList

    def get_remote_file_modified_date(self, username, password, localFilePath, localRoot, remoteRoot):
        """
        Get remote file modified date of equivalent local file path

        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string
        :param localFilePath: Local file path of remote file size to get
        :type localFilePath: string
        :param localRoot: Local root path of local account files to map with remote root.
        :type localRoot: String.
        :param remoteRoot: Remote root path of remote accounts to map with local root.
        :type remoteRoot: String.

        :return tuple: Remote file modified data and remote file path
        """

        logger = getLogger('MegaTools_Lib.get_remote_file_modified_date')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = sub('\\\\', '/', localRoot)
        localFilePath_adj = sub('\\\\', '/', localFilePath)
        postfix = split(LOCAL_ROOT_adj, localFilePath_adj)

        if len(postfix) > 1:
            subPath = postfix[1]

            chdir('%s' % self.__megaToolsDir)

            cmd = 'start /B megals -ln -u %s -p %s "%s"' % (username, password, remoteRoot + subPath)
            # proc = Popen(cmd, stdout=PIPE, shell=True)
            out, err = self._exec_cmd_and_get_output(cmd, workingDir=self.__megaToolsDir)
            # (out, err) = proc.communicate()
            line_split = out.split()
            if len(line_split) > 2:
                remoteFileModifiedDate = line_split[4]
                remoteFileModifiedTime = line_split[5]

                remoteFileModifiedDate_time = '%s %s' % (remoteFileModifiedDate, remoteFileModifiedTime)

                return remoteFileModifiedDate_time, remoteRoot + subPath

        return 0, ''

    def get_remote_file_size(self, username, password, localFilePath, localRoot, remoteRoot):
        """
        Get remote file sizes of equivalent local file path

        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string
        :param localFilePath: Local file path of remote file size to get
        :type localFilePath: string
        :param localRoot: Local root path of local account files to map with remote root.
        :type localRoot: String.
        :param remoteRoot: Remote root path of remote accounts to map with local root.
        :type remoteRoot: String.

        :return tuple: remote file size and remote file path
        """

        logger = getLogger('MegaManager.get_remote_file_size')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = sub('\\\\', '/', localRoot)
        localFilePath_adj = sub('\\\\', '/', localFilePath)
        postfix = split(LOCAL_ROOT_adj, localFilePath_adj)
        if len(postfix) > 1:
            subPath = postfix[1]

            chdir('%s' % self.__megaToolsDir)

            cmd = 'start /B megals -ln -u %s -p %s "%s"' % (username, password, remoteRoot + subPath)
            proc = Popen(cmd, stdout=PIPE, shell=True)

            (out, err) = proc.communicate()
            line_split = out.split()
            if len(line_split) > 2:
                remoteFileSize = line_split[3]

                return remoteFileSize, remoteRoot + subPath

        return 0, ''

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

        :param username: username of account to get remote directories from
        :type username: string
        :param password: password of account to get remote directories from
        :type password: string
        :param remotePath: Remote root path of remote accounts to map with local root.
        :type remotePath: String.

        :return: List of sub directory names.
        """

        logger = getLogger('MegaTools_Lib.get_remote_subdir_names_only')
        logger.setLevel(self.logLevel)

        remote_root = remotePath + '/'
        cmd = 'start /B megals -n -u %s -p %s "%s"' % (username, password, remote_root)
        proc = Popen(cmd, stdout=PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info(str(err))
        else:
            if not out == '':
                lines = out.split('\r\n')
                return lines
        return []

    def remove_local_incomplete_files(self, username, password, localRoot, remoteRoot):
        """
        Delete incomplete files from account.

        :param username: username for MEGA account
        :type username: string
        :param password: password for MEGA account
        :type password: string
        :param localRoot: Local path to __download file to
        :type localRoot: string
        :param remoteRoot: Remote path of file to __download
        :type remoteRoot: string

        :return:
        """

        logger = getLogger('MegaManager._delete_local_incomplete_files_from_account')
        logger.setLevel(self.logLevel)

        chdir('%s' % self.__megaToolsDir)

        cmd = 'start /B megals -ln -u %s -p %s' % (username, password)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
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

    def remove_remote_file(self, username, password, remoteFilePath):
        """
        Remove remote file.

        Args:
            username (str): username of account to __upload to
            password (str): password of account to __upload to
            remoteFilePath (str): remote file path to remove
        """

        logger = getLogger('MegaTools_Lib.remove_remote_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' %s - %s: Removing remote file "%s"!' % (username, password, remoteFilePath))

        cmd = 'megarm -u %s -p %s "%s"' % (username, password, remoteFilePath)

        out, err = self._exec_cmd(command=cmd, workingDir=self.__megaToolsDir)
        # proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)

        # (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        # logFile.close()


    def upload_local_dir(self, username, password, localDir, remoteDir):
        """
        Upload directory.

        :param username: username of account to __upload to
        :type username: string
        :param password: password of account to __upload to
        :type password: string
        :param localDir: Local directory to __upload
        :type localDir: string
        :param remoteDir: Remote directory to __upload to
        :type remoteDir: string

        :return:
        """

        logger = getLogger('MegaTools_Lib.upload_local_dir')
        logger.setLevel(self.logLevel)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (username, password, localDir))
        logFile = open(self.megaTools_log, 'a')

        chdir('%s' % self.__megaToolsDir)
        if self.upSpeedLimit:
            cmd = 'megacopy -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, self.upSpeedLimit, localDir, remoteDir)
        else:
            cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (username, password, localDir, remoteDir)

        proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)
        # proc = Popen(cmd)
        # proc = Popen(cmd, stdout=logFile, stderr=logFile)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        logFile.close()

    def upload_to_account(self, username, password, localRoot, remoteRoot):
        """
        Upload files to account.

        :param username: username of account to __upload to
        :type username: string
        :param password: password of account to __upload to
        :type password: string
        :param localRoot: Local root path of local account files to map with remote root.
        :type localRoot: String.
        :param remoteRoot: Remote root path of remote accounts to map with local root.
        :type remoteRoot: String.

        :return: returns list of dictionaries holding user and pass
        """

        logger = getLogger('MegaManager.upload_to_account')
        logger.setLevel(self.logLevel)

        logger.debug(' Starting uploading for %s - %s' % (username, password))

        localRoot_adj = sub('\\\\', '/', localRoot)
        chdir('%s' % self.__megaToolsDir)

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remoteRoot)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
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
