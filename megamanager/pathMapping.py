##
# Created by: Curtis Szmania
# Date: 7/2/2017
# Initial Creation.
# Path Mapping class. Used for path mappings.
###

from account import Account
from logging import getLogger
from os import path

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))

class PathMapping(Account):
    def __init__(self, localPath, remotePath, logLevel='DEBUG'):
        """
        Class used to keep track of local and remote path mappings. This correlates local locations with remote locations,
        for syncing purposes.

        Args:
            localPath (str): Local path of path mapping.
            remotePath (str): Remote path of path mapping.
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
        """


        self.__localPath = localPath
        self.__remotePath = remotePath
        self.__logLevel = logLevel

        self.__localPath_freeSpace = None
        self.__localPath_usedSpace = None
        self.__remotePath_usedSpace = None

    @property
    def localPath(self):
        """
        Getter for MEGA local path.

        Returns:
            String: Returns local path
        """

        logger = getLogger('SyncProfile.localPath')
        logger.setLevel(self.__logLevel)

        return self.__localPath

    @localPath.setter
    def localPath(self, value):
        """
        Setter for local path.

        Args:
            value (str): value to set local path to.
        """

        logger = getLogger('SyncProfile.localPath')
        logger.setLevel(self.__logLevel)

        self.__localPath = value

    @property
    def localPath_freeSpace(self):
        """
        Getter for MEGA local path free space.

        Returns:
            String: Returns local path free space
        """

        logger = getLogger('SyncProfile.localPath_freeSpace')
        logger.setLevel(self.__logLevel)

        return self.__localPath_freeSpace

    @localPath_freeSpace.setter
    def localPath_freeSpace(self, value):
        """
        Setter for local path free space.

        Args:
            value (str): value to set local path free space to.
        """

        logger = getLogger('SyncProfile.localPath_freeSpace')
        logger.setLevel(self.__logLevel)

        self.__localPath_freeSpace = value

    @property
    def localPath_usedSpace(self):
        """
        Getter for local path used space.

        Returns:
            String: Returns local path used space
        """

        logger = getLogger('SyncProfile.localRoot_usedSpace')
        logger.setLevel(self.__logLevel)

        return self.__localPath_usedSpace

    @localPath_usedSpace.setter
    def localPath_usedSpace(self, value):
        """
        Setter for local path used space.

        Args:
            value (str): value to set local path used space to.
        """

        logger = getLogger('SyncProfile.localPath_usedSpace')
        logger.setLevel(self.__logLevel)

        self.__localPath_usedSpace = value

    @property
    def remotePath(self):
        """
        Getter for remote path.

        Returns:
            String: Returns remote path
        """

        logger = getLogger('SyncProfile.remotePath')
        logger.setLevel(self.__logLevel)

        return self.__remotePath

    @remotePath.setter
    def remotePath(self, value):
        """
        Setter for remote path.

        Args:
            value (str): value to set remote path to.
        """

        logger = getLogger('SyncProfile.remotePath')
        logger.setLevel(self.__logLevel)

        self.__remotePath = value


    @property
    def remotePath_usedSpace(self):
        """
        Getter for remote path used space.

        Returns:
            String: Returns remote path used space
        """

        logger = getLogger('SyncProfile.remotePath_usedSpace')
        logger.setLevel(self.__logLevel)

        return self.__remotePath_usedSpace

    @remotePath_usedSpace.setter
    def remotePath_usedSpace(self, value):
        """
        Setter for remote path used space.

        Args:
            value (str): value to set remote path used space to.
        """

        logger = getLogger('SyncProfile.remotePath_usedSpace')
        logger.setLevel(self.__logLevel)

        self.__remotePath_usedSpace = value


