# Created by: Curtis Szmania
# Date: 10/1/2016
# Initial Creation

__author__='szmania'


import re
import subprocess
import os
import threading
import time
import argparse
import logging
import sys
import shutil
import psutil
from random import randint
import tempfile
# import requests
# import xml.etree.ElementTree as ET
# import feedparser
# from requests import session
# import sys
# import io
# import math
# import socket
# logger.info(socket.gethostname())

MEGAMANAGER_CONFIG = 'megaManager.cfg'

# MEGATOOLS_PATH = 'D:\\Program Files (x86)\\megatools'
# MEGA_ACCOUNTS = "I:\\Games\\1\\MEGA_ACCOUNTS.txt"
# LOCAL_ROOT = 'I:\\Games\\1\\Done\\MEGA'
# REMOTE_ROOT = '/Root/Porn'

MEGA_locations = "I:\\Games\\1\\MEGA_locations_ALL.txt"
MEGA_locations_ALL_output = "I:\\Games\\1\\MEGA_locations_ALL.txt"
WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

COMPRESSED_IMAGES_FILE =  WORKING_DIR + "compressed_images.tmp"
UNABLE_TO_COMPRESS_IMAGES_FILE =  WORKING_DIR + "unable_to_compress_images.tmp"
COMPRESSED_VIDEOS_FILE =  WORKING_DIR + "compressed_videos.tmp"
UNABLE_TO_COMPRESS_VIDEOS_FILE = WORKING_DIR + "unable_to_compress_videos.tmp"


LOGFILE_stdout = os.path.dirname(os.path.realpath(__file__)) + '\mega_stdout.log'
LOGFILE_stderr = os.path.dirname(os.path.realpath(__file__)) + '\mega_stderr.log'
LOGFILE_mega = os.path.dirname(os.path.realpath(__file__)) + '\megaManager_log.log'



