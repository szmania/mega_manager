###
# Created by: Curtis Szmania
# Date: 10/1/2016
# Initial Creation
###
# Modified by: Curtis Szmania
# Date: 5/21/2017
# Pep8 compliant.
###


from argparse import ArgumentParser
from logging import DEBUG, getLogger, FileHandler, Formatter, StreamHandler
from os import chdir, getpid, listdir, path, remove, rename, walk
from psutil import IDLE_PRIORITY_CLASS, Process
from random import randint
from re import findall, split, sub
from shutil import copyfile, rmtree
from subprocess import call, PIPE, Popen
from sys import stdout
from tempfile import gettempdir
from threading import Thread
from time import sleep, time


__author__ = 'szmania'


MEGAMANAGER_CONFIG = 'megaManager.cfg'

MEGA_ACCOUNTS_DATA = "self.megaAccounts_DATA.txt"
MEGATOOLS_PATH = ''
MEGA_ACCOUNTS = ''
LOCAL_ROOT = ''
REMOTE_ROOT = ''

WORKING_DIR = path.dirname(path.realpath(__file__))

TEMP_LOGFILE_PATH = gettempdir() + '\\%d.tmp' % randint(0, 9999999999)

COMPRESSED_IMAGES_FILE =  WORKING_DIR + "\\compressed_images.tmp"
UNABLE_TO_COMPRESS_IMAGES_FILE =  WORKING_DIR + "\\unable_to_compress_images.tmp"
COMPRESSED_VIDEOS_FILE =  WORKING_DIR + "\\compressed_videos.tmp"
UNABLE_TO_COMPRESS_VIDEOS_FILE = WORKING_DIR + "\\unable_to_compress_videos.tmp"


LOGFILE_STDOUT = path.dirname(path.realpath(__file__)) + '\mega_stdout.log'
LOGFILE_STDERR = path.dirname(path.realpath(__file__)) + '\mega_stderr.log'
LOGFILE_MEGA = path.dirname(path.realpath(__file__)) + '\megaManager_log.log'



