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
from libs import FFMPEG_Lib, MegaManager_Lib, MegaTools_Lib
from os import chdir, getpid, path, remove, rename, walk
from psutil import IDLE_PRIORITY_CLASS, Process
from random import randint
from re import findall, split, sub
from shutil import copyfile
from subprocess import call, PIPE, Popen
from sys import stdout
from tempfile import gettempdir
from threading import Thread
from time import sleep, time


__author__ = 'szmania'


MEGAMANAGER_CONFIG = 'megaManager.cfg'

MEGA_ACCOUNTS_DATA = "megaAccounts_DATA.txt"
MEGATOOLS_PATH = ''
MEGA_ACCOUNTS = ''
LOCAL_ROOT = ''
REMOTE_ROOT = ''

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
VIDEO_EXTENSIONS = ['.avi', '.mp4', '.wmv']

WORKING_DIR = path.dirname(path.realpath(__file__))

TEMP_LOGFILE_PATH = gettempdir() + '\\megaManager_error_files_%d.npz' % randint(0, 9999999999)

COMPRESSED_IMAGES_FILE = WORKING_DIR + "\\data\\compressed_images.npz"
UNABLE_TO_COMPRESS_IMAGES_FILE = WORKING_DIR + "\\data\\unable_to_compress_images.npz"
COMPRESSED_VIDEOS_FILE = WORKING_DIR + "\\data\\compressed_videos.npz"
UNABLE_TO_COMPRESS_VIDEOS_FILE = WORKING_DIR + "\\data\\unable_to_compress_videos.npz"
REMOVED_REMOTE_FILES = WORKING_DIR + '\\data\\removed_remote_files.npz'

LOGFILE_STDOUT = WORKING_DIR + '\\data\\mega_stdout.log'
LOGFILE_STDERR = WORKING_DIR + '\\data\\mega_stderr.log'
MEGAMANAGER_LOGFILEPATH = WORKING_DIR + '\\data\\megaManager_log.log'


