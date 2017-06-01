##
# Created by: Curtis Szmania
# Date: 5/31/2017
# Initial Creation.
###

from logging import DEBUG, getLogger, FileHandler, Formatter, StreamHandler
from os import chdir, getpid, kill, listdir, path, remove, rename, walk
from re import findall, split, sub
from signal import SIGTERM
from subprocess import call, PIPE, Popen

MEGATOOLS_LOG = 'megaTools.log'

__author__ = 'szmania'

WORKING_DIR = path.realpath(__file__)

class MegaTools_Lib(object):
    def __init__(self, megaToolsPath, logLevel='DEBUG'):
        """
        :param megaToolsPath: Path to megaTools directory which includes megaget.exe, megals.exe, mega.copy.
        :type username: string
        :param logLevel: Logging level setting ie: "DEBUG" or "WARN"
        :type logLevel: String.
        """
        self.megaToolsPath = megaToolsPath
        self.logLevel = logLevel

    
    def download_file(self, username, password, localFilePath, remoteFilePath):
        """
        Download a remote file from MEGA account.

        :param username: username of account to download file from
        :type username: string
        :param password: password of account to download file from
        :type password: string
        :param localFilePath: Location to download file to.
        :type localFilePath: String.
        :param remoteFilePath: Location to download file from.
        :type remoteFilePath: String.

        :return :
        """

        logger = getLogger('MegaManager._download_file')
        logger.setLevel(self.logLevel)

        logger.debug(' MEGA downloading file from account "%s" - "%s" to "%s"' % (username, password, localFilePath))
        logFile = open(MEGATOOLS_LOG, 'a')

        chdir('%s' % self.megaToolsPath)
        cmd = 'start /B megaget -u %s -p %s --path "%s" "%s"' % (username, password, localFilePath, remoteFilePath)
        # proc = Popen(cmd)
        proc = Popen(cmd, stdout=logFile, stderr=logFile)

        while not proc.poll():
            pass

        logFile.close()

    def upload_local_dir(self, username, password, localDir, remoteDir, upSpeedLimit=None):
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
        :param upSpeedLimit: Upload speed limit in kilobytes.
        :type upSpeedLimit: int

        :return:
        :type:
        """

        logger = getLogger('MegaTools_Lib.upload_local_dir')
        logger.setLevel(self.logLevel)

        logger.debug('%s - %s: Uploading files in directory "%s"' % (username, password, localDir))
        logFile = open(MEGATOOLS_LOG, 'a')

        chdir('%s' % self.megaToolsPath)
        if upSpeedLimit:
            cmd = 'megacopy -u %s -p %s --limit-speed %d --local "%s" --remote "%s"' % (username, password, upSpeedLimit, localDir, remoteDir)
        else:
            cmd = 'megacopy -u %s -p %s --local "%s" --remote "%s"' % (username, password, localDir, remoteDir)

        proc = Popen(cmd, stdout=logFile, stderr=logFile, shell=True)
        # proc = Popen(cmd)
        # proc = Popen(cmd, stdout=logFile, stderr=logFile)

        (out, err) = proc.communicate()
        # lines = out.split('\r\n')
        logFile.close()
