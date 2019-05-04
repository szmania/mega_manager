##
# Created by: Curtis Szmania
# Date: 7/2/2017
# Initial Creation.
# Path Mapping class. Used for path mappings.
###

from account import Account
from logging import getLogger

__author__ = 'szmania'


class PathMapping(Account):
    def __init__(self, local_path, remote_path, log_level='DEBUG'):
        """
        Class used to keep track of local and remote path mappings. This correlates local locations with remote locations,
        for syncing purposes.

        Args:
            local_path (str): Local path of path mapping.
            remote_path (str): Remote path of path mapping.
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
        """


        self.__local_path = local_path
        self.__remote_path = remote_path
        self.__log_level = log_level

        self.__local_path_free_space = None
        self.__local_path_used_space = None
        self.__remote_path_used_space = None

    @property
    def local_path(self):
        """
        Getter for MEGA local path.

        Returns:
            String: Returns local path
        """

        logger = getLogger('SyncProfile.local_path')
        logger.setLevel(self.__log_level)

        return self.__local_path

    @local_path.setter
    def local_path(self, value):
        """
        Setter for local path.

        Args:
            value (str): value to set local path to.
        """

        logger = getLogger('SyncProfile.local_path')
        logger.setLevel(self.__log_level)

        self.__local_path = value

    @property
    def local_path_free_space(self):
        """
        Getter for MEGA local path free space.

        Returns:
            String: Returns local path free space
        """

        logger = getLogger('SyncProfile.local_path_free_space')
        logger.setLevel(self.__log_level)

        return self.__local_path_free_space

    @local_path_free_space.setter
    def local_path_free_space(self, value):
        """
        Setter for local path free space.

        Args:
            value (str): value to set local path free space to.
        """

        logger = getLogger('SyncProfile.local_path_free_space')
        logger.setLevel(self.__log_level)

        self.__local_path_free_space = value

    @property
    def local_path_used_space(self):
        """
        Getter for local path used space.

        Returns:
            String: Returns local path used space
        """

        logger = getLogger('SyncProfile.localRoot_usedSpace')
        logger.setLevel(self.__log_level)

        return self.__local_path_used_space

    @local_path_used_space.setter
    def local_path_used_space(self, value):
        """
        Setter for local path used space.

        Args:
            value (str): value to set local path used space to.
        """

        logger = getLogger('SyncProfile.local_path_used_space')
        logger.setLevel(self.__log_level)

        self.__local_path_used_space = value

    @property
    def remote_path(self):
        """
        Getter for remote path.

        Returns:
            String: Returns remote path
        """

        logger = getLogger('SyncProfile.remote_path')
        logger.setLevel(self.__log_level)

        return self.__remote_path

    @remote_path.setter
    def remote_path(self, value):
        """
        Setter for remote path.

        Args:
            value (str): value to set remote path to.
        """

        logger = getLogger('SyncProfile.remote_path')
        logger.setLevel(self.__log_level)

        self.__remote_path = value


    @property
    def remote_path_used_space(self):
        """
        Getter for remote path used space.

        Returns:
            String: Returns remote path used space
        """

        logger = getLogger('SyncProfile.remote_path_used_space')
        logger.setLevel(self.__log_level)

        return self.__remote_path_used_space

    @remote_path_used_space.setter
    def remote_path_used_space(self, value):
        """
        Setter for remote path used space.

        Args:
            value (str): value to set remote path used space to.
        """

        logger = getLogger('SyncProfile.remote_path_used_space')
        logger.setLevel(self.__log_level)

        self.__remote_path_used_space = value