class MegaManager(object):
    def __init__(self, **kwargs):
        self.threads = []
        self.download = None
        self.upload = None
        self.removeRemote = None
        self.removeIncomplete = None
        self.compress = None
        self.compressImages = None
        self.compressVideos = None
        self.downSpeed = None
        self.upSpeed = None
        self.logLevel = None
        # self.downSpeed = 0
        # self.upSpeed = 0
        self.megaManager_logFilePath = MEGAMANAGER_LOGFILEPATH



        if path.exists(self.megaManager_logFilePath):
            # if path.getsize(self.megaManager_logFilePath) > 10000000:
            try:
                remove(self.megaManager_logFilePath)
            except Exception as e:
                print(' Exception: %s' % str(e))
                pass

        self._assign_attributes(**kwargs)
        self._setup()


    def _setup(self):
        """
        Setup megaManager applicaiton.

        :return:
        """

        try:
            self._setup_logger(self.megaManager_logFilePath)
            self._load_config_file()

            self.ffmpeg = FFMPEG_Lib(ffmpegExePath=self.ffmpegExePath, logLevel=self.logLevel)
            self.lib = MegaManager_Lib(workingDir=WORKING_DIR, logLevel=self.logLevel)
            self.megaTools = MegaTools_Lib(megaToolsDir=self.megaToolsDir, downSpeedLimit=self.downSpeed, upSpeedLimit=self.upSpeed, logLevel=self.logLevel)

            self.foundUserPass = self._get_accounts_user_pass(file=self.megaAccountsPath)

            # totalAccounts = len(self.foundUserPass)

            # if self.downSpeed:
            #     self.downSpeed = int(self.downSpeed) / totalAccounts
            # if self.upSpeed:
            #     self.upSpeed = int(self.upSpeed) / totalAccounts


        except Exception as e:
            print(' Exception: ' + str(e))
            self._tear_down()

    def _assign_attributes(self, **kwargs):
        """
        Assign argumetns to class attributes.

        :param kwargs:  Dictionary of arguments.
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
        logger.info(' Logging to %s' % self.megaManager_logFilePath)

    def _load_config_file(self):
        """
        Load config file.
            
        :return:
        """

        logger = getLogger('MegaManager._load_config_file')
        logger.setLevel(self.logLevel)

        logger.debug(' Loading megaManager.cfg file.')

        with open(MEGAMANAGER_CONFIG, "r") as ins:
            for line in ins:
                if '=' in line:
                    value = split(' = ', line)[1].strip()
                    if line.startswith('MEGATOOLS_DIR'):
                        self.megaToolsDir = value
                    elif line.startswith('FFMPEG_EXE_PATH'):
                        self.ffmpegExePath = value
                    elif line.startswith('MEGA_ACCOUNTS') and not line.startswith('MEGA_ACCOUNTS_OUTPUT'):
                        self.megaAccountsPath = value
                    elif line.startswith('MEGA_ACCOUNTS_OUTPUT'):
                        self.megaAccountsOutputPath = value
                    elif line.startswith('LOCAL_ROOT'):
                        self.localRoot = value
                    elif line.startswith('REMOTE_ROOT'):
                        self.remoteRoot = value
        ins.close()

    def run(self):
        """
        Run MegaManager tasks.
        """

        logger = getLogger('MegaManager.run')
        logger.setLevel(self.logLevel)

        logger.debug(' Running megaManager.')

        try:

            self._create_thread_create_mega_accounts_data_file()

            if self.removeIncomplete:
                self._create_threads_local_unfinished_file_remover()

            if self.download:
                self._create_thread_download()
            if self.upload:
                self._create_thread_upload()
            if self.removeRemote:
                self._create_threads_removed_remote_file_deletion()

            if self.compress:
                self._create_thread_compress_image_files()
                self._create_thread_compress_video_files()
            elif self.compressImages:
                self._create_thread_compress_image_files()
            elif self.compressVideos:
                self._create_thread_compress_video_files()

            self._wait_for_threads_to_finish()

        except Exception as e:
            logger.debug(' Exception: ' + str(e))
            self._tear_down()

    def _create_thread_create_mega_accounts_data_file(self):
        """
        Create thread to create self.megaAccountsOutputPath file.
        """

        logger = getLogger('MegaManager._create_thread_create_mega_accounts_data_file')
        logger.setLevel(self.logLevel)

        logger.debug(' Creating thread to create "%s" file.' % self.megaAccountsOutputPath)

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

        for account in self.foundUserPass:
            t_unfinishedFileRemover = Thread(target=self.megaTools.remove_local_incomplete_files, args=(account['user'], account['pass'], self.localRoot, self.remoteRoot, ), name='thread_unfinishedFileRemover_%s' % account['user'])
            self.threads.append(t_unfinishedFileRemover)
            t_unfinishedFileRemover.start()

            sleep(self.lib.get_sleep_time())

    def _create_thread_download(self):
        """
        Create thread to download files.
        """

        logger = getLogger('MegaManager._create_thread_download')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to download files from MEGA accounts.')

        t = Thread(target=self._all_accounts_download, args=(), name='thread_download')
        self.threads.append(t)
        t.start()

    def _create_thread_upload(self):
        """
        Create thread to upload files.
        """

        logger = getLogger('MegaManager._create_thread_upload')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to upload files to MEGA accounts.')

        t = Thread(target=self._all_accounts_upload, args=(), name='thread_upload')
        self.threads.append(t)
        t.start()

    def _create_threads_removed_remote_file_deletion(self):
        """
        Create threads to remove remote files that don't exist locally.
        """

        logger = getLogger('MegaManager._create_threads_removed_remote_file_deletion')
        logger.setLevel(self.logLevel)

        # self._load_removed_remote_files_lists()
        self.removedRemoteFiles = self.lib.load_file_as_list(filePath=REMOVED_REMOTE_FILES)

        logger.debug(' Creating thread to remove files remotely.')

        # t_remover = Thread(target=self._removed_remote_file_deletion, args=( ), name='thread_remoteFileRemover')
        # self.threads.append(t_remover)
        # t_remover.start()

        for account in self.foundUserPass:
            t = Thread(target=self._find_remote_files_that_dont_exist_locally, args=(account['user'], account['pass'],), name='thread_remoteFileRemover_%s' % account['user'])

            # t = Thread(target=self._upload_to_account, args=(account['user'], account['pass'],), name='thread_upload_%s' % account['user'])
            self.threads.append(t)
            t.start()
            sleep(self.lib.get_sleep_time())


    def _create_thread_compress_image_files(self):
        """
        Create threads to compress image files.
        """

        logger = getLogger('MegaManager._create_thread_compress_image_files')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to compress local image files.')
        # self._load_compressed_image_lists()

        self.compressedImageFiles = self.lib.load_file_as_list(filePath=COMPRESSED_IMAGES_FILE)
        self.unableToCompressImageFiles = self.lib.load_file_as_list(filePath=UNABLE_TO_COMPRESS_IMAGES_FILE)

        t_compress = Thread(target=self._all_accounts_image_compression, args=( ), name='thread_compressImages')
        self.threads.append(t_compress)
        t_compress.start()

    def _create_thread_compress_video_files(self):
        """
        Create threads to compress video files.
        """

        logger = getLogger('MegaManager._create_thread_compress_video_files')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to compress local video files.')

        self.compressedVideoFiles = self.lib.load_file_as_list(filePath=COMPRESSED_VIDEOS_FILE)
        self.unableToCompressVideoFiles = self.lib.load_file_as_list(filePath=UNABLE_TO_COMPRESS_VIDEOS_FILE)

        t_compress = Thread(target=self._all_accounts_video_compression, args=( ), name='thread_compressVideos')
        self.threads.append(t_compress)
        t_compress.start()


    def _all_accounts_download(self):
        """
        Download from all MEGA accounts.
        """

        logger = getLogger('MegaManager._all_accounts_download')
        logger.setLevel(self.logLevel)
        
        for account in self.foundUserPass:
            self.megaTools.download_from_account(account['user'], account['pass'], self.localRoot, self.remoteRoot)

    def _all_accounts_upload(self):
        """
        Upload to all MEGA accounts.
        """

        logger = getLogger('MegaManager._all_accounts_upload')
        logger.setLevel(self.logLevel)
        
        for account in self.foundUserPass:
            self.megaTools.upload_to_account(account['user'], account['pass'], self.localRoot, self.remoteRoot)

    def _all_accounts_image_compression(self):
        """
        Compress image.
        """

        logger = getLogger('MegaManager._all_accounts_image_compression')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Compressing local image files')

        for account in self.foundUserPass:
            self._find_image_files_to_compress(account['user'], account['pass'])
            # t_remover = Thread(target=self._deleteRemoteFiles, args=(account['user'], account['pass'], ), name='thread_remoteRemover_%s' % account['user'])
            # self.threads.append(t_remover)
            # t_remover.start()
            sleep(self.lib.get_sleep_time())

    def _all_accounts_video_compression(self):
        """
        Compress video.
        """

        logger = getLogger('MegaManager._all_accounts_video_compression')
        logger.setLevel(self.logLevel)

        logger.debug(' Compressing local video files')

        for account in self.foundUserPass:
            self._find_video_files_to_compress(account['user'], account['pass'])
            sleep(self.lib.get_sleep_time())

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
                sleep(self.lib.get_sleep_time())
                for thread in self.threads:
                    if not thread.isAlive():
                        self.threads.remove(thread)
                        logger.info(' Thread "%s" finished!' % thread.name)
                        logger.debug(' Threads left: %d' % len(self.threads))
                    else:
                        if 'megaFile' in thread.name:
                            megaFileThreads_found = True

                if not megaFileThreads_found and not megaFileFinished:
                    self._dump_accounts_details_dict()
                    logger.info(' "%s" file creation complete!' % self.megaAccountsOutputPath)
                    megaFileFinished = True
            else:
                logger.debug(' Waiting for threads to complete TIMED OUT!')
                return




    def _get_accounts_user_pass(self, file):
        """
        Get username and password from file with lines of "<username> - <password>"

        :param file: file with lines of "<username> - <password>"
        :type file: string

        :return: Returns list of dictionaries holding user and pass.
        """

        logger = getLogger('MegaManager._get_accounts_user_pass')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Getting usernames and passwords.')

        foundUserPass = []

        with open(file, "r") as ins:
            for line in ins:
                dict = {}
                if len(findall('-', line)) > 0 and len(findall('@', line)) > 0:
                    username = sub('\\n','',sub(' - .*','',line))
                    password = sub('\\n','',sub('.* - ','',line))

                    dict['user'] = username
                    dict['pass'] = password
                    foundUserPass.append(dict)

        ins.close()
        return foundUserPass



    def _find_remote_files_that_dont_exist_locally(self, username, password):
        """
        Remove remote files that don't exist locally.

        :param username: username of account to upload to
        :type username: string
        :param password: Password of account to upload to
        :type password: String
        :param self.remoteRoot: Remote path to iterate through.
        :type self.remoteRoot: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_remote_files_that_dont_exist_locally')
        logger.setLevel(self.logLevel)

        logger.debug(' Removing remote files that do not exist locally on %s - %s.' % (username, password))

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        chdir('%s' % self.megaToolsDir)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, self.remoteRoot)
        cmd = 'megals -R -u %s -p %s "%s"' % (username, password, self.remoteRoot)

        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')


        for line in lines:
            if not line == '' and len(findall("\?", line)) == 0:

                # remote_filePath = split(':\d{2} ', line)[1]
                remote_filePath = line

                # remote_filePath = ' '.join(line.split()[6:])
                file_subPath = sub(self.remoteRoot, '', remote_filePath)
                local_filePath = LOCAL_ROOT_adj + file_subPath


                fileName, fileExt = path.splitext(remote_filePath)

                if not path.exists(local_filePath) and remote_filePath not in self.removedRemoteFiles and fileExt in IMAGE_EXTENSIONS:
                    higherDirRemoved = False

                    for removed_file in self.removedRemoteFiles:
                        if removed_file in remote_filePath:
                            higherDirRemoved = True
                            break

                    # remote_type = line.split()[2]

                    if not higherDirRemoved:
                        # if remote_type == '0':
                        self.removedRemoteFiles.append(remote_filePath)
                        self._remove_remote_file(username, password, remote_filePath)
                        # elif remote_type == '1':
                        #     self.removedRemoteFiles.append(remote_filePath)
                        #     self._remove_remote_file(username, password, remote_filePath)

                        self.lib.dump_list_into_file(itemList=self.removedRemoteFiles, filePath=REMOVED_REMOTE_FILES, )

    def get_mega_manager_log_file(self):
        """
        Returns Mega Manager logging file path.

        :return: Mega Manager logging file path.
        """
        
        return self.megaManager_logFilePath

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
        """

        logger = getLogger('MegaManager._remove_remote_file')
        logger.setLevel(self.logLevel)

        logger.debug(' %s - %s: Removing remote file "%s"!' % (username, password, remoteFilePath))
        logFile = open(self.megaManager_logFilePath, 'a')

        chdir('%s' % self.megaToolsDir)

        cmd = 'megarm -u %s -p %s "%s"' % (username, password, remoteFilePath)
        proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')

        logFile.close()


    def _find_image_files_to_compress(self, username, password):
        """
        Find image files to compress.

        :param username: Username of account to find local images for.
        :type username: String.
        :param password: Password of account to find local images for.
        :type password: String.
        :param self.remoteRoot: Remote path to iterate through.
        :type self.remoteRoot: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_image_files_to_compress')
        logger.setLevel(self.logLevel)

        logger.debug(' Compressing image files.')

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        chdir('%s' % self.megaToolsDir)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, self.remoteRoot)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                # test = split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = path.splitext(split(':\d{2} ', line)[1])
                    if fileExt in IMAGE_EXTENSIONS:
                        remote_filePath = split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = sub(self.remoteRoot, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = LOCAL_ROOT_adj + file_subPath

                            if (path.exists(local_filePath)):
                                if (local_filePath not in self.compressedImageFiles) and (local_filePath not in self.unableToCompressImageFiles):
                                    # timeout = 2
                                    result = self.lib.compress_image_file(local_filePath, )
                                    if result:
                                        # startTime = time.time()
                                        compressPath_backup = local_filePath + '.compressimages-backup'
                                        # while time.time() - startTime < timeout:
                                        if path.exists(compressPath_backup):
                                            logger.debug(' File compressed successfully "%s"!' % local_filePath)
                                            try:
                                                remove(compressPath_backup)
                                            except WindowsError as e:
                                                logger.warning(' Exception: %s' % str(e))
                                                pass

                                            self.compressedFiles = []
                                            self.compressedFiles.append(local_filePath)
                                            self.lib.dump_list_into_file(itemList=self.compressedImageFiles, filePath=COMPRESSED_IMAGES_FILE, )

                                        else:
                                            logger.debug(' File cannot be compressed any further "%s"!' % local_filePath)
                                            self.unableToCompressImageFiles.append(local_filePath)
                                            self.lib.dump_list_into_file(itemList=self.unableToCompressImageFiles, filePath=UNABLE_TO_COMPRESS_IMAGES_FILE, )

                                    else:
                                        logger.debug(' Error, image file could not be compressed "%s"!' % local_filePath)
                                        self.unableToCompressImageFiles.append(local_filePath)
                                        self.lib.dump_list_into_file(itemList=self.unableToCompressImageFiles,
                                                                     filePath=UNABLE_TO_COMPRESS_IMAGES_FILE, )

                                else:
                                    logger.debug(' Error, image file previously processed. Moving on.  "%s"!' % local_filePath)
                            else:
                                logger.debug(' Error, image file does NOT exist locally. Moving on.  "%s"!' % local_filePath)

            sleep(self.lib.get_sleep_time())

    def _find_video_files_to_compress(self, username, password):
        """
        Find video files to compress.

        :param username: username of account to find local video files for
        :type username: string
        :param password: password of account to find local video files for
        :type password: string
        :param self.remoteRoot: Remote path to mirror locally to iterate through.
        :type self.remoteRoot: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_video_files_to_compress')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Finding video files to compress.')

        LOCAL_ROOT_adj = sub('\\\\', '/', self.localRoot)
        chdir('%s' % self.megaToolsDir)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, self.remoteRoot)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')

        for line in lines:
            if not line == '':
                # test = split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = path.splitext(split(':\d{2} ', line)[1])
                    if fileExt in VIDEO_EXTENSIONS:
                        remote_filePath = split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = sub(self.remoteRoot, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = LOCAL_ROOT_adj + file_subPath

                            if path.isfile(local_filePath):
                                if (local_filePath not in self.compressedVideoFiles) and (local_filePath not in self.unableToCompressVideoFiles):

                                    newFilePath = local_filePath.rsplit(".", 1)[0] + '_NEW.mp4'

                                    if path.isfile(newFilePath):
                                        for retry in range(100):
                                            try:
                                                remove(newFilePath)
                                                break
                                            except:
                                                logger.debug(" Remove failed, retrying...")
                                    returnCode = self.ffmpeg.compress_video_file(local_filePath, targetPath=newFilePath,)

                                    if returnCode == 0 and path.exists(newFilePath):
                                        for retry in range(100):
                                            try:
                                                remove(local_filePath)
                                                break
                                            except:
                                                logger.debug(" Remove failed, retrying...")

                                        for retry in range(100):
                                            try:
                                                rename(newFilePath, sub('_NEW', '', newFilePath))
                                                break
                                            except:
                                                logger.debug(" Rename failed, retrying...")

                                        logger.debug(' Video file compressed successfully "%s" into "%s"!' % (local_filePath, newFilePath))
                                        self.compressedVideoFiles.append(newFilePath)
                                        self.lib.dump_list_into_file(itemList=self.compressedVideoFiles,
                                                                     filePath=COMPRESSED_VIDEOS_FILE, )

                                    elif path.exists(newFilePath):
                                        remove(newFilePath)

                                    else:
                                        logger.debug(' Error, video file could not be compressed "%s"!' % local_filePath)

                                else:
                                    logger.debug(' Error, video file previously processed. Moving on. "%s"!' % local_filePath)

                            else:
                                logger.debug(
                                    ' Error, local video file doesnt exist: "%s"!' % local_filePath)

            sleep(self.lib.get_sleep_time())



    def _compress_image_file_delete_backup(self, filePath):
        """
        Compress image file and delete backup file that is created of old file

        :param filePath: File path of image file to compress.
        :type filePath: string

        :return: subprocess object
        """

        logger = getLogger('MegaManager._compress_image_file_delete_backup')
        logger.setLevel(self.logLevel)

        logger.debug(' Deleting compressed backup files "%s".' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        proc1 = call('python tools\\compressImages\\compressImages.py --mode detletebackup "%s"' % (filePath),  creationflags=CREATE_NO_WINDOW)
        return proc1


    def _create_mega_accounts_data_file(self):
        """
        Create self.megaAccountsOutputPath file. File that has all fetched data of accounts and local and remote spaces of each account.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._create_mega_accounts_data_file')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating self.megaAccountsOutputPath.txt file.')


        # copyfile(self.megaAccountsOutputPath, self.megaAccountsOutputPath + '.old')

        try:
            self.accounts_details_dict = {}
            with open(self.megaAccountsOutputPath, "w") as outs:
                for account in self.foundUserPass:
                    logger.debug(' Creating thread to gather details on account %s.' % account)

                    t_megaFile = Thread(target=self._get_account_details, args=(account['user'], account['pass']),
                                                  name='thread_megaFile_%s' % account['user'])
                    t_megaFile.start()
                    self.threads.append(t_megaFile)
                    sleep(self.lib.get_sleep_time())


                # self._wait_for_threads_to_finish(threads, timeout=500, sleep=1)

            outs.close()

        except (Exception, KeyboardInterrupt)as e:
            logger.debug(' Exception: %s' % e)
            if path.exists(self.megaAccountsOutputPath + '.old'):
                copyfile(self.megaAccountsOutputPath + '.old', self.megaAccountsOutputPath)

    def _dump_accounts_details_dict(self):
        """
        Dump self.accounts_details_dict to file.
        
        :return: 
        """

        logger = getLogger('MegaManager._dump_accounts_details_dict')
        logger.setLevel(self.logLevel)

        with open(self.megaAccountsOutputPath, "w") as outs:
            for accountDetails in sorted(self.accounts_details_dict):
                for line in self.accounts_details_dict[accountDetails]:
                    outs.write(line)
        outs.close()




    def _get_account_details(self, username, password):
        """
        Creats dictionary of account data (remote size, local size, etc...) for self.megaAccountsOutputPath file.

        :param username: Username of account to get data for 
        :type username: String
        :param password: Passworde of account to get data for 
        :type password: String
        :param self.remoteRoot: Remote path of account to get data for.
        :type self.remoteRoot: String

        :return:
        :type:
        """

        logger = getLogger('MegaManager._get_account_details')
        logger.setLevel(self.logLevel)

        accountDetails = []
        accountDetails.append(username + ' - ' + password + '\n')
        chdir('%s' % self.megaToolsDir)

        freeSpace = self.megaTools.get_account_free_space(username=username, password=password)
        accountDetails.append('FREE SIZE: ' + freeSpace)

        usedSpace = self.megaTools.get_account_used_space(username=username, password=password)
        accountDetails.append('REMOTE SIZE: ' + usedSpace)

        subDirs = self.megaTools.get_remote_subdir_names_only(username=username, password=password, remotePath=self.remoteRoot)

        directoryLines = []
        totalLocalSize = 0


        for line in subDirs:
            localDirSize = 0
            localDirPath = self.localRoot + '\\' + line
            remoteDirSize, remoteDirPath = self.megaTools.get_remote_dir_size(username, password, localDirPath, localRoot=self.localRoot, remoteRoot=self.remoteRoot)

            if path.exists(localDirPath) and not line == '':
                # localDirSize = path.getsize(localDirPath)
                for r, d, f in walk(localDirPath):
                    for file in f:
                        filePath = path.join(r, file)
                        if path.exists(filePath):
                            localDirSize = localDirSize + path.getsize(filePath)

                totalLocalSize = totalLocalSize + localDirSize
                directoryLines.append(line + ' (%s remote, %s local)\n' % (self.lib.get_mb_size_from_bytes(int(remoteDirSize)), self.lib.get_mb_size_from_bytes(int(localDirSize))))

            elif not line == '':
                directoryLines.append(line + ' (%s remote, NONE local)\n' % (self.lib.get_mb_size_from_bytes(int(remoteDirSize))))
                # accountDetails.append('LOCAL SIZE: NONE \n')


        accountDetails.append('LOCAL SIZE: %s \n' % self.lib.get_mb_size_from_bytes(totalLocalSize))


        for line in directoryLines:
            accountDetails.append(line)
        accountDetails.append('\n')
        accountDetails.append('\n')

        self.accounts_details_dict[username] = accountDetails


    def _tear_down(self):
        """
        Tearing down of MEGA Manager.

        :return:
        """
        
        logger = getLogger('MegaManager._tear_down')
        logger.setLevel(self.logLevel)
        
        logger.info(' Tearing down megaManager!')
        try:
            if self.removeRemote:
                self.lib.dump_list_into_file(itemList=self.removedRemoteFiles, filePath=REMOVED_REMOTE_FILES, )
            if self.compressImages:
                self.lib.dump_list_into_file(itemList=self.compressedImageFiles, filePath=COMPRESSED_IMAGES_FILE, )
                self.lib.dump_list_into_file(itemList=self.unableToCompressImageFiles, filePath=UNABLE_TO_COMPRESS_IMAGES_FILE)
            if self.compressVideos:
                self.lib.dump_list_into_file(itemList=self.compressedVideoFiles, filePath=COMPRESSED_VIDEOS_FILE, )
                self.lib.dump_list_into_file(itemList=self.unableToCompressVideoFiles, filePath=UNABLE_TO_COMPRESS_VIDEOS_FILE)

            self.lib.kill_running_processes_with_name('megacopy.exe')
            self.lib.kill_running_processes_with_name('megals.exe')
            self.lib.kill_running_processes_with_name('megadf.exe')
            self.lib.kill_running_processes_with_name('ffmpeg.exe')

        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
            pass


