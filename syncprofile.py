##
# Created by: Curtis Szmania
# Date: 7/2/2017
# Initial Creation.
# Sync Profile class. Used for sync profile data.
###

from account import Account
from logging import getLogger
from os import path
from pathMapping import PathMapping

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))

class SyncProfile(Account):
    def __init__(self, username, password, pathMappings, profileName=None, logLevel='DEBUG'):
        """
        Library for ffmpeg converter and encoder interaction.

        Args:
            username (str): MEGA account user name
            password (str): MEGA account password
            pathMappings (list): dictionary of local and remote path mappings.
            profileName (str): Unique profile name
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        Account.__init__(self, username=username, password=password, logLevel=logLevel)

        self.__profileName = profileName if profileName is not None else username
        self.__pathMappings = pathMappings
        self.__logLevel = logLevel

        self.__local_usedSpace = None
        self.__remote_usedSpace = None

        # self.__account = super(SyncProfile, self).__init__(self, username=username, password=password, logLevel=logLevel)
        # # self.__account = super(self.__class__, self)
        # pass
    #
    # @property
    # def account(self):
    #     """
    #     Getter for MEGA profile account.
    #
    #     Returns:
    #         Account: Returns MEGA profile account
    #     """
    #
    #     logger = getLogger('SyncProfile.account')
    #     logger.setLevel(self.__logLevel)
    #
    #     return self.__account
    #
    # @account.setter
    # def account(self, value):
    #     """
    #     Setter for MEGA profile account.
    #
    #     Args:
    #         value (str): value to set profile account to.
    #     """
    #
    #     logger = getLogger('SyncProfile.account')
    #     logger.setLevel(self.__logLevel)
    #
    #     self.__account = value

    @property
    def local_usedSpace(self):
        """
        Getter for MEGA profile local used space.

        Returns:
            String: Returns MEGA profile local used space
        """

        logger = getLogger('SyncProfile.local_usedSpace')
        logger.setLevel(self.__logLevel)

        return self.__local_usedSpace

    @local_usedSpace.setter
    def local_usedSpace(self, value):
        """
        Setter for MEGA profile local used space.

        Args:
            value (str): value to set profile local used space to.
        """

        logger = getLogger('SyncProfile.local_usedSpace')
        logger.setLevel(self.__logLevel)

        self.__local_usedSpace = value

    @property
    def pathMappings(self):
        """
        Getter for MEGA profile path mappings.

        Returns:
            Account: Returns MEGA profile path mappings list of PathMapping objects
        """

        logger = getLogger('SyncProfile.pathMappings')
        logger.setLevel(self.__logLevel)

        return self.__pathMappings

    @pathMappings.setter
    def pathMappings(self, value):
        """
        Setter for MEGA profile pathMappings.

        Args:
            value (list): list of PathMapping objects to set to.
        """

        logger = getLogger('SyncProfile.pathMappings')
        logger.setLevel(self.__logLevel)

        self.__pathMappings = value

    @property
    def profileName(self):
        """
        Getter for profile name.

        Returns:
            String: Returns profile name
        """

        logger = getLogger('SyncProfile.profileName')
        logger.setLevel(self.__logLevel)

        return self.__profileName

    @profileName.setter
    def profileName(self, value):
        """
        Setter for profile name.

        Args:
            value (str): value to set profile name to.
        """

        logger = getLogger('SyncProfile.profileName')
        logger.setLevel(self.__logLevel)

        self.__profileName = value

    @property
    def remote_usedSpace(self):
        """
        Getter for MEGA profile remote used space.

        Returns:
            String: Returns MEGA profile remote  used space
        """

        logger = getLogger('SyncProfile.remote_usedSpace')
        logger.setLevel(self.__logLevel)

        return self.__remote_usedSpace

    @remote_usedSpace.setter
    def remote_usedSpace(self, value):
        """
        Setter for MEGA profile remote used space.

        Args:
            value (str): value to set profile remote used space to.
        """

        logger = getLogger('SyncProfile.remote_usedSpace')
        logger.setLevel(self.__logLevel)

        self.__remote_usedSpace = value

    def add_path_mapping(self, localRoot, remoteRoot):
        """
        Add path mapping to profile path mappings list.

        Args:
            localRoot (str): Local root of pair.
            remoteRoot (str): Remote root of pair.
        """

        logger = getLogger('SyncProfile.add_path_mapping')
        logger.setLevel(self.__logLevel)

        logger.debug(' Adding path mapping to profile.')

        try:
            pathMapObj = PathMapping(localPath=localRoot, remotePath=remoteRoot)
            self.__pathMappings[self.get_path_mappings_count()] = pathMapObj
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
        logger.setLevel(self.__logLevel)

        logger.debug(' Returning path mapping at index %d.' % index)

        if index:
            if not index + 1 > len(self.__pathMappings):
                return self.__pathMappings[index]
            else:
                logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
                return None
        else:
            if len(self.__pathMappings) > 0:
                logger.debug(' No index given. Returning first item.')
                return self.__pathMappings[0].remotePath
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
        logger.setLevel(self.__logLevel)
        
        logger.debug(' Returning path mapping local root path.')
        
        if index:
            if not index + 1 > len(self.__pathMappings):
                return self.__pathMappings[index].localPath
            else:
                logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
                return None
        else:
            if len(self.__pathMappings) > 0:
                logger.debug(' No index given. Returning first item.')
                return self.__pathMappings[0].localPath
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
        logger.setLevel(self.__logLevel)

        logger.debug(' Returning path mapping remote root path.')

        if index:
            if not index + 1 > len(self.__pathMappings):
                return self.__pathMappings[index].remotePath
            else:
                logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
                return None
        else:
            if len(self.__pathMappings) > 0:
                logger.debug(' No index given. Returning first item.')
                return self.__pathMappings[0].remotePath
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
        logger.setLevel(self.__logLevel)

        return len(self.__pathMappings)

    def set_path_mapping_local_path(self, value, index=None):
        """
        Setter for profile local root path.

        Args:
            index (int): index of path mapping to set local root of.
            value (str): value to set local root to.
        """

        logger = getLogger('SyncProfile.set_path_mapping_local_path')
        logger.setLevel(self.__logLevel)

        logger.debug(' Setting path mapping local root path.')

        # if index:
        if not index + 1 > len(self.__pathMappings):
            self.__pathMappings[index].localPath = value
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
        logger.setLevel(self.__logLevel)

        logger.debug(' Setting path mapping remote root path.')

        if not index + 1 > len(self.__pathMappings):
            self.__pathMappings[index].remotePath = value
            return True
        else:
            logger.error(' Error, given index of "%d" is larger than path mappings list for profile.' % index)
            return False

    
                