class MegaManager(object):
    def __init__(self, **kwargs):
        self.threads = []

        if os.path.getsize(LOGFILE_mega) > 10000000:
            os.remove(LOGFILE_mega)


        for key, value in kwargs.items():
            setattr(self, key, value)

        self._setLogger(LOGFILE_mega)

        self._load_configFile()

    def _setLogger(self, logFile):
        """
        Logger setup.

        @param: logFile:  Log file path.

        @return: None
        """

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        self.handler = logging.FileHandler(logFile)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

        # formatter = logging.Formatter(fmt='%(message)s', datefmt='')
        self.handler.setLevel(logging.DEBUG)
        self.handler.setFormatter(formatter)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(self.logLevel)
        ch.setFormatter(formatter)

        root.addHandler(self.handler)
        root.addHandler(ch)

        logger = logging.getLogger('MegaManager._setLogger')
        logger.setLevel(self.logLevel)

        logger.info(' Logging to %s' % LOGFILE_mega)


    def _load_configFile(self):

        logger = logging.getLogger('MegaManager._load_configFile')
        logger.setLevel(self.logLevel)

        logger.debug(' Loading megaManager.cfg file.')

        with open(MEGAMANAGER_CONFIG, "r") as ins:
            for line in ins:
                if '=' in line:
                    value = re.split('=', line)[1].strip()
                    if line.startswith('MEGATOOLS_PATH'):
                        global MEGATOOLS_PATH
                        MEGATOOLS_PATH = value
                    elif line.startswith('MEGA_ACCOUNTS'):
                        global MEGA_ACCOUNTS
                        MEGA_ACCOUNTS = value
                    elif line.startswith('LOCAL_ROOT'):
                        global LOCAL_ROOT
                        LOCAL_ROOT = value
                    elif line.startswith('REMOTE_ROOT'):
                        global REMOTE_ROOT
                        REMOTE_ROOT = value


    def _load_compressedLists(self):
        logger = logging.getLogger('MegaManager._load_compressedLists')
        logger.setLevel(self.logLevel)

        logger.debug(' Loading %s file.' % COMPRESSED_IMAGES_FILE)
        self.compressedImageFiles = []

        if os.path.exists('%s\\%s' % (WORKING_DIR, COMPRESSED_IMAGES_FILE)):
            with open('%s\\%s' % (WORKING_DIR, COMPRESSED_IMAGES_FILE), "r") as ins:
                self.compressedImageFiles = [line.rstrip('\n') for line in ins]

        logger.debug(' Loading %s file.' % UNABLE_TO_COMPRESS_IMAGES_FILE)
        self.unableToCompressImageFiles = []

        if os.path.exists('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_IMAGES_FILE)):
            with open('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_IMAGES_FILE), "r") as ins:
                self.unableToCompressImageFiles = [line.rstrip('\n') for line in ins]


        logger.debug(' Loading %s file.' % COMPRESSED_VIDEOS_FILE)
        self.compressedVideoFiles = []

        if os.path.exists('%s\\%s' % (WORKING_DIR, COMPRESSED_vIDEOS_FILE)):
            with open('%s\\%s' % (WORKING_DIR, COMPRESSED_VIDEOS_FILE), "r") as ins:
                self.compressedVideoFiles = [line.rstrip('\n') for line in ins]

        logger.debug(' Loading %s file.' % UNABLE_TO_COMPRESS_IMAGES_FILE)
        self.unableToCompressVideoFiles = []

        if os.path.exists('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_VIDEOS_FILE)):
            with open('%s\\%s' % (WORKING_DIR, UNABLE_TO_COMPRESS_VIDEOS_FILE), "r") as ins:
                self.unableToCompressVideoFiles = [line.rstrip('\n') for line in ins]



    def _dump_compressedImageFileList(self):
        logger = logging.getLogger('MegaManager._dump_compressedImageFileList')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.compressedImageFiles to %s file.' % COMPRESSED_IMAGES_FILE)

        compressedList_file = open('%s' % (COMPRESSED_IMAGES_FILE), 'w')

        for compressedFilePath in self.compressedImageFiles:
            compressedList_file.write("%s\n" % compressedFilePath)


    def _dump_compressedVideoFileList(self):
        logger = logging.getLogger('MegaManager._dump_compressedVideoFileList')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.compressedVideoFiles to %s file.' % COMPRESSED_VIDEOS_FILE)

        compressedList_file = open('%s' % (COMPRESSED_VIDEOS_FILE), 'w')

        for compressedFilePath in self.compressedVideoFiles:
            compressedList_file.write("%s\n" % compressedFilePath)


    def _dump_unableToCompressImageFileList(self):
        logger = logging.getLogger('MegaManager._dump_unableToCompressImageFileList')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.unableToCompressImageFiles to %s file.' % UNABLE_TO_COMPRESS_IMAGES_FILE)

        unCompressedList_file = open('%s' % (UNABLE_TO_COMPRESS_IMAGES_FILE), 'w')

        for unCompressedFilePath in self.unableToCompressImageFiles:
            unCompressedList_file.write("%s\n" % unCompressedFilePath)


    def _dump_unableToCompressVideoFileList(self):
        logger = logging.getLogger('MegaManager._dump_unableToCompressVideoFileList')
        logger.setLevel(self.logLevel)

        logger.debug(' Dumping self.unableToCompressVideoFiles to %s file.' % UNABLE_TO_COMPRESS_VIDEOS_FILE)

        unCompressedList_file = open('%s' % (UNABLE_TO_COMPRESS_VIDEOS_FILE), 'w')

        for unCompressedFilePath in self.unableToCompressImageFiles:
            unCompressedList_file.write("%s\n" % unCompressedFilePath)


    def run(self):
        logger = logging.getLogger('MegaManager.run')
        logger.setLevel(self.logLevel)

        logger.debug(' Running megaManager.')

        try:
            self._createThread_createMEGA_locationsFile()

            self._createThreads_unfinishedFileRemover()

            if self.download:
                self._createThreads_download()
            if self.upload:
                self._createThreads_upload()
            if self.removeRemote:
                self._createThreads_remoteFileRemoval()

            if self.compress:
                self._createThreads_compressImageFiles()
                self._createThreads_compressVideoFiles()
            elif self.compressImages:
                self._createThreads_compressImageFiles()
            elif self.compressVideos:
                self._createThreads_compressVideoFiles()

            self._waitForFinished()

        except Exception as e:
            logger.debug(' Exception: ' + str(e))
            self._tearDown()


    def _createThread_createMEGA_locationsFile(self):
        logger = logging.getLogger('MegaManager._createThread_createMEGA_locationsFile')
        logger.setLevel(self.logLevel)

        logger.debug(' Creating thread to create MEGA_locations.txt file.')

        t_unfinishedFileRemover = threading.Thread(target=self._create_MEGA_locationsFile, name='thread_createMEGA_locationsFile')
        t_unfinishedFileRemover.start()


    def _createThreads_unfinishedFileRemover(self):
        logger = logging.getLogger('MegaManager._createThreads_unfinishedFileRemover')
        logger.setLevel(self.logLevel)

        logger.debug(' Creating threads to remove unfinished files.')

        foundUserPass = self._getUserPass()

        for account in foundUserPass:
            t_unfinishedFileRemover = threading.Thread(target=self._deleteIncompleteFiles, args=(account['user'], account['pass'],), name='thread_unfinishedFileRemover_%s' % account['user'])
            # self.threads.append(t_unfinishedFileRemover)
            t_unfinishedFileRemover.start()

            time.sleep(self._getSpeed())

    def _createThreads_download(self):
        logger = logging.getLogger('MegaManager._createThreads_download')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating threads to download files from MEGA, for each account.')

        foundUserPass = self._getUserPass()

        for account in foundUserPass:

            t = threading.Thread(target=self._download, args=(account['user'], account['pass'], ), name='thread_download_%s' % account['user'])
            self.threads.append(t)
            t.start()

            time.sleep(self._getSpeed())


    def _createThreads_upload(self):
        logger = logging.getLogger('MegaManager._createThreads_upload')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating threads to upload files to MEGA, for each account.')

        foundUserPass = self._getUserPass()

        for account in foundUserPass:

            t = threading.Thread(target=self._upload, args=(account['user'], account['pass'], ), name='thread_upload_%s' % account['user'])
            self.threads.append(t)
            t.start()
            time.sleep(self._getSpeed())

    def _createThreads_remoteFileRemoval(self):
        logger = logging.getLogger('MegaManager._createThreads_remoteFileRemoval')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to remove files remotely.')

        t_remover = threading.Thread(target=self._remoteFileRemoval, args=( ), name='thread_remoteFileRemover')
        self.threads.append(t_remover)
        t_remover.start()


    def _remoteFileRemoval(self):
        logger = logging.getLogger('MegaManager._remoteFileRemoval')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Removing remote files.')

        foundUserPass = self._getUserPass( file="I:\\Games\\1\\MEGA_accounts.txt")

        for account in foundUserPass:
            self._deleteRemoteFiles(account['user'], account['pass'])
            # t_remover = threading.Thread(target=self._deleteRemoteFiles, args=(account['user'], account['pass'], ), name='thread_remoteRemover_%s' % account['user'])
            # self.threads.append(t_remover)
            # t_remover.start()
            time.sleep(self._getSpeed())

    def _createThreads_compressImageFiles(self):
        logger = logging.getLogger('MegaManager._createThreads_compressImageFiles')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to compress local image files.')
        self._load_compressedLists()

        t_compress = threading.Thread(target=self._imageCompression, args=( ), name='thread_compressImages')
        self.threads.append(t_compress)
        t_compress.start()


    def _createThreads_compressVideoFiles(self):
        logger = logging.getLogger('MegaManager._createThreads_compressVideoFiles')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating thread to compress local video files.')
        self._load_compressedLists()

        t_compress = threading.Thread(target=self._videoCompression, args=( ), name='thread_compressVideos')
        self.threads.append(t_compress)
        t_compress.start()


    def _imageCompression(self):
        logger = logging.getLogger('MegaManager._imageCompression')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Compressing local image files')
        foundUserPass = self._getUserPass( file="I:\\Games\\1\\MEGA_accounts.txt")

        for account in foundUserPass:
            self._compressImageFiles(account['user'], account['pass'])
            # t_remover = threading.Thread(target=self._deleteRemoteFiles, args=(account['user'], account['pass'], ), name='thread_remoteRemover_%s' % account['user'])
            # self.threads.append(t_remover)
            # t_remover.start()
            time.sleep(self._getSpeed())

    def _videoCompression(self):
        logger = logging.getLogger('MegaManager._videoCompression')
        logger.setLevel(self.logLevel)

        logger.debug(' Compressing local video files')
        foundUserPass = self._getUserPass( file="I:\\Games\\1\\MEGA_accounts.txt")

        for account in foundUserPass:
            self._compressVideoFiles(account['user'], account['pass'])
            time.sleep(self._getSpeed())

    def _deleteIncompleteFiles(self, username, password):
        logger = logging.getLogger('MegaManager._deleteIncompleteFiles')
        logger.setLevel(self.logLevel)
        
        self._getRemoteFilePaths(username, password)


    def _getRemoteFilePaths(self, user, password):
        logger = logging.getLogger('MegaManager._getRemoteFilePaths')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)

        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'start /B megals -ln -u %s -p %s' % (user, password)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

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
                        if REMOTE_ROOT in remoteFilePath:
                            remote_root = REMOTE_ROOT.replace('/', '\\')
                            local_root = LOCAL_ROOT
                            conv_remoteFilePath = remoteFilePath.replace('/', '\\')
                            localFilePath = conv_remoteFilePath.replace(remote_root, local_root)
                            if os.path.exists(localFilePath):
                                if os.path.isfile(localFilePath):
                                    localFileSize = os.path.getsize(localFilePath)
                                    if localFileSize < int(remoteFileSize):
                                        logger.debug(' File incomplete. Deleting file "%s"' % localFilePath)
                                        try:
                                            os.rename(localFilePath, localFilePath)
                                            os.remove(localFilePath)
                                        except OSError as e:
                                            logger.debug(' Access-error on file "' + localFilePath + '"! \n' + str(e))


    def _getRemoteFileSize(self, user, password, localFilePath):
        logger = logging.getLogger('MegaManager._getRemoteFileSize')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)
        localFilePath_adj = re.sub('\\\\', '/',localFilePath)
        postfix = re.split(LOCAL_ROOT_adj, localFilePath_adj)
        if len(postfix) > 1:
            subPath = postfix[1]

            os.chdir('%s' % MEGATOOLS_PATH)

            cmd = 'start /B megals -ln -u %s -p %s "%s"' % (user, password, REMOTE_ROOT + subPath)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

            (out, err) = proc.communicate()
            line_split = out.split()
            if len(line_split) > 2:
                remoteFileSize = line_split[3]

                return remoteFileSize, REMOTE_ROOT + subPath

        return 0, ''


    def _getRemoteDirSize(self, user, password, localDirPath):
        logger = logging.getLogger('MegaManager._getRemoteDirSize')
        logger.setLevel(self.logLevel)

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)
        localFilePath_adj = re.sub('\\\\', '/',localDirPath)
        postfix = re.split(LOCAL_ROOT_adj, localFilePath_adj)
        if len(postfix) > 1:
            subPath = postfix[1]

            os.chdir('%s' % MEGATOOLS_PATH)

            cmd = 'start /B megals -lnR -u %s -p %s "%s"' % (user, password, REMOTE_ROOT + subPath)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

            (out, err) = proc.communicate()
            lines = out.split('\r\n')
            totalRemoteDirSize = 0
            for line in lines:
                line_split = line.split()
                if len(line_split) > 2:
                    remoteFileSize = line_split[3]
                    if remoteFileSize.isdigit():
                        totalRemoteDirSize = totalRemoteDirSize + int(remoteFileSize)


            return totalRemoteDirSize, REMOTE_ROOT + subPath

        return 0, ''


    def _remove_incompleteFiles(self, temp_logFile_path):
        logger = logging.getLogger('MegaManager._remove_incompleteFiles')
        logger.setLevel(self.logLevel)
        
        temp_stderr_file = open(temp_logFile_path, "r")
        # with open(temp_logFile_path, 'r') as temp_stderr_file:
        #     for line in temp_stderr_file:
        lines = temp_stderr_file.readlines()
        for line in lines:
            if 'already exists at ' in line:
                localFilePath = re.split('already exists at ', line)[1].replace('\n', '').replace('\r', '')
                if os.path.exists(localFilePath):
                    localFileSize = os.path.getsize(localFilePath)

                    split_line = re.split(' - ', re.split(':', line)[0])

                    if len(split_line) > 1:
                        user = split_line[0]
                        password = split_line[1]
                        remoteFileSize, remoteFilePath = self._getRemoteFileSize(user, password, localFilePath)

                        if str(remoteFileSize).isdigit():
                        # if isinstance(remoteFileSize, (int, long)):
                            if localFileSize < int(remoteFileSize):
                                logger.debug(' File incomplete. Deleting file "%s"' % localFilePath)

                                try:
                                    if os.path.isfile(localFilePath):
                                        os.remove(localFilePath)
                                    elif os.path.isdir(localFilePath):
                                        shutil.rmtree(localFilePath)
                                except OSError as e:
                                    logger.debug(' Could not remove, access-error on file or directory "' + localFilePath + '"! \n' + str(e))


                                self._downloadFile(user, password, localFilePath, remoteFilePath)

                            else:
                                logger.debug(' Local file size is greater or equal to remote file size: "%s"' % localFilePath)
                        else:
                            logger.debug(' File does not exist remotely: "%s"' % localFilePath)

                else:
                    logger.debug(' File does not exist locally: "%s"' % localFilePath)

        temp_stderr_file.close()


    def _downloadFile(self, username, password, localPath, remotePath):
        logger = logging.getLogger('MegaManager._downloadFile')
        logger.setLevel(self.logLevel)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, remotePath, localPath))
        logFile = open(LOGFILE_mega, 'a')

        os.chdir('%s' % MEGATOOLS_PATH)
        cmd = 'start /B megaget -u %s -p %s --path "%s" "%s"' % (username, password, localPath, remotePath)
        proc = subprocess.Popen(cmd, stdout=logFile, stderr=logFile)

        while not proc.poll():
            pass

        logFile.close()


    def _download(self, username, password):
        logger = logging.getLogger('MegaManager._download')
        logger.setLevel(self.logLevel)


        logger.debug(' MEGA downloading directory from account "%s" from "%s" to "%s"' % (username, REMOTE_ROOT, LOCAL_ROOT))
        logFile = open(LOGFILE_mega, 'a')

        # logFile_stdout = open(LOGFILE_stdout, 'a')
        temp_logFile_path = tempfile.gettempdir() + '\\%d.tmp' % randint(0,9999999999)
        temp_logFile_stderr = open(temp_logFile_path, 'a')


        os.chdir('%s' % MEGATOOLS_PATH)
        # cmd = ['megacopy', '--download', '-u', '%s' % username, '-p', '%s' % password, '--local', '"%s"' % localPath, '--remote', '"%s"' % remotePath]
        # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        # (out, err) = proc.communicate()

        # cmd = 'megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (username, password, LOCAL_ROOT, REMOTE_ROOT)

        cmd = 'start "" /B megacopy --download -u %s -p %s --local "%s" --remote "%s"' % (username, password, LOCAL_ROOT, REMOTE_ROOT)
        proc = subprocess.Popen(cmd, stdout=logFile, stderr=subprocess.PIPE, shell=True)
        logger.debug('%s - %s: %s \n' % (username, password, cmd))

        # out, err = proc.communicate()
        # proc.wait()
        while not proc.poll():
            err = proc.stderr.readline()

            # logFile_stderr = open(LOGFILE_stderr, 'a')

            if err == '':
                break
            logFile.write('%s - %s: %s' % (username, password, err))
            # logFile_stderr.close()

            temp_logFile_stderr.write('%s - %s: %s' % (username, password, err))
            # time.sleep(10)

        self._remove_incompleteFiles(temp_logFile_path)




        output = proc.communicate()[0]
        exitCode = proc.returncode

        # logFile_stderr.close()
        # logFile_stdout.close()
        temp_logFile_stderr.close()
        logFile.close()


    def _waitForFinished(self, timeout=99999, sleep=5):
        logger = logging.getLogger('MegaManager._waitForFinished')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Waiting for threads to finish.')

        startTime = time.time()
        megaFileFinished = False
        while len(self.threads) > 0:
            megaFileThreads_found = False

            if not time.time() - startTime > timeout:
                time.sleep(self._getSpeed())
                for thread in self.threads:
                    if not thread.isAlive():
                        self.threads.remove(thread)
                        logger.info(' Thread "%s" finished!' % thread.name)
                        logger.debug(' Threads left: %d' % len(self.threads))

                    if 'megaFile' in thread.name:
                        megaFileThreads_found = True

                if not megaFileThreads_found and not megaFileFinished:
                    logger.info(' MEGA_locations_ALL.txt file creation complete!')
                    megaFileFinished = True
            else:
                logger.debug(' Waiting for threads to complete TIMED OUT!')
                return


    def _getRemoteDirs(self):
        logger = logging.getLogger('MegaManager._getRemoteDirs')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Get remote directories.')

        os.chdir('%s' % MEGATOOLS_PATH)
        cmd = ['start', '/B', 'megals', '-u', 'user', '-p', 'pass', '"%s"' % REMOTE_ROOT]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        (out, err) = proc.communicate()

        dirs = out.split('\r\n')
        dirList = []
        for dir in dirs:
            dirName = re.sub('%s' % REMOTE_ROOT, '', dir)
            if not dirName == '':
                dirList.append(re.sub('/', '', dirName))

        return dirList


        # cmd = 'megaals -u %s -p %s %s' % (username, password, REMOTE_ROOT)
        # proc1 = os.system(cmd)


    def _getUserPass(self, item=None, file=None):
        logger = logging.getLogger('MegaManager._getUserPass')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Getting usernames and passwords.')

        foundUserPass = []
        if file==None:
            file = MEGA_locations

        with open(file, "r") as ins:
            for line in ins:
                dict = {}
                if len(re.findall('-', line)) > 0 and len(re.findall('@', line)) > 0:
                    username = re.sub('\\n','',re.sub(' - .*','',line))
                    password = re.sub('\\n','',re.sub('.* - ','',line))


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


    def _upload(self, user, password):
        logger = logging.getLogger('MegaManager._upload')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Starting uploading for %s - %s' % (user, password))

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)
        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'megals -ln -u %s -p %s "%s"' % (user, password, REMOTE_ROOT)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                remote_filePath = re.split(':\d{2} ', line)[1]
                # remote_filePath = ' '.join(line.split()[6:])
                remote_type = line.split()[2]
                # if remote_type == '1':
                dir_subPath = re.sub(REMOTE_ROOT, '', remote_filePath)
                local_dir = LOCAL_ROOT_adj + '/' + dir_subPath
                remote_dir = REMOTE_ROOT + '/' + dir_subPath
                if os.path.exists(local_dir):
                    self._upload_localDir(user, password, local_dir, remote_dir)


    def _upload_localDir(self, user, password, localDir, remoteDir):
        logger = logging.getLogger('MegaManager._upload_localDir')
        logger.setLevel(self.logLevel)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (user, password, localDir))
        logFile = open(LOGFILE_mega, 'a')

        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (user, password, localDir, remoteDir)
        # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        proc = subprocess.Popen(cmd, stdout=logFile, stderr=logFile)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        logFile.close()


    def _deleteRemoteFiles(self, username, password):
        logger = logging.getLogger('MegaManager._deleteRemoteFiles')
        logger.setLevel(self.logLevel)
        self._remove_remoteFilesThatDontExist(username, password)


    def _remove_remoteFilesThatDontExist(self, user, password):
        logger = logging.getLogger('MegaManager._remove_remoteFilesThatDontExist')
        logger.setLevel(self.logLevel)
        logger.debug(' Removing remote files that do not exist locally on %s - %s.' % (user, password))

        dirs_removed = []

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)
        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (user, password, REMOTE_ROOT)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                remote_filePath = re.split(':\d{2} ', line)[1]
                # remote_filePath = ' '.join(line.split()[6:])
                file_subPath = re.sub(REMOTE_ROOT, '', remote_filePath)
                local_filePath = LOCAL_ROOT_adj + file_subPath
                higherDirRemoved = False

                for removed_dir in dirs_removed:
                    if removed_dir in remote_filePath:
                        higherDirRemoved = True
                        break

                if not os.path.exists(local_filePath):
                    remote_type = line.split()[2]

                    if not higherDirRemoved:
                        if remote_type == '0':
                            self._remove_remoteFile(user, password, remote_filePath)
                        elif remote_type == '1':
                            dirs_removed.append(remote_filePath)
                            self._remove_remoteFile(user, password, remote_filePath)


    def _compressImageFiles(self, user, password):
        logger = logging.getLogger('MegaManager._compressImageFiles')
        logger.setLevel(self.logLevel)

        logger.debug(' Compressing image files.')
        extensions = ['.jpg', '.jpeg', '.png']

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)
        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (user, password, REMOTE_ROOT)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                # test = re.split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = os.path.splitext(re.split(':\d{2} ', line)[1])
                    if fileExt in extensions:
                        remote_filePath = re.split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = re.sub(REMOTE_ROOT, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = LOCAL_ROOT_adj + file_subPath

                            if (os.path.exists(local_filePath)) and (local_filePath not in self.compressedImageFiles) and (local_filePath not in self.unableToCompressImageFiles):
                                # timeout = 2
                                returnCode = self._compressImageFile(local_filePath)
                                if returnCode == 0:
                                    # startTime = time.time()
                                    compressPath_backup = local_filePath + '.compressimages-backup'
                                    # while time.time() - startTime < timeout:
                                    if os.path.exists(compressPath_backup):
                                        logger.debug(' File compressed successfully "%s"!' % local_filePath)
                                        os.remove(compressPath_backup)
                                        self.compressedFiles.append(local_filePath)
                                        self._dump_compressedFileLists()

                                    else:
                                        logger.debug(' File cannot be compressed any further "%s"!' % local_filePath)
                                        self.unableToCompressImageFiles.append(local_filePath)
                                        self._dump_unableToCompressImageFileList()

                                        # self._deleteCompressedBackup(local_filePath)
                                        # self._remove_remoteFile(user, password, remote_filePath)

                                else:
                                    logger.debug(' Error, image file could not be compressed "%s"!' % local_filePath)

                            else:
                                logger.debug(' Error, image file previously processed. Moving on.  "%s"!' % local_filePath)

            time.sleep(self._getSpeed())


    def _compressImageFile(self, filePath):
        logger = logging.getLogger('MegaManager._compressImageFile')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Compressing image file "%s".' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        os.chdir(WORKING_DIR)

        # proc1 = subprocess.call('python libs\\compressImages\\compressImages.py --h', creationflags=CREATE_NO_WINDOW)
        cmd = 'D:\\Python\\Python27\\python.exe "%s\\libs\\compressImages\\compressImages.py" --mode compress "%s"' % (WORKING_DIR, filePath)
        proc1 = subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)
        return proc1


    def _compressVideoFiles(self, user, password):
        logger = logging.getLogger('MegaManager._compressVideoFiles')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Finding video files to compress.')
        extensions = ['.avi', '.mp4', '.wmv']

        LOCAL_ROOT_adj = re.sub('\\\\', '/', LOCAL_ROOT)
        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'megals -lnR -u %s -p %s "%s"' % (user, password, REMOTE_ROOT)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        (out, err) = proc.communicate()
        lines = out.split('\r\n')
        for line in lines:
            if not line == '':
                # test = re.split(':\d{2} ', line)
                remote_type = line.split()[2]
                if remote_type == '0':
                    fileName, fileExt = os.path.splitext(re.split(':\d{2} ', line)[1])
                    if fileExt in extensions:
                        remote_filePath = re.split(':\d{2} ', line)[1]
                        # remote_filePath = ' '.join(line.split()[6:])
                        file_subPath = re.sub(REMOTE_ROOT, '', remote_filePath)

                        if file_subPath is not '':
                            local_filePath = LOCAL_ROOT_adj + file_subPath

                            if (os.path.exists(local_filePath)) and (local_filePath not in self.compressedVideoFiles) and (local_filePath not in self.unableToCompressVideoFiles):
                                # timeout = 2
                                returnCode, new_filePath = self._compressVideoFile(local_filePath)
                                if returnCode == 0:
                                    logger.debug(' File compressed successfully "%s" into "%s"!' % (local_filePath, new_filePath))
                                    self.compressedVideoFiles.append(new_filePath)
                                    self._dump_compressedVideoFileLists()

                                else:
                                    logger.debug(' Error, video file could not be compressed "%s"!' % local_filePath)

                            else:
                                logger.debug(' Error, video file previously processed. Moving on. "%s"!' % local_filePath)

            time.sleep(self._getSpeed())

    def _compressVideoFile(self, filePath):
        logger = logging.getLogger('MegaManager._compressVideoFile')
        logger.setLevel(self.logLevel)
        logger.debug(' Compressing video file: "%s"' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        os.chdir(WORKING_DIR)
        newFilePath = filePath.rsplit( ".", 1 )[ 0 ] + '_NEW.mp4'
        if os.path.exists(newFilePath):
            os.remove(newFilePath)

        cmd = '"%s\\libs\\compressVideos\\ffmpeg.exe" -i "%s" -vf "scale=\'if(gte(iw,720), 720, iw)\':-2" -preset medium -threads 1 "%s"' % (WORKING_DIR, filePath, newFilePath)

        # proc1 = subprocess.call(cmd)
        proc1 = subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)

        if os.path.exists(newFilePath) and proc1 == 0:
            os.remove(filePath)
        elif os.path.exists(newFilePath):
            os.remove(newFilePath)

        os.rename(newFilePath, re.sub('_NEW', '', newFilePath))

        return proc1, re.sub('_NEW', '', newFilePath)


    def _deleteCompressedBackup(self, filePath):
        logger = logging.getLogger('MegaManager._deleteCompressedBackup')
        logger.setLevel(self.logLevel)
        logger.debug(' Deleting compressed directory backup files "%s".' % filePath)

        CREATE_NO_WINDOW = 0x08000000
        proc1 = subprocess.call('python libs\\compressImages\\compressImages.py --mode detletebackup "%s"' % (filePath),  creationflags=CREATE_NO_WINDOW)
        return proc1


    def _remove_remoteFile(self, user, password, remote_filePath):
        logger = logging.getLogger('MegaManager._remove_remoteFile')
        logger.setLevel(self.logLevel)

        logger.debug(' %s - %s: Removing remote file "%s"!' % (user, password, remote_filePath))
        logFile = open(LOGFILE_mega, 'a')

        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'megarm -u %s -p %s "%s"' % (user, password, remote_filePath)
        proc = subprocess.Popen(cmd, stdout=logFile, stderr=logFile, shell=True)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')

        logFile.close()


    def _create_MEGA_locationsFile(self):
        logger = logging.getLogger('MegaManager._create_MEGA_locationsFile')
        logger.setLevel(self.logLevel)
        
        logger.debug(' Creating MEGA_locations_ALL.txt file.')

        foundUserPass = self._getUserPass(file=MEGA_ACCOUNTS)

        # shutil.copyfile(MEGA_locations_ALL_output, MEGA_locations_ALL_output + '.old')

        try:
            self.accounts_details_dict = {}
            with open(MEGA_locations_ALL_output, "w") as outs:
                for account in foundUserPass:
                    logger.debug(' Creating thread to gather details on account %s.' % account)

                    t_megaFile = threading.Thread(target=self._getAccountDetails, args=(account, ),
                                                 name='thread_megaFile_%s' % account['user'])
                    t_megaFile.start()
                    self.threads.append(t_megaFile)
                    time.sleep(self._getSpeed())


                # self._waitForFinished(threads, timeout=500, sleep=1)

                for accountDetails in sorted(self.accounts_details_dict):
                    for line in self.accounts_details_dict[accountDetails]:
                        outs.write(line)



            outs.close()

        except (Exception, KeyboardInterrupt)as e:
            logger.debug(' Exception: %s' % e)
            shutil.copyfile(MEGA_locations_ALL_output + '.old', MEGA_locations_ALL_output)

    def _getSpeed(self):
        logger = logging.getLogger('MegaManager._getSpeed')
        logger.setLevel(self.logLevel)
        return 0


    def _getAccountDetails(self, account):
        logger = logging.getLogger('MegaManager._getAccountDetails')
        logger.setLevel(self.logLevel)
        
        accountDetails = []
        accountDetails.append(account['user'] + ' - ' + account['pass'] + '\n')
        os.chdir('%s' % MEGATOOLS_PATH)

        cmd = 'start /B megadf --free -h -u %s -p %s' % (account['user'], account['pass'])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info(str(err))

        if not out == '':
            out = re.sub('\r', '', out)
            accountDetails.append('FREE SPACE: ' + out)

        cmd = 'start /B megadf --used -h -u %s -p %s' % (account['user'], account['pass'])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if err:
            logger.info()

        if not out == '':
            out = re.sub('\r', '', out)
            accountDetails.append('REMOTE SIZE: ' + out)

        REMOTE_ROOT + '/'
        cmd = 'start /B megals -n -u %s -p %s "%s"' % (account['user'], account['pass'], REMOTE_ROOT)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        directoryLines = []
        totalLocalSize = 0
        if err:
            logger.info()

        if not out == '':
            lines = out.split('\r\n')
            for line in lines:
                localDirSize = 0
                localDirPath = LOCAL_ROOT + '\\' + line
                remoteDirSize, remotePath = self._getRemoteDirSize(account['user'], account['pass'], localDirPath)

                if os.path.exists(localDirPath) and not line == '':
                    # localDirSize = os.path.getsize(localDirPath)
                    for r, d, f in os.walk(localDirPath):
                        for file in f:
                            filePath = os.path.join(r, file)
                            if os.path.exists(filePath):
                                localDirSize = localDirSize + os.path.getsize(filePath)

                    totalLocalSize = totalLocalSize + localDirSize
                    directoryLines.append(line + ' (%s remote, %s local)\n' % (size_format(int(remoteDirSize)), size_format(int(localDirSize))))

                elif not line == '':
                    directoryLines.append(line + ' (%s remote, NONE local)\n' % (size_format(int(remoteDirSize))))
                    # accountDetails.append('LOCAL SIZE: NONE \n')


        accountDetails.append('LOCAL SIZE: %s \n' % size_format(totalLocalSize))


        for line in directoryLines:
            accountDetails.append(line)
        accountDetails.append('\n')
        accountDetails.append('\n')

        self.accounts_details_dict[account['user']] = accountDetails



    def _tearDown(self):
        logger = logging.getLogger('MegaManager._tearDown')
        logger.setLevel(self.logLevel)
        
        logger.info('Tearing down megaManager!')

        try:
            self.compressedImageFiles
            self._dump_compressedImageFileList()
        except NameError:
            logger.debug("self.compressedImageFiles wasn't defined!")


        try:
            self.compressedVideoFiles
            self._dump_compressedVideoFileList()
        except NameError:
            logger.debug("self.compressedVideoFiles wasn't defined!")

        try:
            self.unableToCompressImageFiles
            self._dump_unableToCompressImageFileList()
        except NameError:
            print "self.unableToCompressImageFiles wasn't defined!"

        try:
            self.unableToCompressVideoFiles
            self._dump_unableToCompressVideoFileList()
        except NameError:
            print "self.unableToCompressVideoFiles wasn't defined!"