def get_args():
    """
    Get arguments from command line, and returns them as dictionary.

    :return: Dictionary of arguments.
    :type: Dictionary.
    """

    parser = ArgumentParser(description='MEGA Manager is a MEGA cloud storage management and optimization application.')

    parser.add_argument('--download', dest='download', action='store_true', default=False,
                        help='If true, items will be downloaded from MEGA')

    parser.add_argument('--upload', dest='upload', action='store_true', default=False,
                        help='If true, items will be uploaded to MEGA')

    parser.add_argument('--removeRemote', dest='removeRemote', action='store_true', default=False,
                        help='If true, this will allow for remote files to be removed.')

    parser.add_argument('--removeIncomplete', dest='removeIncomplete', action='store_true', default=False,
                        help='If true, this will allow for local downloaded files that are incomplete to be removed.')

    parser.add_argument('--compress', dest='compress', action='store_true', default=False,
                        help='If true, this will compress local image and video files.')

    parser.add_argument('--compressImages', dest='compressImages', action='store_true', default=False,
                        help='If true, this will compress local image files.')

    parser.add_argument('--compressVideos', dest='compressVideos', action='store_true', default=False,
                        help='If true, this will compress local video files.')

    parser.add_argument('--downSpeed', dest='downSpeed', type=int, default=None,
                        help='Total download speed limit.')

    parser.add_argument('--upSpeed', dest='upSpeed', type=int, default=None,
                        help='Total upload speed limit.')

    parser.add_argument('--log', dest='logLevel', default='INFO',
                        help='Set logging level')

    args = parser.parse_args()
    return args.__dict__




def main():
    proc = Process(getpid())
    proc.nice(IDLE_PRIORITY_CLASS)  # Sets low priority

    kwargs = get_args()

    megaObj = MegaManager(**kwargs)

    megaObj.run()


if __name__ == "__main__":
    main()


