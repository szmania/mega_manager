###
# Created by: Curtis Szmania
# Date: 10/1/2016
# Initial Creation
###
# Modified by: Curtis Szmania
# Date: 5/21/2017
# Pep8 compliant.
###

from account import Account
from argparse import ArgumentParser
from logging import DEBUG, getLogger, FileHandler, Formatter, StreamHandler
from libs import CompressImages_Lib, FFMPEG_Lib, Lib, MegaTools_Lib
from os import chdir, getpid, path, remove, rename, walk
from pathMapping import PathMapping
from psutil import IDLE_PRIORITY_CLASS, Process
from random import randint
from re import findall, split, sub
from shutil import copyfile
from syncprofile import SyncProfile
from sys import stdout
from tempfile import gettempdir
from threading import Thread
from time import time


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
        self.__compressionImageExtensions = COMPRESSION_IMAGE_EXTENSIONS
        self.__compressionVideoExtensions = COMPRESSION_VIDEO_EXTENSIONS
        self.__megaManager_configPath = MEGAMANAGER_CONFIG
        self.__megaManager_logFilePath = MEGAMANAGER_LOGFILEPATH
        self.__removedRemoteFilePath = REMOVED_REMOTE_FILES
        self.__unableToCompressImagesFilePath = UNABLE_TO_COMPRESS_IMAGES_FILE
        self.__unableToCompressVideosFilePath = UNABLE_TO_COMPRESS_VIDEOS_FILE

        self.__syncProfiles = []

        if path.exists(self.__megaManager_logFilePath):
            try:
                remove(self.__megaManager_logFilePath)
            except Exception as e:
                print(' Exception: %s' % str(e))
                pass

        self._assign_attributes(**kwargs)
        self._setup()

    def _all_profiles_download(self):
        """
        Download from all MEGA accounts.
        """

        logger = getLogger('MegaManager._all_profiles_download')
        logger.setLevel(self.__logLevel)

        for profile in self.__syncProfiles:
            for pathMapping in profile.pathMappings:
                self.__megaTools.download_all_files_from_account(username=profile.username, password=profile.password,
                                                                 localRoot=pathMapping['localRoot'],
                                                                 remoteRoot=pathMapping['remoteRoot'])

                # self.__megaTools.download_all_files_from_account(account['user'], account['pass'], self.__localRoot, self.__remoteRoot)

    def _all_profiles_image_compression(self):
        """
        Compress image.
        """

        logger = getLogger('MegaManager._all_profiles_image_compression')
        logger.setLevel(self.__logLevel)

        logger.debug(' Compressing local image files')

        for profile in self.__syncProfiles:
            for pathMapping in profile.pathMappings:
                self._find_image_files_to_compress(username=profile.username, password=profile.password,
                                                   localRoot=pathMapping.localPath, remoteRoot=pathMapping.remotePath)

    def _all_profiles_upload(self):
        """
        Upload to all MEGA profile accounts.
        """

        logger = getLogger('MegaManager._all_profiles_upload')
        logger.setLevel(self.__logLevel)

        for profile in self.__syncProfiles:
            for pathMapping in profile.pathMappings:
                self.__megaTools.upload_to_account(username=profile.username, password=profile.password,
                                                   localRoot=pathMapping['localRoot'],
                                                   remoteRoot=pathMapping['remoteRoot'])

    def _all_profiles_video_compression(self):
        """
        Compress video.
        """

        logger = getLogger('MegaManager._all_profiles_video_compression')
        logger.setLevel(self.__logLevel)

        logger.debug(' Compressing local video files')

        for profile in self.__syncProfiles:
            for pathMapping in profile.pathMappings:
                self._find_video_files_to_compress(username=profile.username, password=profile.password,
                                                   localRoot=pathMapping.localPath, remoteRoot=pathMapping.remotePath)

    def _assign_attributes(self, **kwargs):
        """
        Assign argumetns to class attributes.

        Args:
            kwargs (dict):  Dictionary of arguments.
        """

        for key, value in kwargs.items():
            setattr(self, '_MegaManager__%s' % key, value)

    def _create_profiles_data_file(self):
        """
        Create self.__megaAccountsOutputPath file. File that has all fetched data of accounts and local and remote spaces of each account.

        """

        logger = getLogger('MegaManager._create_profiles_data_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating self.__megaAccountsOutputPath.txt file.')

        try:
            self.__accounts_details_dict = {}
            with open(self.__megaAccountsOutputPath, "w") as outs:
                for profile in self.__syncProfiles:
                    logger.debug(' Creating thread to gather details for profile "%s".' % profile.profileName)

                    t_megaFile = Thread(target=self._get_profile_details, args=(profile, ),
                                        name='thread_megaFile_%s' % profile.profileName)
                    t_megaFile.start()
                    self.__threads.append(t_megaFile)

            outs.close()

        except (Exception, KeyboardInterrupt)as e:
            logger.debug(' Exception: %s' % e)
            if path.exists(self.__megaAccountsOutputPath + '.old'):
                copyfile(self.__megaAccountsOutputPath + '.old', self.__megaAccountsOutputPath)

    def _create_thread_create_profiles_data_file(self):
        """
        Create thread to create profiles data file.
        """

        logger = getLogger('MegaManager._create_thread_create_profiles_data_file')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to create "%s" file.' % self.__megaAccountsOutputPath)

        t = Thread(target=self._create_profiles_data_file, name='thread_create_profiles_data_file')
        self.__threads.append(t)
        t.start()

    def _create_thread_download(self):
        """
        Create thread to download files.
        """

        logger = getLogger('MegaManager._create_thread_download')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to download files from MEGA accounts.')

        t = Thread(target=self._all_profiles_download, args=(), name='thread_download')
        self.__threads.append(t)
        t.start()

    def _create_thread_upload(self):
        """
        Create thread to upload files.
        """

        logger = getLogger('MegaManager._create_thread_upload')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating thread to upload files to MEGA accounts.')

        t = Thread(target=self._all_profiles_upload, args=(), name='thread_upload')
        self.__threads.append(t)
        t.start()

    def _create_threads_local_unfinished_file_remover(self):
        """
        Create threads to remove unfinished local downloaded files.
        """

        logger = getLogger('MegaManager._create_threads_local_unfinished_file_remover')
        logger.setLevel(self.__logLevel)

        logger.debug(' Creating threads to remove unfinished files.')

        for profile in self.__syncProfiles:
            profileName = profile.profileName
            username = profile.username
            password = profile.password

            for pathMapping in profile.pathMappings:
                localPath = pathMapping.localPath
                remotePath = pathMapping.remotePath
                t_unfinishedFileRemover = Thread(target=self.__megaTools.remove_local_incomplete_files, args=(
                    username, password, localPath, remotePath,),
                                                 name='thread_unfinishedFileRemover_%s' % profileName)
                self.__threads.append(t_unfinishedFileRemover)
                t_unfinishedFileRemover.start()

        # for account in self.__foundUserPass:
        #     t_unfinishedFileRemover = Thread(target=self.__megaTools.remove_local_incomplete_files, args=(
        #     account['user'], account['pass'], self.__localRoot, self.__remoteRoot,),
        #                                      name='thread_unfinishedFileRemover_%s' % account['user'])
        #     self.__threads.append(t_unfinishedFileRemover)
        #     t_unfinishedFileRemover.start()

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

        t_compress = Thread(target=self._all_profiles_image_compression, args=( ), name='thread_compressImages')
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

        t_compress = Thread(target=self._all_profiles_video_compression, args=( ), name='thread_compressVideos')
        self.__threads.append(t_compress)
        t_compress.start()

    def _delete_remote_files_that_dont_exist_locally(self, username, password):
        """
        Remove remote files that don't exist locally.

        Args:
            username (str): username of account to upload to
            password (str): Password of account to upload to
        """

        logger = getLogger('MegaManager._delete_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__logLevel)

        logger.debug(' Deleting remote files that do not exist locally on %s - %s.' % (username, password))

        dontExistLocally = self._get_remote_files_that_dont_exist_locally(username=username, password=password)

        for filePath in dontExistLocally:

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

    def _export_accounts_details_dict(self):
        """
        Dump self.__accounts_details_dict to file.

        """

        logger = getLogger('MegaManager._export_accounts_details_dict')
        logger.setLevel(self.__logLevel)

        with open(self.__megaAccountsOutputPath, "w") as outs:
            for username in sorted(self.__accounts_details_dict):
                accountObj = self.__accounts_details_dict[username]
                lines = []
                line = 'Total Space: ' + str(accountObj.remote_totalSpace)
                lines.append(line)
                line = 'Used Space: ' + str(accountObj.remote_usedSpace)
                lines.append(line)
                line = 'Free Space: ' + str(accountObj.remote_freeSpace)
                lines.append(line)
                outs.write(lines)
        outs.close()

    def _export_config_file_data(self):
        """
        Export config file data.

        """

        logger = getLogger('MegaManager._export_config_file_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Exporting config data to MEGA Manager config file.')
        try:
            with open(self.__megaManager_configPath, "w") as outs:
                outs.write('MEGATOOLS_DIR=%s' % str(self.__megaToolsDir))
                outs.write('FFMPEG_EXE_PATH=%s' % str(self.__ffmpegExePath))
                outs.write('MEGA_ACCOUNTS=%s' % str(self.__megaAccountsPath))
                outs.write('MEGA_ACCOUNTS_OUTPUT=%s' % str(self.__megaAccountsOutputPath))

                profileCount = 0
                for profile in self.__syncProfiles:
                    profileCount += 1
                    outs.write('[Profile%d]' % profileCount)
                    outs.write('ProfileName=%s' % str(profile.profileName))
                    outs.write('Username=%s' % str(profile.username))
                    outs.write('Password=%s' % str(profile.password))

                    pathMappingsCount = 0
                    for pathMapping in profile.pathMappings:
                        pathMappingsCount += 1
                        outs.write('LocalPath%d=%s' % (pathMappingsCount, str(pathMapping.localPath)))
                        outs.write('RemotePath%d=%s' % (pathMappingsCount, str(pathMapping.remotPath)))

            outs.close()
            return True
        except Exception as e:
            logger.error(' Exception: %s' % str(e))
            return False

    def _find_image_files_to_compress(self, username, password, localRoot, remoteRoot):
        """
        Find image files to compress.

        Args:
            username (str): Username of account to find local images for.
            password (str): Password of account to find local images for.
            localRoot (str): Local path to search for image files to compress
            remoteRoot (str): Remote path to search for image files to compress
        """

        logger = getLogger('MegaManager._find_image_files_to_compress')
        logger.setLevel(self.__logLevel)

        logger.debug(' Compressing image files.')

        localRoot_adj = sub('\\\\', '/', localRoot)
        # chdir('%s' % self.__megaToolsDir)

        # cmd = 'megals -lR -u %s -p %s "%s"' % (username, password, self.__remoteRoot)
        # proc = Popen(cmd, stdout=PIPE, shell=True)

        # (out, err) = proc.communicate()
        # lines = out.split('\r\n')

        lines = self.__megaTools.get_remote_file_data_recursively(username=username, password=password,
                                                                  remotePath=remoteRoot)

        if lines:
            for line in lines:
                remote_type = self.__megaTools.get_file_type_from_megals_line_data(line=line)
                remote_fileExt = self.__megaTools.get_file_extension_from_megals_line_data(line=line)
                remote_filePath = self.__megaTools.get_file_path_from_megals_line_data(line=line)
                file_subPath = sub(remoteRoot, '', remote_filePath)
                local_filePath = localRoot_adj + file_subPath

                if remote_type == '0' and remote_fileExt in self.__compressionImageExtensions and \
                                path.isfile(local_filePath) and (local_filePath not in self.__compressedImageFiles) \
                                and (local_filePath not in self.__unableToCompressImageFiles):

                    newFilePath = local_filePath.rsplit(".", 1)[0] + '_NEW.mp4'

                    result = self.__compressImages_lib.compress_image_file(filePath=local_filePath)
                    if result:
                        compressPath_backup = local_filePath + '.compressimages-backup'
                        if path.exists(compressPath_backup):
                            logger.debug(' File compressed successfully "%s"!' % local_filePath)
                            try:
                                remove(compressPath_backup)
                            except WindowsError as e:
                                logger.warning(' Exception: %s' % str(e))
                                pass

                            self.compressedFiles = []
                            self.compressedFiles.append(local_filePath)
                            self.__lib.dump_list_into_file(itemList=self.__compressedImageFiles,
                                                           filePath=self.__compressedImagesFilePath, )

                        else:
                            logger.debug(
                                ' File cannot be compressed any further "%s"!' % local_filePath)
                            self.__unableToCompressImageFiles.append(local_filePath)
                            self.__lib.dump_list_into_file(
                                itemList=self.__unableToCompressImageFiles,
                                filePath=self.__unableToCompressImagesFilePath, )

                    else:
                        logger.debug(
                            ' Error, image file could not be compressed "%s"!' % local_filePath)
                        self.__unableToCompressImageFiles.append(local_filePath)
                        self.__lib.dump_list_into_file(itemList=self.__unableToCompressImageFiles,
                                                       filePath=self.__unableToCompressImagesFilePath)


                    else:
                        logger.debug(
                            ' Error, image file previously processed. Moving on.  "%s"!' % local_filePath)
                else:
                    logger.debug(
                        ' Error, image file does NOT exist locally. Moving on.  "%s"!' % local_filePath)


    def _find_video_files_to_compress(self, username, password, localRoot, remoteRoot):
        """
        Find video files to __compressAll.

        Args:
            username (str): username of account to find local video files for
            password (str): password of account to find local video files for
            localRoot (str): Local path to search for image files to compress
            remoteRoot (str): Remote path to search for image files to compress
        """

        logger = getLogger('MegaManager._find_video_files_to_compress')
        logger.setLevel(self.__logLevel)

        logger.debug(' Finding video files to compress.')

        localRoot_adj = sub('\\\\', '/', localRoot)

        lines = self.__megaTools.get_remote_file_data_recursively(username=username, password=password,
                                                                  remotePath=remoteRoot)

        if lines:
            for line in lines:
                remote_type = self.__megaTools.get_file_type_from_megals_line_data(line=line)
                remote_fileExt = self.__megaTools.get_file_extension_from_megals_line_data(line=line)
                remote_filePath = self.__megaTools.get_file_path_from_megals_line_data(line=line)
                file_subPath = sub(remoteRoot, '', remote_filePath)
                local_filePath = localRoot_adj + file_subPath

                # remote_type = line.split()[2]
                if remote_type == '0' and remote_fileExt in self.__compressionVideoExtensions and \
                                path.isfile(local_filePath) and (local_filePath not in self.__compressedVideoFiles) \
                                and (local_filePath not in self.__unableToCompressVideoFiles):

                    newFilePath = local_filePath.rsplit(".", 1)[0] + '_NEW.mp4'

                    if path.exists(newFilePath):
                        for retry in range(100):
                            try:
                                remove(newFilePath)
                                break
                            except:
                                logger.debug(" Remove failed, retrying...")
                    result = self.__ffmpeg.compress_video_file(local_filePath,
                                                               targetPath=newFilePath, )

                    if result == True and path.exists(newFilePath):
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

                        logger.debug(' Video file compressed successfully "%s" into "%s"!' % (
                        local_filePath, newFilePath))
                        self.__compressedVideoFiles.append(newFilePath)
                        self.__lib.dump_list_into_file(itemList=self.__compressedVideoFiles,
                                                       filePath=COMPRESSED_VIDEOS_FILE, )

                    elif path.exists(newFilePath):
                        remove(newFilePath)

                    else:
                        logger.debug(
                            ' Error, video file could not be compressed "%s"!' % local_filePath)

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
                        username = sub('\\n', '', sub(' - .*', '', line))
                        password = sub('\\n', '', sub('.* - ', '', line))

                        dict['user'] = username
                        dict['pass'] = password
                        foundUserPass.append(dict)
            ins.close()
        except Exception as e:
            logger.warning(' Exception: %s' % str(e))

        return foundUserPass

    def _get_profile_details(self, profile):
        """
        Creats dictionary of account data (remote size, local size, etc...) for self.__megaAccountsOutputPath file.

        Args:
            profile (SyncProfile): Profile to get data for.
        """

        profile = self._update_account_remote_details(profile=profile)

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

        remoteFiles = self.__megaTools.get_remote_file_paths_recursively(username=username, password=password,
                                                                         remotePath=self.__remoteRoot)

        dontExistLocally = []
        for remote_filePath in remoteFiles:
            file_subPath = sub(self.__remoteRoot, '', remote_filePath)
            local_filePath = localRoot_adj + file_subPath

            if not path.exists(local_filePath):
                dontExistLocally.append(local_filePath)

        return dontExistLocally

    def _import_config_file_data(self):
        """
        Load config file.
        """

        logger = getLogger('MegaManager._import_config_file_data')
        logger.setLevel(self.__logLevel)

        logger.debug(' Loading megaManager.cfg file.')

        with open(self.__megaManager_configPath, "r") as ins:
            line = ins.readline()
            while line:
                if line.startswith('MEGATOOLS_DIR='):
                    value = split('=', line)[1].strip()
                    self.__megaToolsDir = value
                elif line.startswith('FFMPEG_EXE_PATH='):
                    value = split('=', line)[1].strip()
                    self.__ffmpegExePath = value
                elif line.startswith('MEGA_ACCOUNTS='):
                    value = split('=', line)[1].strip()
                    self.__megaAccountsPath = value
                elif line.startswith('MEGA_ACCOUNTS_OUTPUT='):
                    value = split('=', line)[1].strip()
                    self.__megaAccountsOutputPath = value
                elif line.startswith('[Profile'):
                    self.__syncProfiles.append(self._import_config_profile_data(fileObject=ins))

                elif line.startswith('LOCAL_ROOT='):
                    value = split('=', line)[1].strip()
                    self.__localRoot = value
                elif line.startswith('REMOTE_ROOT='):
                    value = split('=', line)[1].strip()
                    self.__remoteRoot = value

                line = ins.readline()
        ins.close()

    def _import_config_profile_data(self, fileObject):
        """
        Load config profile data.

        Args:
            fileObject (object): File object handle.
        """

        logger = getLogger('MegaManager._import_config_profile_data')
        logger.setLevel(self.__logLevel)

        profileName = None
        username = None
        password = None
        pathMappings = []

        line = fileObject.readline()

        while (not line.startswith('[Profile')) and line:

            if line.startswith('ProfileName='):
                value = split('=', line)[1].strip()
                profileName = value
            elif line.startswith('Username='):
                value = split('=', line)[1].strip()
                username = value
            elif line.startswith('Password='):
                value = split('=', line)[1].strip()
                password = value
            elif line.startswith('LocalPath'):
                localPath = split('=', line)[1].strip()
                line = fileObject.readline()
                if line.startswith('RemotePath'):
                    remotePath = split('=', line)[1].strip()
                    pathMappingObj = PathMapping(localPath=localPath, remotePath=remotePath, logLevel=self.__logLevel)
                    pathMappings.append(pathMappingObj)

            line = fileObject.readline()

        syncProfileObj = SyncProfile(profileName=profileName, username=username, password=password,
                                     pathMappings=pathMappings)
        return syncProfileObj

    def _setup(self):
        """
        Setup MegaManager applicaiton.
        """

        try:
            self._setup_logger(self.__megaManager_logFilePath)
            self._import_config_file_data()

            self.__compressImages_lib = CompressImages_Lib(logLevel=self.__logLevel)
            self.__ffmpeg = FFMPEG_Lib(ffmpegExePath=self.__ffmpegExePath, logLevel=self.__logLevel)
            self.__lib = Lib(logLevel=self.__logLevel)
            self.__megaTools = MegaTools_Lib(megaToolsDir=self.__megaToolsDir, downSpeedLimit=self.__downSpeed,
                                             upSpeedLimit=self.__upSpeed, logLevel=self.__logLevel)

            # self.__foundUserPass = self._get_accounts_user_pass(file=self.__megaAccountsPath)

        except Exception as e:
            print(' Exception: ' + str(e))
            self._tear_down()

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

    def _tear_down(self):
        """
        Tearing down of MEGA Manager.
        """

        logger = getLogger('MegaManager._tear_down')
        logger.setLevel(self.__logLevel)

        logger.info(' Tearing down megaManager!')
        try:
            if self.__removeRemote:
                self.__lib.dump_list_into_file(itemList=self.__removedRemoteFiles,
                                               filePath=self.__removedRemoteFilePath, )
            if self.__compressImages:
                self.__lib.dump_list_into_file(itemList=self.__compressedImageFiles,
                                               filePath=self.__compressedImagesFilePath, )
                self.__lib.dump_list_into_file(itemList=self.__unableToCompressImageFiles,
                                               filePath=self.__unableToCompressImagesFilePath)
            if self.__compressVideos:
                self.__lib.dump_list_into_file(itemList=self.__compressedVideoFiles,
                                               filePath=self.__compressedVideosFilePath, )
                self.__lib.dump_list_into_file(itemList=self.__unableToCompressVideoFiles,
                                               filePath=self.__unableToCompressVideosFilePath)

            self.__lib.kill_running_processes_with_name('megacopy.exe')
            self.__lib.kill_running_processes_with_name('megals.exe')
            self.__lib.kill_running_processes_with_name('megadf.exe')
            self.__lib.kill_running_processes_with_name('ffmpeg.exe')

        except Exception as e:
            logger.debug(' Exception: %s' % str(e))
            pass

    def _update_account_remote_details(self, profile):
        """
        Gather data for profile (remote used space, remote free space, remote total space, etc...).

        Args:
            profile (SyncProfile): Account object to gather data for.

        Returns:
            Profile: profile object with remote data updated
        """

        logger = getLogger('MegaManager._update_account_remote_details')
        logger.setLevel(self.__logLevel)

        username = profile.username
        password = profile.password

        profile.account_totalSpace = self.__megaTools.get_account_total_space(username=username, password=password)

        profile.account_freeSpace = self.__megaTools.get_account_free_space(username=username, password=password)

        profile.account_usedSpace = self.__megaTools.get_account_used_space(username=username, password=password)
        # accountDetails.append('REMOTE SIZE: ' + usedSpace)
        #
        # subDirs = self.__megaTools.get_remote_subdir_names_only(username=username, password=password, remotePath=self.__remoteRoot)
        #
        # directoryLines = []
        # totalLocalSize = 0
        #
        # if subDirs:
        #     for line in subDirs:
        #         localDirSize = 0
        #         localDirPath = self.__localRoot + '\\' + line
        #
        #         if path.exists(localDirPath) and not line == '':
        #             for r, d, f in walk(localDirPath):
        #                 for file in f:
        #                     filePath = path.join(r, file)
        #                     if path.exists(filePath):
        #                         localDirSize = localDirSize + path.getsize(filePath)
        #
        #             totalLocalSize = totalLocalSize + localDirSize
        #             remoteDirSize = self.__megaTools.get_remote_dir_size(username, password, localDirPath,
        #                                                                  localRoot=self.__localRoot,
        #                                                                  remoteRoot=self.__remoteRoot)
        #
        #             directoryLines.append(line +
        #                                   ' (%s remote, %s local)\n' % (self.__lib.get_mb_size_from_bytes(int(remoteDirSize)), self.__lib.get_mb_size_from_bytes(int(localDirSize))))
        #
        #         elif not line == '':
        #             directoryLines.append(line + ' (%s remote, NONE local)\n' % (self.__lib.get_mb_size_from_bytes(int(remoteDirSize))))
        #
        #     accountDetails.append('LOCAL SIZE: %s \n' % self.__lib.get_mb_size_from_bytes(totalLocalSize))
        #
        #     for line in directoryLines:
        #         accountDetails.append(line)
        #     accountDetails.append('\n')
        #     accountDetails.append('\n')
        #
        #     self.__accounts_details_dict[username] = accountDetails

        return profile

    def _update_profile_remote_details(self, profile):
        """
        Gather data for profile (remote size, local size, etc...) for self.__megaAccountsOutputPath file.

        Args:
            profile (SyncProfile): profile object to gather data for.

        Returns:
            SyncProfile: profile object with remote data updated
        """

        logger = getLogger('MegaManager._update_profile_remote_details')
        logger.setLevel(self.__logLevel)

        username = profile.username
        password = profile.password
        totalRemoteSize = 0

        for pathMapping in profile.pathMappings:
            remotePath = pathMapping.remotepath
            remotePaths = self.__megaTools.get_remote_file_paths_recursively(username=username, password=password, remotePath=remotePath)

            pathMappingRemoteSize = 0
            for path in remotePaths:
                pathMappingRemoteSize += self.__megaTools.get_remote_file_size(username=username, password=password, remotePath=path)

            pathMapping.remotePath_usedSpace = pathMappingRemoteSize
            totalRemoteSize += pathMappingRemoteSize
        return profile

    def _wait_for_threads_to_finish(self, timeout=99999):
        """
        Wait for threads to finish.

        Args:
            timeout (int): Maximum time in seconds to wait for threads.
        """

        logger = getLogger('MegaManager._wait_for_threads_to_finish')
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Waiting for threads to finish.')

        startTime = time()
        megaFileFinished = False

        while len(self.__threads) > 0:
            megaFileThreads_found = False

            if not time() - startTime > timeout:
                for thread in self.__threads:
                    if not thread.isAlive():
                        self.__threads.remove(thread)
                        logger.info(' Thread "%s" finished!' % thread.name)
                        logger.debug(' Threads left: %d' % len(self.__threads))
                    else:
                        if 'megaFile' in thread.name:
                            megaFileThreads_found = True

                if not megaFileThreads_found and not megaFileFinished:
                    self._export_accounts_details_dict()
                    logger.info(' "%s" file creation complete!' % self.__megaAccountsOutputPath)
                    megaFileFinished = True
            else:
                logger.debug(' Waiting for threads to complete TIMED OUT! Timeout %d (seconds)' % timeout)
                return

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

            self._create_thread_create_profiles_data_file()

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

def get_args():
    """
    Get arguments from command line, and returns them as dictionary.

    Returns:
        Dictionary: Dictionary of arguments for MEGA Manager.
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

    parser.add_argument('--compressAll', dest='compressAll', action='store_true', default=False,
                        help='If true, this will compressAll local image and video files.')

    parser.add_argument('--compressImages', dest='compressImages', action='store_true', default=False,
                        help='If true, this will compressAll local image files.')

    parser.add_argument('--compressVideos', dest='compressVideos', action='store_true', default=False,
                        help='If true, this will __compressAll local video files.')

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