def size_format(b):
    if b < 1000:
        return '%i' % b + 'B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b/1000) + 'KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b/1000000) + 'MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b/1000000000) + 'GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b/1000000000000) + 'TB'


def size_of_dir(dirPath):
    """Walks through the directory, getting the cumulative size of the directory"""
    sum = 0
    for file in os.listdir(dirPath):
        sum += os.path.getsize(dirPath+'\\'+file)
    return sum
    # logger.info("Size of directory: ")
    # logger.info(sum, "bytes")
    # logger.info(sum/1000, "kilobytes")
    # logger.info(sum/1000000, "megabytes")
    # logger.info(sum/1000000000, "gigabytes")
    # logger.info("-"*80)
    # input("Press ENTER to view all files and sizes")


def getArgs():
    parser = argparse.ArgumentParser(description='Process some integers.')

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
    proc = psutil.Process(os.getpid())
    proc.nice(psutil.IDLE_PRIORITY_CLASS)  # Sets low priority

    kwargs = getArgs()

    megaObj = MegaManager(**kwargs)
    # returnCode = megaObj._compressVideoFile('I:\\Games\\1\\Done\\MEGA\\Jada Fire\\Screw My Wife Please!! 42.wmv')

    megaObj.run()


if __name__ == "__main__":
    main()