class MegaManager(object):
    def __init__(self, **kwargs):
        self.threads = []
        self.download = None
        self.upload = None
        self.removeRemote = None
        self.compress = None
        self.compressImages = None
        self.compressVideos = None
        self.logLevel = None
        
        if path.getsize(LOGFILE_MEGA) > 10000000:
            try:
                remove(LOGFILE_MEGA)
            except Exception as e:
                pass


        self._assign_attributes(**kwargs)


        self._setup_logger(LOGFILE_MEGA)

        self._load_config_file()


    def _assign_attributes(self, **kwargs):
        """
        Assign argumetns to class attributes.

        :param kwargs:  Dictionary of argument.s
        :type kwargs: Dictionary
        
        :return:
        """



        for key, value in kwargs.items():
            setattr(self, key, value)


    def _setup_logger(self, logFile):
        """
        Logger setup.

        :param logFile:  Log file path.
        :type logFile: string
        """

        root = getLogger()
        root.setLevel(DEBUG)

        self.handler = FileHandler(logFile)
        formatter = Formatter('%(levelname)s:%(name)s:%(message)s')

        # formatter = logging.Formatter(fmt='%(message)s', datefmt='')
        self.handler.setLevel(DEBUG)
        self.handler.setFormatter(formatter)

        ch = StreamHandler(stdout)
        ch.setLevel(self.logLevel)
        ch.setFormatter(formatter)

        root.addHandler(self.handler)
        root.addHandler(ch)

        logger = getLogger('MegaManager._setup_logger')
        logger.setLevel(self.logLevel)

        logger.info(' Logging to %s' % LOGFILE_MEGA)


    def _load_config_file(self):
        """
        Load config file.

        """


        logger = getLogger('MegaManager._load_config_file')
        logger.setLevel(self.logLevel)

        logger.debug(' Loading megaManager.cfg file.')

        with open(MEGAMANAGER_CONFIG, "r") as ins:
            for line in ins:
                if '=' in line:
                    value = split('=', line)[1].strip()
                    if line.startswith('MEGATOOLS_PATH'):
                        self.megaToolsPath= value
                    elif line.startswith('MEGA_ACCOUNTS') and not line.startswith('MEGA_ACCOUNTS_DATA'):
                        self.megaAccounts = value
                    elif line.startswith('MEGA_ACCOUNTS_DATA'):
                        self.megaAccountsData = value
                    elif line.startswith('LOCAL_ROOT'):
                        self.localRoot = value
                    elif line.startswith('REMOTE_ROOT'):
                        self.remoteRoot = value


    def _load_compressed_lists(self):
        """
        Load compressed and uncompressed file lists from *.tmp.
        """

        logger = getLogger('MegaManager._load_compressed_lists')
        logger.setLevel(self.logLevel)

        logger.debug(' Loading %s file.' % COMPRESSED_IMAGES_FILE)
        self.compressedImageFiles = []

        if path.exists('%s\\%s' % (WORKING_DIR, COMPRESSED_IMAGES_FILE)):
            with open('%s\\%s' % (WORKING_DIR, COMPRESSED_IMAGES_FILE), "r") as ins:
                self.compressedImageFiles = [line.rstrip('\n') for line in ins]

        logger.debug(' Loading %s file.' % UNABLE_TO_COMPRESS_IMAGES_FILE)
        self.unableToCompressImageFiles = []

        if path.exists('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_IMAGES_FILE)):
            with open('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_IMAGES_FILE), "r") as ins:
                self.unableToCompressImageFiles = [line.rstrip('\n') for line in ins]


        logger.debug(' Loading %s file.' % COMPRESSED_VIDEOS_FILE)
        self.compressedVideoFiles = []

        if path.exists('%s\\%s' % (WORKING_DIR, COMPRESSED_VIDEOS_FILE)):
            with open('%s\\%s' % (WORKING_DIR, COMPRESSED_VIDEOS_FILE), "r") as ins:
                self.compressedVideoFiles = [line.rstrip('\n') for line in ins]

        logger.debug(' Loading %s file.' % UNABLE_TO_COMPRESS_IMAGES_FILE)
        self.unableToCompressVideoFiles = []

        if path.exists('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_VIDEOS_FILE)):
            with open('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_VIDEOS_FILE), "r") as ins:
                self.unableToCompressVideoFiles = [line.rstrip('\n') for line in ins]



    def _dump_compressed_image_file_list(self):
        """
        Dump compressed image file list to *.tmp file.
        """

        logger = getLogger('MegaManager._dump_compressed_image_file_list')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.compressedImageFiles to %s file.' % COMPRESSED_IMAGES_FILE)

        compressedList_file = open('%s' % (COMPRESSED_IMAGES_FILE), 'w')

        for compressedFilePath in self.compressedImageFiles:
            compressedList_file.write("%s\n" % compressedFilePath)

    def _dump_compressed_video_fle_list(self):
        """
        Dump compressed video file list to *.tmp file.
        """

        logger = getLogger('MegaManager._dump_compressed_video_fle_list')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.compressedVideoFiles to %s file.' % COMPRESSED_VIDEOS_FILE)

        compressedList_file = open('%s' % (COMPRESSED_VIDEOS_FILE), 'w')

        for compressedFilePath in self.compressedVideoFiles:
            compressedList_file.write("%s\n" % compressedFilePath)


    def _dump_unable_to_compress_image_file_list(self):
        """
        Dump unable to compress image file list to *.tmp file.
        """

        logger = getLogger('MegaManager._dump_unable_to_compress_image_file_list')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.unableToCompressImageFiles to %s file.' % UNABLE_TO_COMPRESS_IMAGES_FILE)

        unCompressedList_file = open('%s' % (UNABLE_TO_COMPRESS_IMAGES_FILE), 'w')

        for unCompressedFilePath in self.unableToCompressImageFiles:
            unCompressedList_file.write("%s\n" % unCompressedFilePath)


    def _dump_unable_to_compress_video_file_list(self):
        """
        Dump unable to compress video file list to *.tmp file.
        """

        logger = getLogger('MegaManager._dump_unable_to_compress_video_file_list')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.unableToCompressVideoFiles to %s file.' % UNABLE_TO_COMPRESS_VIDEOS_FILE)

        unCompressedList_file = open('%s' % (UNABLE_TO_COMPRESS_VIDEOS_FILE), 'w')

        for unCompressedFilePath in self.unableToCompressImageFiles:
            unCompressedList_file.write("%s\n" % unCompressedFilePath)

    def run(self):
        """
        Run MegaManager tasks.
        """

        logger = getLogger('MegaManager.run')
        logger.setLevel(self.logLevel)

        logger.debug(' Running megaManager.')

        try:
            self._create_thread_create_mega_accounts_data_file()

            self._create_threads_local_unfinished_file_remover()

            if self.download:
                self._create_threads_download()
            if self.upload:
                self._create_threads_upload()
            if self.removeRemote:
                self._create_threads_remote_file_removal()

            if self.compress:
                self._create_threads_compress_image_files()
                self._create_threads_compress_video_files()
            elif self.compressImages:
                self._create_threads_compress_image_files()
            elif self.compressVideos:
                self._create_threads_compress_video_files()

            self._wait_for_threads_to_finish()

        except Exception as e:
            logger.debug(' Exception: ' + str(e))
            self._tear_down()

    def _create_thread_create_mega_accounts_data_file(self):
        """
        Create thread to create self.megaAccountsData file.
        """

        logger = getLogger('MegaManager._create_thread_create_mega_accounts_data_file')
        logger.setLevel(self.logLevel)

        logger.debug(' Creating thread to create "%s" file.' % self.megaAccountsData)

        t = Thread(target=self._create_mega_accounts_data_file, name='thread_createself.megaAccountsData_file')
        self.threads.append(t)
        t.start()


    def _create_threads_local_unfinished_file_remover(self):
        """
        Create threads to remove unfinished local downloaded files.
        """

        logger = getLogger('MegaManager._create_threads_local_unfinished_file_remover')
        logger.setLevel(self.logLevel)

        logger.debug(' Creating threads to remove unfinished files.')

        foundUserPass = self._get_accounts_user_pass()

        for account in foundUserPass:
            t_unfinishedFileRemover = Thread(target=self._delete_local_incomplete_files_from_account, args=(account['user'], account['pass'],), name='thread_unfinishedFileRemover_%s' % account['user'])
            self.threads.append(t_unfinishedFileRemover)
            t_unfinishedFileRemover.start()

            sleep(self._get_sleep_time())

    def _create_threads_download(self):
        """
        Create threads to download files.
        """

        logger = getLogger('MegaManager._create_threads_download')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating threads to download files from MEGA, for each account.')

        foundUserPass = self._get_accounts_user_pass()

        for account in foundUserPass:

            t = Thread(target=self._download_account_files, args=(account['user'], account['pass'],), name='thread_download_%s' % account['user'])
            self.threads.append(t)
            t.start()

            sleep(self._get_sleep_time())


    def _create_threads_upload(self):
        """
        Create threads to upload files.
        """

        logger = getLogger('MegaManager._create_threads_upload')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating threads to upload files to MEGA, for each account.')

        foundUserPass = self._get_accounts_user_pass()

        for account in foundUserPass:

            t = Thread(target=self._upload_to_account, args=(account['user'], account['pass'],), name='thread_upload_%s' % account['user'])
            self.threads.append(t)
            t.start()
            sleep(self._get_sleep_time())


    def _create_threads_remote_file_removal(self):
        """
        Create threads to remove remote files that don't exist locally.
        """

        logger = getLogger('MegaManager._create_threads_remote_file_removal')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to remove files remotely.')

        t_remover = Thread(target=self._all_accounts_remote_file_removal, args=( ), name='thread_remoteFileRemover')
        self.threads.append(t_remover)
        t_remover.start()


    def _create_threads_compress_image_files(self):
        """
        Create threads to compress image files.
        """

        logger = getLogger('MegaManager._create_threads_compress_image_files')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to compress local image files.')
        self._load_compressed_lists()

        t_compress = Thread(target=self._all_accounts_image_compression, args=( ), name='thread_compressImages')
        self.threads.append(t_compress)
        t_compress.start()

    def _create_threads_compress_video_files(self):
        """
        Create threads to compress video files.
        """

        logger = getLogger('MegaManager._create_threads_compress_video_files')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to compress local video files.')
        self._load_compressed_lists()

        t_compress = Thread(target=self._all_accounts_video_compression, args=( ), name='thread_compressVideos')
        self.threads.append(t_compress)
        t_compress.start()


    def _all_accounts_remote_file_removal(self):
        """
        Remove remote file.
        """

        logger = getLogger('MegaManager._all_accounts_remote_file_removal')
        logger.setLevel(self.logLevel)

        logger.debug(' Removing remote files.')

        foundUserPass = self._get_accounts_user_pass()

        for account in foundUserPass:
            self._find_remote_files_that_dont_exist_locally(account['user'], account['pass'])
            # t_remover = Thread(target=self._deleteRemoteFiles, args=(account['user'], account['pass'], ), name='thread_remoteRemover_%s' % account['user'])
            # self.threads.append(t_remover)
            # t_remover.start()
            sleep(self._get_sleep_time())


    def _all_accounts_image_compression(self):
        """
        Compress image.
        """

        logger = getLogger('MegaManager._all_accounts_image_compression')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Compressing local image files')
        foundUserPass = self._get_accounts_user_pass()

        for account in foundUserPass:
            self._find_image_files_to_compress(account['user'], account['pass'])
            # t_remover = Thread(target=self._deleteRemoteFiles, args=(account['user'], account['pass'], ), name='thread_remoteRemover_%s' % account['user'])
            # self.threads.append(t_remover)
            # t_remover.start()
            sleep(self._get_sleep_time())

    def _all_accounts_video_compression(self):
        """
        Compress video.
        """

        logger = getLogger('MegaManager._all_accounts_video_compression')
        logger.setLevel(self.logLevel)

        logger.debug(' Compressing local video files')
        foundUserPass = self._get_accounts_user_pass()

        for account in foundUserPass:
            self._find_video_files_to_compress(account['user'], account['pass'])
            sleep(self._get_sleep_time())

    def _delete_local_incomplete_files_from_account(self, username, password, remotePath=REMOTE_ROOT):
        """
        Delete incomplete files.
        
        :param username: username for MEGA account
        :type username: string
        
        :param password: password for MEGA account
        :type password: string
        
        """

        logger = getLogger('MegaManager._delete_local_incomplete_files_from_account')
        logger.setLevel(self.logLevel)

        chdir('%s' % self.megaToolsPath)

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
                        remoteFilePath = '/'+ '/'.join(line_split[1:])
                        if remotePath in remoteFilePath:
                            remote_root = remotePath.replace('/', '\\')
                            local_root = self.localRoot
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


    def _get_remote_file_size(self, username, password, localFilePath, remotePath=REMOTE_ROOT):
        """
        Get remote file sizes of equivalent local file path

        :param username: username for MEGA account
        :type username: string

        :param password: password for MEGA account
        :type password: string
        
        :param localFilePath: Local file path of remote file size to get
        :type localFilePath: string
        
        :return tuple: remote file size and remote file path
        """

        logger = getLogger('MegaManager._get_remote_file_size')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        localFilePath_adj = sub('\\\\', '/',localFilePath)
        postfix = split(LOCAL_ROOT_adj, localFilePath_adj)
        if len(postfix) > 1:
            subPath = postfix[1]

            chdir('%s' % self.megaToolsPath)

            cmd = 'start /B megals -ln -u %s -p %s "%s"' % (username, password, remotePath + subPath)
            proc = Popen(cmd, stdout=PIPE, shell=True)

            (out, err) = proc.communicate()
            line_split = out.split()
            if len(line_split) > 2:
                remoteFileSize = line_split[3]

                return remoteFileSize, remotePath + subPath

        return 0, ''


    def _get_remote_dir_size(self, user, password, localDirPath, remotePath=REMOTE_ROOT):
        """
        Get remote directory sizes of equivalent local file path

        :param user: username for MEGA account
        :type user: string

        :param password: password for MEGA account
        :type password: string

        :param localDirPath: Local directory path of remote file size to get
        :type localDirPath: string

        :return tuple: remote directory size and remote directory path
        """

        logger = getLogger('MegaManager._get_remote_dir_size')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        localFilePath_adj = sub('\\\\', '/',localDirPath)
        postfix = split(LOCAL_ROOT_adj, localFilePath_adj)
        if len(postfix) > 1:
            subPath = postfix[1]

            chdir('%s' % self.megaToolsPath)

            cmd = 'start /B megals -lnR -u %s -p %s "%s"' % (user, password, remotePath + subPath)
            proc = Popen(cmd, stdout=PIPE, shell=True)

            (out, err) = proc.communicate()
            lines = out.split('\r\n')
            totalRemoteDirSize = 0
            for line in lines:
                line_split = line.split()
                if len(line_split) > 2:
                    remoteFileSize = line_split[3]
                    if remoteFileSize.isdigit():
                        totalRemoteDirSize = totalRemoteDirSize + int(remoteFileSize)


            return totalRemoteDirSize, remotePath + subPath

        return 0, ''


    def _remove_incomplete_files(self, temp_logFile_path=TEMP_LOGFILE_PATH):
        """
        Remove incomplete files located in TEMP_LOGFILE_PATH

        :param temp_logFile_path: temporary file path located in temp directory that has incomplete file paths listed
        :type temp_logFile_path: string

        :return :
        """

        logger = getLogger('MegaManager._remove_incomplete_files')
        logger.setLevel(self.logLevel)
        
        temp_stderr_file = open(temp_logFile_path, "r")
        # with open(TEMP_LOGFILE_PATH, 'r') as temp_stderr_file:
        #     for line in temp_stderr_file:
        lines = temp_stderr_file.readlines()
        for line in lines:
            if 'already exists at ' in line:
                localFilePath = split('already exists at ', line)[1].replace('\n', '').replace('\r', '')
                if path.exists(localFilePath):
                    localFileSize = path.getsize(localFilePath)

                    split_line = split(' - ', split(':', line)[0])

                    if len(split_line) > 1:
                        user = split_line[0]
                        password = split_line[1]
                        remoteFileSize, remoteFilePath = self._get_remote_file_size(user, password, localFilePath)

                        if str(remoteFileSize).isdigit():
                        # if isinstance(remoteFileSize, (int, long)):
                            if localFileSize < int(remoteFileSize):
                                logger.debug(' File incomplete. Deleting file "%s"' % localFilePath)

                                try:
                                    if path.isfile(localFilePath):
                                        remove(localFilePath)
                                    elif path.isdir(localFilePath):
                                        rmtree(localFilePath)
                                except OSError as e:
                                    logger.debug(' Could not remove, access-error on file or directory "' + localFilePath + '"! \n' + str(e))


                                self._download_file(user, password, localFilePath, remoteFilePath)

                            else:
                                logger.debug(' Local file size is greater or equal to remote file size: "%s"' % localFilePath)
                        else:
                            logger.debug(' File does not exist remotely: "%s"' % localFilePath)
                else:
                    logger.debug(' File does not exist locally: "%s"' % localFilePath)

        temp_stderr_file.close()


    def _download_file(self, username, password, localPath, remotePath):
        """
        Download a remote file.

        :param username: username of account to download file from
        :type username: string
        :param password: password of account to download file from
        :type password: string
        :param localPath: Local path to download file to
        :type localPath: string
        :param remotePath: Remote path of file to download
        :type remotePath: string

        :return :
        """

        logger = getLogger('MegaManager._download_file')
        logger.setLevel(self.logLevel)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, remotePath, localPath))
        logFile = open(LOGFILE_MEGA, 'a')

        chdir('%s' % self.megaToolsPath)
        cmd = 'start /B megaget -u %s -p %s --path "%s" "%s"' % (username, password, localPath, remotePath)
        proc = Popen(cmd, stdout=logFile, stderr=logFile)

        while not proc.poll():
            pass

        logFile.close()


    def _download_account_files(self, username, password, localPath=LOCAL_ROOT, remotePath=REMOTE_ROOT):
        """
        Download all account files.

        :param username: username of account to download file from
        :type username: string
        :param password: password of account to download file from
        :type password: string
        :param localPath: Local path to download file to
        :type localPath: string
        :param remotePath: Remote path of file to download
        :type remotePath: string

        :return :
        """

        logger = getLogger('MegaManager._download_account_files')
        logger.setLevel(self.logLevel)


        logger.debug(' MEGA downloading directory from account "%s" from "%s" to "%s"' % (username, localPath, remotePath))
        logFile = open(LOGFILE_MEGA, 'a')

        # logFile_stdout = open(LOGFILE_STDOUT, 'a')
        temp_logFile_stderr = open(TEMP_LOGFILE_PATH, 'a')


        chdir('%s' % self.megaToolsPath)
        # cmd = ['megacopy', '--download', '-u', '%s' % username, '-p', '%s' % password, '--local', '"%s"' % localPath, '--remote', '"%s"' % remotePath]
        # proc = Popen(cmd, stdout=PIPE, shell=True)
        # (out, err) = proc.communicate()

        # cmd = 'megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (username, password, LOCAL_ROOT, remotePath)

        cmd = 'start "" /B megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (username, password, localPath, remotePath)
        proc = Popen(cmd, stdout=logFile, stderr=PIPE, shell=True)
        logger.debug('%s - %s: %s \n' % (username, password, cmd))

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

        self._remove_incomplete_files(TEMP_LOGFILE_PATH)

        output = proc.communicate()[0]
        exitCode = proc.returncode

        # logFile_stderr.close()
        # logFile_stdout.close()
        temp_logFile_stderr.close()
        logFile.close()


    def _wait_for_threads_to_finish(self, timeout=99999):
        """
        Wait for threads to finish.

        :param timeout: Maximum time in seconds to wait for threads.
        :type timeout: int

        :return :
        """

        logger = getLogger('MegaManager._wait_for_threads_to_finish')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Waiting for threads to finish.')

        startTime = time()
        megaFileFinished = False
        while len(self.threads) > 0:
            megaFileThreads_found = False

            if not time() - startTime > timeout:
                sleep(self._get_sleep_time())
                for thread in self.threads:
                    if not thread.isAlive():
                        self.threads.remove(thread)
                        logger.info(' Thread "%s" finished!' % thread.name)
                        logger.debug(' Threads left: %d' % len(self.threads))

                    if 'megaFile' in thread.name:
                        megaFileThreads_found = True

                if not megaFileThreads_found and not megaFileFinished:
                    logger.info(' "%s" file creation complete!' % self.megaAccountsData)
                    megaFileFinished = True
            else:
                logger.debug(' Waiting for threads to complete TIMED OUT!')
                return


    def _get_remote_dirs(self, username, password, remotePath=REMOTE_ROOT):
        """
        Get remote directories
        
        :param username: username of account to get remote directories from
        :type username: string
        :param password: password of account to get remote directories from
        :type password: string
        :param remotePath: remote path to search directories
        :type remotePath: string

        :return: returns list of directories 
        :type: list of strings
        """

        logger = getLogger('MegaManager._get_remote_dirs')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Get remote directories.')

        chdir('%s' % self.megaToolsPath)
        cmd = ['start', '/B', 'megals', '-u', '%s' % username, '-p', '%s' % password, '"%s"' % remotePath]
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()

        dirs = out.split('\r\n')
        dirList = []
        for dir in dirs:
            dirName = sub('%s' % remotePath, '', dir)
            if not dirName == '':
                dirList.append(sub('/', '', dirName))

        return dirList


        # cmd = 'megaals -u %s -p %s %s' % (username, password, remotePath)
        # proc1 = os.system(cmd)

    def _get_accounts_user_pass(self):
        """
        Get username and password from file with lines of "<username> - <password>"

        :param file: file with lines of "<username> - <password>"
        :type file: string

        :return: returns list of dictionaries holding user and pass
        :type: list of dictionaries
        """

        logger = getLogger('MegaManager._get_accounts_user_pass')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Getting usernames and passwords.')

        foundUserPass = []

        file = self.megaAccounts
        with open(file, "r") as ins:
            for line in ins:
                dict = {}
                if len(findall('-', line)) > 0 and len(findall('@', line)) > 0:
                    username = sub('\\n','',sub(' - .*','',line))
                    password = sub('\\n','',sub('.* - ','',line))


                    dict['user'] = username
                    dict['pass'] = password
                    foundUserPass.append(dict)

                # if not all and item:
                #     if item in line:
                #         dict['user'] = username
                #         dict['pass'] = password
                #         foundUserPass.append(dict)

        ins.close()
        return foundUserPass


    def _upload_to_account(self, username, password, localPath=LOCAL_ROOT, remotePath=REMOTE_ROOT):
        """
        Upload files to account.

        :param username: username of account to upload to
        :type username: string
        :param password: password of account to upload to
        :type password: string
        :param localPath: Local path to upload from
        :type localPath: string
        :param remotePath: Remote path of to upload to
        :type remotePath: string

        :return: returns list of dictionaries holding user and pass
        :type: list of dictionaries
        """

        logger = getLogger('MegaManager._upload_to_account')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Starting uploading for %s - %s' % (username, password))


        localPath_adj = sub('\\\\', '/', localPath)
        chdir('%s' % self.megaToolsPath)

        cmd = 'megals -ln -u %s -p %s "%s"' % (username, password, remotePath)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                if len(split(':\d{2} ', line)) > 1:
                    remote_filePath = split(':\d{2} ', line)[1]
                    # remote_filePath = ' '.join(line.split()[6:])
                    # remote_type = line.split()[2]
                    # if remote_type == '1':
                    dir_subPath = sub(remotePath, '', remote_filePath)
                    local_dir = localPath_adj + '/' + dir_subPath
                    remote_dir = remotePath + '/' + dir_subPath
                    if path.exists(local_dir):
                        self._upload_local_dir(username, password, local_dir, remote_dir)


    def _upload_local_dir(self, username, password, localDir, remoteDir):
        """
        Upload directory.

        :param username: username of account to upload to
        :type username: string
        :param password: password of account to upload to
        :type password: string
        :param localDir: Local directory to upload
        :type localDir: string
        :param remoteDir: Remote directory to upload to
        :type remoteDir: string

        :return:
        :type:
        """

        logger = getLogger('MegaManager._upload_local_dir')
        logger.setLevel(self.logLevel)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (username, password, localDir))
        logFile = open(LOGFILE_MEGA, 'a')

        chdir('%s' % self.megaToolsPath)

        cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (username, password, localDir, remoteDir)
        # proc = Popen(cmd, stdout=PIPE, shell=True)
        proc = Popen(cmd, stdout=logFile, stderr=logFile)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        logFile.close()


    def _find_remote_files_that_dont_exist_locally(self, username, password, remotePath=REMOTE_ROOT):
        """
        Remove remote files that don't exist locally.

        :param username: username of account to upload to
        :type username: string
        :param password: Password of account to upload to
        :type password: String
        :param remotePath: Remote path to iterate through.
        :type remotePath: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_remote_files_that_dont_exist_locally')
        logger.setLevel(self.logLevel)
        logger.debug(' Removing remote files that do not exist locally on %s - %s.' % (username, password))

        dirs_removed = []

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        chdir('%s' % self.megaToolsPath)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, remotePath)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                remote_filePath = split(':\d{2} ', line)[1]
                # remote_filePath = ' '.join(line.split()[6:])
                file_subPath = sub(remotePath, '', remote_filePath)
                local_filePath = LOCAL_ROOT_adj + file_subPath
                higherDirRemoved = False

                for removed_dir in dirs_removed:
                    if removed_dir in remote_filePath:
                        higherDirRemoved = True
                        break

                if not path.exists(local_filePath):
                    remote_type = line.split()[2]

                    if not higherDirRemoved:
                        if remote_type == '0':
                            self._remove_remote_file(username, password, remote_filePath)
                        elif remote_type == '1':
                            dirs_removed.append(remote_filePath)
                            self._remove_remote_file(username, password, remote_filePath)


    def _remove_remote_file(self, username, password, remoteFilePath):
        """
        Remove remote file.

        :param username: username of account to upload to
        :type username: string
        :param password: password of account to upload to
        :type password: string
        :param remoteFilePath: remote file path to remove
        :type remoteFilePath: string

        :return:
        :type:
        """

        logger = getLogger('MegaManager._remove_remote_file')
        logger.setLevel(self.logLevel)

        logger.debug(' %s - %s: Removing remote file "%s"!' % (username, password, remoteFilePath))
        logFile = open(LOGFILE_MEGA, 'a')

        chdir('%s' % self.megaToolsPath)

        cmd = 'megarm -u %s -p %s "%s"' % (username, password, remoteFilePath)
        proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')

        logFile.close()


    def _find_image_files_to_compress(self, username, password, remotePath=REMOTE_ROOT):
        """
        Find image files to compress.

        :param username: Username of account to find local images for.
        :type username: String.
        :param password: Password of account to find local images for.
        :type password: String.
        :param remotePath: Remote path to iterate through.
        :type remotePath: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_image_files_to_compress')
        logger.setLevel(self.logLevel)

        logger.debug(' Compressing image files.')
        extensions = ['.jpg', '.jpeg', '.png']

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        chdir('%s' % self.megaToolsPath)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, remotePath)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                # test = split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = path.splitext(split(':\d{2} ', line)[1])
                    if fileExt in extensions:
                        remote_filePath = split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = sub(remotePath, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = LOCAL_ROOT_adj + file_subPath

                            if (path.exists(local_filePath)) and (local_filePath not in self.compressedImageFiles) and (local_filePath not in self.unableToCompressImageFiles):
                                # timeout = 2
                                returnCode = self._compress_image_file(local_filePath)
                                if returnCode == 0:
                                    # startTime = time.time()
                                    compressPath_backup = local_filePath + '.compressimages-backup'
                                    # while time.time() - startTime < timeout:
                                    if path.exists(compressPath_backup):
                                        logger.debug(' File compressed successfully "%s"!' % local_filePath)
                                        remove(compressPath_backup)

                                        self.compressedFiles = None
                                        self.compressedFiles.append(local_filePath)
                                        self._dump_compressed_image_file_list()

                                    else:
                                        logger.debug(' File cannot be compressed any further "%s"!' % local_filePath)
                                        self.unableToCompressImageFiles.append(local_filePath)
                                        self._dump_unable_to_compress_image_file_list()

                                        # self._compress_image_file_delete_backup(local_filePath)
                                        # self._remove_remote_file(username, password, remote_filePath)

                                else:
                                    logger.debug(' Error, image file could not be compressed "%s"!' % local_filePath)

                            else:
                                logger.debug(' Error, image file previously processed. Moving on.  "%s"!' % local_filePath)

            sleep(self._get_sleep_time())


    def _compress_image_file(self, filePath):
        """
        Compress images file.

        :param filePath: File path of image to compress.
        :type filePath: string

        :return: subprocess object
        :type: call()
        """

        logger = getLogger('MegaManager._compress_image_file')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Compressing image file "%s".' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        chdir(WORKING_DIR)

        # proc1 = call('python libs\\compressImages\\compressImages.py --h', creationflags=CREATE_NO_WINDOW)
        cmd = 'D:\\Python\\Python27\\python.exe "%s\\libs\\compressImages\\compressImages.py" --mode compress "%s"' % (WORKING_DIR, filePath)
        proc1 = call(cmd, creationflags=CREATE_NO_WINDOW)
        return proc1


    def _find_video_files_to_compress(self, username, password, remotePath=REMOTE_ROOT):
        """
        Find video files to compress.

        :param username: username of account to find local video files for
        :type username: string
        :param password: password of account to find local video files for
        :type password: string
        :param remotePath: Remote path to mirror locally to iterate through.
        :type remotePath: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_video_files_to_compress')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Finding video files to compress.')
        extensions = ['.avi', '.mp4', '.wmv']

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        chdir('%s' % self.megaToolsPath)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, remotePath)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                # test = split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = path.splitext(split(':\d{2} ', line)[1])
                    if fileExt in extensions:
                        remote_filePath = split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = sub(remotePath, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = LOCAL_ROOT_adj + file_subPath

                            if path.exists(local_filePath):
                                if (local_filePath not in self.compressedVideoFiles) and (local_filePath not in self.unableToCompressVideoFiles):
                                    # timeout = 2
                                    returnCode, new_filePath = self._compress_video_file(local_filePath)
                                    if returnCode == 0:
                                        logger.debug(' Video file compressed successfully "%s" into "%s"!' % (local_filePath, new_filePath))
                                        self.compressedVideoFiles.append(new_filePath)
                                        self._dump_compressed_video_fle_list()

                                    else:
                                        logger.debug(' Error, video file could not be compressed "%s"!' % local_filePath)

                                else:
                                    logger.debug(' Error, video file previously processed. Moving on. "%s"!' % local_filePath)

                            else:
                                logger.debug(
                                    ' Error, local video file doesnt exist: "%s"!' % local_filePath)

            sleep(self._get_sleep_time())


    def _compress_video_file(self, filePath):
        """
        Compress images file.
        
        :param filePath: File path of video to compress.
        :type filePath: string

        :return: subprocess object
        :type: call()
        :return: File path of new video file.
        :type: string
        """

        logger = getLogger('MegaManager._compress_video_file')
        logger.setLevel(self.logLevel)
        logger.debug(' Compressing video file: "%s"' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        chdir(WORKING_DIR)
        newFilePath = filePath.rsplit( ".", 1 )[ 0 ] + '_NEW.mp4'
        if path.exists(newFilePath):
            remove(newFilePath)

        cmd = '"%s\\libs\\compressVideos\\ffmpeg.exe" -i "%s" -vf "scale=\'if(gte(iw,720), 720, iw)\':-2" -preset medium -threads 1 "%s"' % (WORKING_DIR, filePath, newFilePath)

        # proc1 = call(cmd)
        proc1 = call(cmd, creationflags=CREATE_NO_WINDOW)

        if path.exists(newFilePath) and proc1 == 0:
            remove(filePath)
        elif path.exists(newFilePath):
            remove(newFilePath)

        rename(newFilePath, sub('_NEW', '', newFilePath))

        return proc1, sub('_NEW', '', newFilePath)


    def _compress_image_file_delete_backup(self, filePath):
        """
        Compress image file and delete backup file that is created of old file

        :param filePath: File path of image file to compress.
        :type filePath: string

        :return: subprocess object
        :type: call()
        """

        logger = getLogger('MegaManager._compress_image_file_delete_backup')
        logger.setLevel(self.logLevel)

        logger.debug(' Deleting compressed backup files "%s".' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        proc1 = call('python libs\\compressImages\\compressImages.py --mode detletebackup "%s"' % (filePath),  creationflags=CREATE_NO_WINDOW)
        return proc1


    def _create_mega_accounts_data_file(self):
        """
        Create self.megaAccountsData file. File that has all fetched data of accounts and local and remote spaces of each account.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._create_mega_accounts_data_file')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating self.megaAccountsData.txt file.')

        foundUserPass = self._get_accounts_user_pass()

        # copyfile(self.megaAccountsData, self.megaAccountsData + '.old')

        try:
            self.accounts_details_dict = {}
            with open(self.megaAccountsData, "w") as outs:
                for account in foundUserPass:
                    logger.debug(' Creating thread to gather details on account %s.' % account)

                    t_megaFile = Thread(target=self._get_account_details, args=(account['user'], account['pass'], self.remoteRoot),
                                                  name='thread_megaFile_%s' % account['user'])
                    t_megaFile.start()
                    self.threads.append(t_megaFile)
                    sleep(self._get_sleep_time())


                # self._wait_for_threads_to_finish(threads, timeout=500, sleep=1)

                for accountDetails in sorted(self.accounts_details_dict):
                    for line in self.accounts_details_dict[accountDetails]:
                        outs.write(line)



            outs.close()

        except (Exception, KeyboardInterrupt)as e:
            logger.debug(' Exception: %s' % e)
            copyfile(self.megaAccountsData + '.old', self.megaAccountsData)


    def _get_sleep_time(self):
        """
        Get time in seconds to sleep. Function is used to pace program speed during iterations.

        :return: time in seconds to sleep
        :type: integer or decimal
        """

        logger = getLogger('MegaManager._get_sleep_time')
        logger.setLevel(self.logLevel)

        sleepTime = 0

        return sleepTime


    def _get_account_details(self, username, password, remotePath=REMOTE_ROOT):
        """
        Creats dictionary of account data (remote size, local size, etc...) for self.megaAccountsData file.

        :param username: Username of account to get data for 
        :type username: String
        :param password: Passworde of account to get data for 
        :type password: String
        :param remotePath: Remote path of account to get data for.
        :type remotePath: String

        :return:
        :type:
        """

        logger = getLogger('MegaManager._get_account_details')
        logger.setLevel(self.logLevel)

        accountDetails = []
        accountDetails.append(username + ' - ' + password + '\n')
        chdir('%s' % self.megaToolsPath)

        cmd = 'start /B megadf --free -h -u %s -p %s' % (username, password)
        proc = Popen(cmd, stdout=PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info(str(err))

        if not out == '':
            out = sub('\r', '', out)
            accountDetails.append('FREE SPACE: ' + out)

        cmd = 'start /B megadf --used -h -u %s -p %s' % (username, password)
        proc = Popen(cmd, stdout=PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info(str(err))

        if not out == '':
            out = sub('\r', '', out)
            accountDetails.append('REMOTE SIZE: ' + out)

        remotePath = remotePath + '/'
        cmd = 'start /B megals -n -u %s -p %s "%s"' % (username, password, remotePath)
        proc = Popen(cmd, stdout=PIPE, shell=True)
        (out, err) = proc.communicate()

        directoryLines = []
        totalLocalSize = 0
        if err:
            logger.info(str(err))

        if not out == '':
            lines = out.split('\r\n')
            for line in lines:
                localDirSize = 0
                localDirPath = self.localRoot + '\\' + line
                remoteDirSize, remotePath = self._get_remote_dir_size(username, password, localDirPath)

                if path.exists(localDirPath) and not line == '':
                    # localDirSize = path.getsize(localDirPath)
                    for r, d, f in walk(localDirPath):
                        for file in f:
                            filePath = path.join(r, file)
                            if path.exists(filePath):
                                localDirSize = localDirSize + path.getsize(filePath)

                    totalLocalSize = totalLocalSize + localDirSize
                    directoryLines.append(line + ' (%s remote, %s local)\n' % (self._get_mb_size_from_bytes(int(remoteDirSize)), self._get_mb_size_from_bytes(int(localDirSize))))

                elif not line == '':
                    directoryLines.append(line + ' (%s remote, NONE local)\n' % (self._get_mb_size_from_bytes(int(remoteDirSize))))
                    # accountDetails.append('LOCAL SIZE: NONE \n')


        accountDetails.append('LOCAL SIZE: %s \n' % self._get_mb_size_from_bytes(totalLocalSize))


        for line in directoryLines:
            accountDetails.append(line)
        accountDetails.append('\n')
        accountDetails.append('\n')

        self.accounts_details_dict[username] = accountDetails


    def _tear_down(self):
        """
        Tearing down of MEGA Manager.

        :return:
        :type:
        """
        
        logger = getLogger('MegaManager._tear_down')
        logger.setLevel(self.logLevel)
        
        logger.info(' Tearing down megaManager!')
        try:
            if self.compressedImageFiles:
                self._dump_compressed_image_file_list()

            if self.compressedVideoFiles:
                self._dump_compressed_video_fle_list()


            if self.unableToCompressImageFiles:
                self._dump_unable_to_compress_image_file_list()


            if self.unableToCompressVideoFiles:
                self._dump_unable_to_compress_video_file_list()
        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
            pass

    def _get_mb_size_from_bytes(self, bytes):
        """
        Convert bytes to size in MegaBytes.
        
        :param bytes: Size in bytes.
        :type bytes: Integer.

        :return: Size in MegaBytes from bytes.
        :type: String.
        """

        logger = getLogger('MegaManager._get_mb_size_from_bytes')
        logger.setLevel(self.logLevel)

        logger.debug(' Converting kilobytes to megabytes.')

        if bytes < 1000:
            return '%i' % bytes + 'B'
        elif 1000 <= bytes < 1000000:
            return '%.1f' % float(bytes / 1000) + 'KB'
        elif 1000000 <= bytes < 1000000000:
            return '%.1f' % float(bytes / 1000000) + 'MB'
        elif 1000000000 <= bytes < 1000000000000:
            return '%.1f' % float(bytes / 1000000000) + 'GB'
        elif 1000000000000 <= bytes:
            return '%.1f' % float(bytes / 1000000000000) + 'TB'


    def _size_of_dir(self, dirPath):
        """
        Walks through the directory, getting the cumulative size of the directory
            
        :param dirPath: Directory to walk through to get size.
        :type dirPath: String.
    
        :return sum: Size in bytes.
        """

        logger = getLogger('MegaManager._size_of_dir')
        logger.setLevel(self.logLevel)

        logger.debug(' Getting size of directory "%s"' % dirPath)

        sum = 0
        for file in listdir(dirPath):
            sum += path.getsize(dirPath+'\\'+file)
        return sum


def getArgs():
    """
    Get arguments from command line, and returns them as dictionary.

    :return: Dictionary of arguments.
    :type: Dictionary.
    """
    
    parser = ArgumentParser(description='Process some integers.')

    parser.add_argument('--download', dest='download', action='store_true', default=False,
                        help='If true, items will be downloaded from MEGA')

    parser.add_argument('--upload', dest='upload', action='store_true', default=False,
                        help='If true, items will be uploaded to MEGA')

    parser.add_argument('--removeRemote', dest='removeRemote', action='store_true', default=False,
                        help='If true, this will allow for remote files to be removed.')

    parser.add_argument('--compress', dest='compress', action='store_true', default=False,
                        help='If true, this will compress local image and video files.')

    parser.add_argument('--compressImages', dest='compressImages', action='store_true', default=False,
                        help='If true, this will compress local image files.')

    parser.add_argument('--compressVideos', dest='compressVideos', action='store_true', default=False,
                        help='If true, this will compress local video files.')

    parser.add_argument('--log', dest='logLevel', default='INFO',
                        help='Set logging level')


    args = parser.parse_args()
    return args.__dict__


def main():
    proc = Process(getpid())
    proc.nice(IDLE_PRIORITY_CLASS)  # Sets low priority

    kwargs = getArgs()

    megaObj = MegaManager(**kwargs)
    # returnCode = megaObj._compress_video_file('I:\\Games\\1\\Done\\MEGA\\Jada Fire\\Screw My Wife Please!! 42.wmv')

    megaObj.run()


if __name__ == "__main__":
    main()


