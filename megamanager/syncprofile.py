##
# Created by: Curtis Szmania
# Date: 7/2/2017
# Initial Creation.
# Sync Profile class. Used for sync profile data.
###

from account import Account
from logging import getLogger
from path_mapping import PathMapping

__author__ = 'szmania'


class SyncProfile(object):
    def __init__(self, username, password, path_mappings, profile_name=None, log_level='DEBUG'):
        """
        Library for ffmpeg converter and encoder interaction.

        Args:
            username (str): MEGA account user name
            password (str): MEGA account password
            path_mappings (list): dictionary of local and remote path mappings.
            profile_name (str): Unique profile name
            log_level (str): Logging level setting ie: "DEBUG" or "WARN"
        """


        self.__profile_name = profile_name if profile_name is not None else username
        self.__path_mappings = path_mappings
        self.__log_level = log_level
        self.__local_used_space = None
        self.__account = Account(username=username, password=password, log_level=log_level)

    @property
    def account(self):
        """
        Getter for MEGA profile account.

        Returns:
            Account: Returns MEGA profile account
        """
        logger = getLogger('SyncProfile.account')
        logger.setLevel(self.__log_level)
        return self.__account

    @account.setter
    def account(self, value):
        """
        Setter for MEGA profile account.

        Args:
            value (str): value to set profile account to.
        """
        logger = getLogger('SyncProfile.account')
        logger.setLevel(self.__log_level)
        self.__account = value

    @property
    def local_used_space(self):
        """
        Getter for MEGA profile local used space.

        Returns:
            String: Returns MEGA profile local used space
        """
        logger = getLogger('SyncProfile.local_used_space')
        logger.setLevel(self.__log_level)
        return self.__local_used_space

    @local_used_space.setter
    def local_used_space(self, value):
        """
        Setter for MEGA profile local used space.

        Args:
            value (str): value to set profile local used space to.
        """
        logger = getLogger('SyncProfile.local_used_space')
        logger.setLevel(self.__log_level)
        self.__local_used_space = value

    @property
    def path_mappings(self):
        """
        Getter for MEGA profile path mappings.

        Returns:
            Account: Returns MEGA profile path mappings list of PathMapping objects
        """
        logger = getLogger('SyncProfile.path_mappings')
        logger.setLevel(self.__log_level)
        return self.__path_mappings

    @path_mappings.setter
    def path_mappings(self, value):
        """
        Setter for MEGA profile path_mappings.

        Args:
            value (list): list of PathMapping objects to set to.
        """
        logger = getLogger('SyncProfile.path_mappings')
        logger.setLevel(self.__log_level)
        self.__path_mappings = value

    @property
    def profile_name(self):
        """
        Getter for profile name.

        Returns:
            String: Returns profile name
        """
        logger = getLogger('SyncProfile.profile_name')
        logger.setLevel(self.__log_level)
        return self.__profile_name

    @profile_name.setter
    def profile_name(self, value):
        """
        Setter for profile name.

        Args:
            value (str): value to set profile name to.
        """
        logger = getLogger('SyncProfile.profile_name')
        logger.setLevel(self.__log_level)
        self.__profile_name = value

    @property
    def remote_free_space(self):
        """
        Getter for MEGA profile remote free space.

        Returns:
            String: Returns MEGA profile remote free space
        """
        logger = getLogger('SyncProfile.remote_free_space')
        logger.setLevel(self.__log_level)
        return self.__account.freeSpace

    @property
    def remote_total_space(self):
        """
        Getter for MEGA profile remote total space.

        Returns:
            String: Returns MEGA profile remote total space
        """
        logger = getLogger('SyncProfile.remote_total_space')
        logger.setLevel(self.__log_level)
        return self.__account.totalSpace

    @property
    def remote_used_space(self):
        """
        Getter for MEGA profile remote used space.

        Returns:
            String: Returns MEGA profile remote  used space
        """
        logger = getLogger('SyncProfile.remote_used_space')
        logger.setLevel(self.__log_level)
        return self.__account.usedSpace

    def add_path_mapping(self, localRoot, remoteRoot):
        """
        Add path mapping to profile path mappings list.

        Args:
            localRoot (str): Local root of pair.
            remoteRoot (str): Remote root of pair.
        """
        logger = getLogger('SyncProfile.add_path_mapping')
        logger.setLevel(self.__log_level)
        logger.debug(' Adding path mapping to profile.')
        try:
            pathMapObj = PathMapping(local_path=localRoot, remote_path=remoteRoot)
            self.__path_mappings[self.get_path_mappings_count()] = pathMapObj
            return True

        except Exception as e:
            logger.error(' Exception: %s' % str(e))
            return False

    def get_path_mapping(self, index=None):
        """
        Getter for profile path mapping at given index.

        Args:
            index (int): index of path mapping to get.

        Returns:
            PathMapping: Returns PathMapping object.
        """
        logger = getLogger('SyncProfile.get_path_mapping')
        logger.setLevel(self.__log_level)
        logger.debug(' Returning path mapping at index %d.' % index)
        if index:
            if not index + 1 > len(self.__path_mappings):
                return self.__path_mappings[index]
            else:
                logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
                return None
        else:
            if len(self.__path_mappings) > 0:
                logger.debug(' No index given. Returning first item.')
                return self.__path_mappings[0]
            else:
                logger.error(' Error, no path mapping exist for this profile!')
                return None

    def get_path_mapping_local_path(self, index=None):
        """
        Getter for profile local root path.

        Args:
            index (int): index of path mapping to get local root of.

        Returns:
            String: Returns local root path.
        """
        logger = getLogger('SyncProfile.get_path_mapping_local_path')
        logger.setLevel(self.__log_level)
        logger.debug(' Returning path mapping local root path.')
        if index:
            if not index + 1 > len(self.__path_mappings):
                return self.__path_mappings[index].local_path
            else:
                logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
                return None
        else:
            if len(self.__path_mappings) > 0:
                logger.debug(' No index given. Returning first item.')
                return self.__path_mappings[0].local_path
            else:
                logger.error(' Error, no path mappings exist for this profile!')
                return None

    def get_path_mapping_remote_path(self, index=None):
        """
        Getter for profile remote root path.

        Args:
            index (int): index of path mapping to get remote root of.

        Returns:
            String: Returns remote root path.
        """
        logger = getLogger('SyncProfile.get_path_mapping_remote_path')
        logger.setLevel(self.__log_level)
        logger.debug(' Returning path mapping remote root path.')
        if index:
            if not index + 1 > len(self.__path_mappings):
                return self.__path_mappings[index].remote_path
            else:
                logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
                return None
        else:
            if len(self.__path_mappings) > 0:
                logger.debug(' No index given. Returning first item.')
                return self.__path_mappings[0].remote_path
            else:
                logger.error(' Error, no path mappings exist for this profile!')
                return None

    def get_path_mappings_count(self):
        """
        Return path mappings list size.

        Returns:
            integer: size of path mappings list.
        """
        logger = getLogger('SyncProfile.get_path_mappings_count')
        logger.setLevel(self.__log_level)
        return len(self.__path_mappings)

    def set_path_mapping_local_path(self, value, index=None):
        """
        Setter for profile local root path.

        Args:
            index (int): index of path mapping to set local root of.
            value (str): value to set local root to.
        """
        logger = getLogger('SyncProfile.set_path_mapping_local_path')
        logger.setLevel(self.__log_level)
        logger.debug(' Setting path mapping local root path.')
        if not index + 1 > len(self.__path_mappings):
            self.__path_mappings[index].local_path = value
            return True
        else:
            logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
            return False

    def set_path_mapping_remote_root(self, index, value):
        """
        Setter for profile remote root path.

        Args:
            index (int): index of path mapping to set remote root of.
            value (str): value to set remote root to.
        """
        logger = getLogger('SyncProfile.set_path_mapping_remote_root')
        logger.setLevel(self.__log_level)
        logger.debug(' Setting path mapping remote root path.')
        if not index + 1 > len(self.__path_mappings):
            self.__path_mappings[index].remote_path = value
            return True
        else:
            logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
            return False

