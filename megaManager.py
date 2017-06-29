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

COMPRESSION_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
COMPRESSION_VIDEO_EXTENSIONS = ['.avi', '.mp4', '.wmv']

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
        self.__threads = []
        self.__download = None
        self.__upload = None
        self.__removeRemote = None
        self.__removeIncomplete = None
        self.__compressAll = None
        self.__compressImages = None
        self.__compressVideos = None
        self.__downSpeed = None
        self.__upSpeed = None
        self.__logLevel = None

        self.__compressedImagesFilePath = COMPRESSED_IMAGES_FILE
        self.__compressedVideosFilePath = COMPRESSED_VIDEOS_FILE
        self.__compressionImageExts = COMPRESSION_IMAGE_EXTENSIONS
        self.__compressionVideoExts = COMPRESSION_VIDEO_EXTENSIONS
        self.__megaManager_logFilePath = MEGAMANAGER_LOGFILEPATH
        self.__removedRemoteFilePath = REMOVED_REMOTE_FILES
        self.__unableToCompressImagesFilePath = UNABLE_TO_COMPRESS_IMAGES_FILE
        self.__unableToCompressVideosFilePath = UNABLE_TO_COMPRESS_VIDEOS_FILE


        if path.exists(self.__megaManager_logFilePath):
            try:
                remove(self.__megaManager_logFilePath)
            except Exception as e:
                print(' Exception: %s' % str(e))
                pass

        self._assign_attributes(**kwargs)
        self._setup()

    def _setup(self):
        """
        Setup MegaManager applicaiton.
        """

        try:
            self._setup_logger(self.__megaManager_logFilePath)
            self._load_config_file()

            self.__ffmpeg = FFMPEG_Lib(ffmpegExePath=self.__ffmpegExePath, logLevel=self.__logLevel)
            self.__lib = MegaManager_Lib(workingDir=WORKING_DIR, logLevel=self.__logLevel)
            self.__megaTools = MegaTools_Lib(megaToolsDir=self.__megaToolsDir, downSpeedLimit=self.__downSpeed,
                                             upSpeedLimit=self.__upSpeed, logLevel=self.__logLevel)

            self.__foundUserPass = self._get_accounts_user_pass(file=self.__megaAccountsPath)

        except Exception as e:
            print(' Exception: ' + str(e))
            self._tear_down()

    def _assign_attributes(self, **kwargs):
        """
        Assign argumetns to class attributes.

        Args:
            kwargs (dict):  Dictionary of arguments.
        """

        for key, value in kwargs.items():
            setattr(self, '__%s' % key, value)

    def _setup_logger(self, logFile):
        """
        Logger setup.

        Args:
            logFile (str):  Log file path.
        """

        root = getLogger()
        root.setLevel(DEBUG)

        self.__handler = FileHandler(logFile)
        formatter = Formatter('%(levelname)s:%(name)s:%(message)s')

        # formatter = logging.Formatter(fmt='%(message)s', datefmt='')
        self.__handler.setLevel(DEBUG)
        self.__handler.setFormatter(formatter)

        ch = StreamHandler(stdout)
        ch.setLevel(self.__logLevel)
        ch.setFormatter(formatter)

        root.addHandler(self.__handler)
        root.addHandler(ch)

        logger = getLogger('MegaManager._setup_logger')
        logger.setLevel(self.__logLevel)
        logger.info(' Logging to %s' % self.__megaManager_logFilePath)

    def _load_config_file(self):
        """
        Load config file.
        """

        logger = getLogger('MegaManager._load_config_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' Loading megaManager.cfg file.')

        with open(MEGAMANAGER_CONFIG, "r") as ins:
            for line in ins:
                if '=' in line:
                    value = split(' = ', line)[1].strip()
                    if line.startswith('MEGATOOLS_DIR'):
                        self.__megaToolsDir = value
                    elif line.startswith('FFMPEG_EXE_PATH'):
                        self.__ffmpegExePath = value
                    elif line.startswith('MEGA_ACCOUNTS') and not line.startswith('MEGA_ACCOUNTS_OUTPUT'):
                        self.__megaAccountsPath = value
                    elif line.startswith('MEGA_ACCOUNTS_OUTPUT'):
                        self.__megaAccountsOutputPath = value
                    elif line.startswith('LOCAL_ROOT'):
                        self.__localRoot = value
                    elif line.startswith('REMOTE_ROOT'):
                        self.__remoteRoot = value
        ins.close()

    def _all_accounts_download(self):
        """
        Download from all MEGA accounts.
        """

        logger = getLogger('MegaManager._all_accounts_download')
        logger.setLevel(self.__logLevel)
        
        for account in self.__foundUserPass:
            self.__megaTools.download_all_files_from_account(account['user'], account['pass'], self.__localRoot, self.__remoteRoot)

    def _all_accounts_upload(self):
        """
        Upload to all MEGA accounts.
        """

        logger = getLogger('MegaManager._all_accounts_upload')
        logger.setLevel(self.__logLevel)
        
        for account in self.__foundUserPass:
            self.__megaTools.upload_to_account(account['user'], account['pass'], self.__localRoot, self.__remoteRoot)

    def _all_accounts_image_compression(self):
        """
        Compress image.
        """

        logger = getLogger('MegaManager._all_accounts_image_compression')
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Compressing local image files')

        for account in self.__foundUserPass:
            self._find_image_files_to_compress(account['user'], account['pass'])

    def _all_accounts_video_compression(self):
        """
        Compress video.
        """

        logger = getLogger('MegaManager._all_accounts_video_compression')
        logger.setLevel(self.__logLevel)

        logger.debug(' Compressing local video files')

        for account in self.__foundUserPass:
            self._find_video_files_to_compress(account['user'], account['pass'])

    def _wait_for_threads_to_finish(self, timeout=99999):
        """
        Wait for __threads to finish.

        :param timeout: Maximum time in seconds to wait for __threads.
        :type timeout: int

        :return :
        """

        logger = getLogger('MegaManager._wait_for_threads_to_finish')
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Waiting for __threads to finish.')

        startTime = time()
        megaFileFinished = False

        while len(self.__threads) > 0:
            megaFileThreads_found = False

            if not time() - startTime > timeout:
                sleep(self.__lib.get_sleep_time())
                for thread in self.__threads:
                    if not thread.isAlive():
                        self.__threads.remove(thread)
                        logger.info(' Thread "%s" finished!' % thread.name)
                        logger.debug(' Threads left: %d' % len(self.__threads))
                    else:
                        if 'megaFile' in thread.name:
                            megaFileThreads_found = True

                if not megaFileThreads_found and not megaFileFinished:
                    self._dump_accounts_details_dict()
                    logger.info(' "%s" file creation complete!' % self.__megaAccountsOutputPath)
                    megaFileFinished = True
            else:
                logger.debug(' Waiting for threads to complete TIMED OUT! Timeout %d (seconds)' % timeout)
                return

    def _get_accounts_user_pass(self, file):
        """
        Get username and password from file with lines of "<username> - <password>"

        Args:
            file (str): file in format with lines:

                "<username> - <password>"
                "<username2> - <password2>"

            Where <username> is account username and <password> is account password.

        Returns:
            Returns list of dictionaries holding user and pass.
        """

        logger = getLogger('MegaManager._get_accounts_user_pass')
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Getting usernames and passwords.')

        foundUserPass = []

        try:
            with open(file, "r") as ins:
                for line in ins:
                    dict = {}
                    if len(findall('-', line)) > 0 and len(findall('@', line)) > 0:
                        username = sub('\\n','',sub(' - .*','',line))
                        password = sub('\\n','',sub('.* - ','',line))

                        dict['user'] = username
                        dict['pass'] = password
                        foundUserPass.append(dict)
        except Exception as e:
            logger.warning(' Exception: %s' % str(e))
        finally:
            ins.close()
        return foundUserPass

    def _create_thread_create_mega_accounts_data_file(self):
        """
        Create thread to create self.__megaAccountsOutputPath file.
        """

        logger = getLogger('MegaManager._create_thread_create_mega_accounts_data_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to create "%s" file.' % self.__megaAccountsOutputPath)

        t = Thread(target=self._create_mega_accounts_data_file, name='thread_createself.megaAccountsData_file')
        self.__threads.append(t)
        t.start()

    def _create_threads_local_unfinished_file_remover(self):
        """
        Create threads to remove unfinished local downloaded files.
        """

        logger = getLogger('MegaManager._create_threads_local_unfinished_file_remover')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating threads to remove unfinished files.')

        for account in self.__foundUserPass:
            t_unfinishedFileRemover = Thread(target=self.__megaTools.remove_local_incomplete_files, args=(
            account['user'], account['pass'], self.__localRoot, self.__remoteRoot,),
                                             name='thread_unfinishedFileRemover_%s' % account['user'])
            self.__threads.append(t_unfinishedFileRemover)
            t_unfinishedFileRemover.start()

            # sleep(self.__lib.get_sleep_time())

    def _create_thread_download(self):
        """
        Create thread to download files.
        """

        logger = getLogger('MegaManager._create_thread_download')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to download files from MEGA accounts.')

        t = Thread(target=self._all_accounts_download, args=(), name='thread_download')
        self.__threads.append(t)
        t.start()

    def _create_thread_upload(self):
        """
        Create thread to upload files.
        """

        logger = getLogger('MegaManager._create_thread_upload')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to upload files to MEGA accounts.')

        t = Thread(target=self._all_accounts_upload, args=(), name='thread_upload')
        self.__threads.append(t)
        t.start()

    def _create_threads_removed_remote_file_deletion(self):
        """
        Create threads to remove remote files that don't exist locally.
        """

        logger = getLogger('MegaManager._create_threads_removed_remote_file_deletion')
        logger.setLevel(self.__logLevel)

        self.__removedRemoteFiles = self.__lib.load_file_as_list(filePath=self.__removedRemoteFilePath)

        logger.debug(' Creating thread to remove files remotely.')

        for account in self.__foundUserPass:
            t = Thread(target=self._get_remote_files_that_dont_exist_locally,
                       args=(account['user'], account['pass'],),
                       name='thread_remoteFileRemover_%s' % account['user'])
            self.__threads.append(t)
            t.start()

    def _create_thread_compress_image_files(self):
        """
        Create threads to compress image files.
        """

        logger = getLogger('MegaManager._create_thread_compress_image_files')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to compress local image files.')

        self.__compressedImageFiles = self.__lib.load_file_as_list(filePath=self.__compressedImagesFilePath)
        self.__unableToCompressImageFiles = self.__lib.load_file_as_list(filePath=self.__unableToCompressImagesFilePath)

        t_compress = Thread(target=self._all_accounts_image_compression, args=( ), name='thread_compressImages')
        self.__threads.append(t_compress)
        t_compress.start()

    def _create_thread_compress_video_files(self):
        """
        Create threads to compress video files.
        """

        logger = getLogger('MegaManager._create_thread_compress_video_files')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to compress local video files.')

        self.__compressedVideoFiles = self.__lib.load_file_as_list(filePath=self.__compressedVideosFilePath)
        self.__unableToCompressVideoFiles = self.__lib.load_file_as_list(filePath=self.__unableToCompressVideosFilePath)

        t_compress = Thread(target=self._all_accounts_video_compression, args=( ), name='thread_compressVideos')
        self.__threads.append(t_compress)
        t_compress.start()

    def _get_remote_files_that_dont_exist_locally(self, username, password):
        """
        Get remote files that don't exist locally.

        Args:
            username (str): username of account to upload to
            password (str): Password of account to upload to

        Returns:
            list of remote files that don't exist locally
        """

        logger = getLogger('MegaManager._get_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__logLevel)

        logger.debug(' Getting remote files that do not exist locally on %s - %s.' % (username, password))

        localRoot_adj = sub('\\\\', '/', self.__localRoot)
        chdir('%s' % self.__megaToolsDir)

        remoteFiles = self.__megaTools.get_remote_files(username=username, password=password,
                                                        remotePath=self.__remoteRoot)

        dontExistLocally = []
        for remote_filePath in remoteFiles:
            file_subPath = sub(self.__remoteRoot, '', remote_filePath)
            local_filePath = localRoot_adj + file_subPath

            if not path.exists(local_filePath):
                dontExistLocally.append(local_filePath)

        return dontExistLocally

    def _delete_remote_files_that_dont_exist_locally(self, username, password):
        """
        Remove remote files that don't exist locally.

        Args:
            username (str): username of account to __upload to
            password (str): Password of account to __upload to
        """

        logger = getLogger('MegaManager._delete_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__logLevel)

        logger.debug(' Deleting remote files that do not exist locally on %s - %s.' % (username, password))

        dontExistLocally = self._get_remote_files_that_dont_exist_locally(username=username, password=password)

        for filePath in dontExistLocally:

            # fileName, fileExt = path.splitext(filePath)

            if not filePath in self.__removedRemoteFiles:
                higherDirRemoved = False

                for removed_file in self.__removedRemoteFiles:
                    if removed_file in filePath:
                        higherDirRemoved = True
                        break

                if not higherDirRemoved:
                    self.__removedRemoteFiles.append(filePath)
                    self.__megaTools.remove_remote_file(username=username, password=password,
                                                        remoteFilePath=filePath)
                    self.__lib.dump_list_into_file(itemList=self.__removedRemoteFiles,
                                                   filePath=self.__removedRemoteFilePath)

    def get_mega_manager_log_file(self):
        """
        Returns Mega Manager logging file path.

        Returns:
             Mega Manager logging file path.
        """
        
        return self.__megaManager_logFilePath

    def run(self):
        """
        Run MegaManager tasks.
        """

        logger = getLogger('MegaManager.run')
        logger.setLevel(self.__logLevel)

        logger.debug(' Running megaManager.')

        try:

            self._create_thread_create_mega_accounts_data_file()

            if self.__removeIncomplete:
                self._create_threads_local_unfinished_file_remover()

            if self.__download:
                self._create_thread_download()
            if self.__upload:
                self._create_thread_upload()
            if self.__removeRemote:
                self._create_threads_removed_remote_file_deletion()

            if self.__compressAll:
                self._create_thread_compress_image_files()
                self._create_thread_compress_video_files()
            elif self.__compressImages:
                self._create_thread_compress_image_files()
            elif self.__compressVideos:
                self._create_thread_compress_video_files()

            self._wait_for_threads_to_finish()

        except Exception as e:
            logger.debug(' Exception: ' + str(e))
            self._tear_down()

    def _find_image_files_to_compress(self, username, password):
        """
        Find image files to __compressAll.

        :param username: Username of account to find local images for.
        :type username: String.
        :param password: Password of account to find local images for.
        :type password: String.
        :param self.__remoteRoot: Remote path to iterate through.
        :type self.__remoteRoot: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_image_files_to_compress')
        logger.setLevel(self.__logLevel)

        logger.debug(' Compressing image files.')

        localRoot_adj = sub('\\\\', '/', self.__localRoot)
        chdir('%s' % self.__megaToolsDir)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, self.__remoteRoot)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                # test = split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = path.splitext(split(':\d{2} ', line)[1])
                    if fileExt in self.__compressionImageExtensions:
                        remote_filePath = split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = sub(self.__remoteRoot, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = localRoot_adj + file_subPath

                            if (path.exists(local_filePath)):
                                if (local_filePath not in self.__compressedImageFiles) and (local_filePath not in self.__unableToCompressImageFiles):
                                    # timeout = 2
                                    result = self.__lib.compress_image_file(local_filePath, )
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
                                            self.__lib.dump_list_into_file(itemList=self.__compressedImageFiles, filePath=self.__compressedImagesFilePath, )

                                        else:
                                            logger.debug(' File cannot be compressed any further "%s"!' % local_filePath)
                                            self.__unableToCompressImageFiles.append(local_filePath)
                                            self.__lib.dump_list_into_file(itemList=self.__unableToCompressImageFiles, filePath=self.__unableToCompressImagesFilePath, )

                                    else:
                                        logger.debug(' Error, image file could not be compressed "%s"!' % local_filePath)
                                        self.__unableToCompressImageFiles.append(local_filePath)
                                        self.__lib.dump_list_into_file(itemList=self.__unableToCompressImageFiles,
                                                                       filePath=self.__unableToCompressImagesFilePath)


                                else:
                                    logger.debug(' Error, image file previously processed. Moving on.  "%s"!' % local_filePath)
                            else:
                                logger.debug(' Error, image file does NOT exist locally. Moving on.  "%s"!' % local_filePath)

            sleep(self.__lib.get_sleep_time())

    def _find_video_files_to_compress(self, username, password):
        """
        Find video files to __compressAll.

        :param username: username of account to find local video files for
        :type username: string
        :param password: password of account to find local video files for
        :type password: string
        :param self.__remoteRoot: Remote path to mirror locally to iterate through.
        :type self.__remoteRoot: String.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._find_video_files_to_compress')
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Finding video files to __compressAll.')

        localRoot_adj = sub('\\\\', '/', self.__localRoot)
        chdir('%s' % self.__megaToolsDir)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (username, password, self.__remoteRoot)
        proc = Popen(cmd, stdout=PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')

        for line in lines:
            if not line == '':
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = path.splitext(split(':\d{2} ', line)[1])
                    if fileExt in VIDEO_EXTENSIONS:
                        remote_filePath = split(':\d{2} ', line)[1]
                        file_subPath = sub(self.__remoteRoot, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = localRoot_adj + file_subPath

                            if path.isfile(local_filePath):
                                if (local_filePath not in self.__compressedVideoFiles) \
                                        and (local_filePath not in self.__unableToCompressVideoFiles):

                                    newFilePath = local_filePath.rsplit(".", 1)[0] + '_NEW.mp4'

                                    if path.exists(newFilePath):
                                        for retry in range(100):
                                            try:
                                                remove(newFilePath)
                                                break
                                            except:
                                                logger.debug(" Remove failed, retrying...")
                                    returnCode = self.__ffmpeg.compress_video_file(local_filePath, targetPath=newFilePath, )

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
                                        self.__compressedVideoFiles.append(newFilePath)
                                        self.__lib.dump_list_into_file(itemList=self.__compressedVideoFiles,
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

            sleep(self.__lib.get_sleep_time())



    def _compress_image_file_delete_backup(self, filePath):
        """
        Compress image file and delete backup file that is created of old file

        :param filePath: File path of image file to __compressAll.
        :type filePath: string

        :return: subprocess object
        """

        logger = getLogger('MegaManager._compress_image_file_delete_backup')
        logger.setLevel(self.__logLevel)

        logger.debug(' Deleting compressed backup files "%s".' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        proc1 = call('python tools\\__compressImages\\__compressImages.py --mode detletebackup "%s"' % (filePath),  creationflags=CREATE_NO_WINDOW)
        return proc1


    def _create_mega_accounts_data_file(self):
        """
        Create self.__megaAccountsOutputPath file. File that has all fetched data of accounts and local and remote spaces of each account.

        :return:
        :type:
        """

        logger = getLogger('MegaManager._create_mega_accounts_data_file')
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Creating self.__megaAccountsOutputPath.txt file.')

        try:
            self.__accounts_details_dict = {}
            with open(self.__megaAccountsOutputPath, "w") as outs:
                for account in self.__foundUserPass:
                    logger.debug(' Creating thread to gather details on account %s.' % account)

                    t_megaFile = Thread(target=self._get_account_details, args=(account['user'], account['pass']),
                                                  name='thread_megaFile_%s' % account['user'])
                    t_megaFile.start()
                    self.__threads.append(t_megaFile)
                    sleep(self.__lib.get_sleep_time())


                # self._wait_for_threads_to_finish(__threads, timeout=500, sleep=1)

            outs.close()

        except (Exception, KeyboardInterrupt)as e:
            logger.debug(' Exception: %s' % e)
            if path.exists(self.__megaAccountsOutputPath + '.old'):
                copyfile(self.__megaAccountsOutputPath + '.old', self.__megaAccountsOutputPath)

    def _dump_accounts_details_dict(self):
        """
        Dump self.__accounts_details_dict to file.
        
        :return: 
        """

        logger = getLogger('MegaManager._dump_accounts_details_dict')
        logger.setLevel(self.__logLevel)

        with open(self.__megaAccountsOutputPath, "w") as outs:
            for accountDetails in sorted(self.__accounts_details_dict):
                for line in self.__accounts_details_dict[accountDetails]:
                    outs.write(line)
        outs.close()




    def _get_account_details(self, username, password):
        """
        Creats dictionary of account data (remote size, local size, etc...) for self.__megaAccountsOutputPath file.

        :param username: Username of account to get data for 
        :type username: String
        :param password: Passworde of account to get data for 
        :type password: String
        :param self.__remoteRoot: Remote path of account to get data for.
        :type self.__remoteRoot: String

        :return:
        :type:
        """

        logger = getLogger('MegaManager._get_account_details')
        logger.setLevel(self.__logLevel)

        accountDetails = []
        accountDetails.append(username + ' - ' + password + '\n')
        chdir('%s' % self.__megaToolsDir)

        freeSpace = self.__megaTools.get_account_free_space(username=username, password=password)
        accountDetails.append('FREE SIZE: ' + freeSpace)

        usedSpace = self.__megaTools.get_account_used_space(username=username, password=password)
        accountDetails.append('REMOTE SIZE: ' + usedSpace)

        subDirs = self.__megaTools.get_remote_subdir_names_only(username=username, password=password, remotePath=self.__remoteRoot)


        directoryLines = []
        totalLocalSize = 0


        for line in subDirs:
            localDirSize = 0
            localDirPath = self.__localRoot + '\\' + line
            remoteDirSize, remoteDirPath = self.__megaTools.get_remote_dir_size(username, password, localDirPath, localRoot=self.__localRoot, remoteRoot=self.__remoteRoot)

            if path.exists(localDirPath) and not line == '':
                # localDirSize = path.getsize(localDirPath)
                for r, d, f in walk(localDirPath):
                    for file in f:
                        filePath = path.join(r, file)
                        if path.exists(filePath):
                            localDirSize = localDirSize + path.getsize(filePath)

                totalLocalSize = totalLocalSize + localDirSize
                directoryLines.append(line + ' (%s remote, %s local)\n' % (self.__lib.get_mb_size_from_bytes(int(remoteDirSize)), self.__lib.get_mb_size_from_bytes(int(localDirSize))))

            elif not line == '':
                directoryLines.append(line + ' (%s remote, NONE local)\n' % (self.__lib.get_mb_size_from_bytes(int(remoteDirSize))))

        accountDetails.append('LOCAL SIZE: %s \n' % self.__lib.get_mb_size_from_bytes(totalLocalSize))

        for line in directoryLines:
            accountDetails.append(line)
        accountDetails.append('\n')
        accountDetails.append('\n')

        self.__accounts_details_dict[username] = accountDetails

    def _tear_down(self):
        """
        Tearing down of MEGA Manager.
        """
        
        logger = getLogger('MegaManager._tear_down')
        logger.setLevel(self.__logLevel)
        
        logger.info(' Tearing down megaManager!')
        try:
            if self.__removeRemote:
                self.__lib.dump_list_into_file(itemList=self.__removedRemoteFiles, filePath=self.__removedRemoteFilePath, )
            if self.__compressImages:
                self.__lib.dump_list_into_file(itemList=self.__compressedImageFiles, filePath=self.__compressedImagesFilePath, )
                self.__lib.dump_list_into_file(itemList=self.__unableToCompressImageFiles, filePath=self.__unableToCompressImagesFilePath)
            if self.__compressVideos:
                self.__lib.dump_list_into_file(itemList=self.__compressedVideoFiles, filePath=self.__compressedVideosFilePath, )
                self.__lib.dump_list_into_file(itemList=self.__unableToCompressVideoFiles, filePath=self.__unableToCompressVideosFilePath)

            self.__lib.kill_running_processes_with_name('megacopy.exe')
            self.__lib.kill_running_processes_with_name('megals.exe')
            self.__lib.kill_running_processes_with_name('megadf.exe')
            self.__lib.kill_running_processes_with_name('__ffmpeg.exe')

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

    parser.add_argument('--__download', dest='__download', action='store_true', default=False,
                        help='If true, items will be downloaded from MEGA')

    parser.add_argument('--__upload', dest='__upload', action='store_true', default=False,
                        help='If true, items will be uploaded to MEGA')

    parser.add_argument('--__removeRemote', dest='__removeRemote', action='store_true', default=False,
                        help='If true, this will allow for remote files to be removed.')

    parser.add_argument('--__removeIncomplete', dest='__removeIncomplete', action='store_true', default=False,
                        help='If true, this will allow for local downloaded files that are incomplete to be removed.')

    parser.add_argument('--__compressAll', dest='__compressAll', action='store_true', default=False,
                        help='If true, this will __compressAll local image and video files.')

    parser.add_argument('--__compressImages', dest='__compressImages', action='store_true', default=False,
                        help='If true, this will __compressAll local image files.')

    parser.add_argument('--__compressVideos', dest='__compressVideos', action='store_true', default=False,
                        help='If true, this will __compressAll local video files.')

    parser.add_argument('--__downSpeed', dest='__downSpeed', type=int, default=None,
                        help='Total __download speed limit.')

    parser.add_argument('--__upSpeed', dest='__upSpeed', type=int, default=None,
                        help='Total __upload speed limit.')

    parser.add_argument('--log', dest='__logLevel', default='INFO',
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


