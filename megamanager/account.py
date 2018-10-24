##
# Created by: Curtis Szmania
# Date: 7/2/2017
# Initial Creation.
# MEGA account class. Used for MEGA account details.
###

from logging import getLogger
from libs.lib import Lib
from os import path

__author__ = 'szmania'

SCRIPT_DIR = path.dirname(path.realpath(__file__))

class Account(object):
    def __init__(self, username, password, logLevel='DEBUG'):
        """
        Library for ffmpeg converter and encoder interaction.

        Args:
            username (str): MEGA account user name
            password (str): MEGA account password
            logLevel (str): Logging level setting ie: "DEBUG" or "WARN"
        """

        self.__username = username
        self.__password = password
        self.__log_level = logLevel
        
        self.__freeSpace = None
        self.__totalSpace = None
        self.__usedSpace = None

        self.__lib = Lib(logLevel=logLevel)

    @property
    def freeSpace(self):
        """
        Getter for MEGA account free space.

        Returns:
            String: Returns MEGA account free space
        """

        logger = getLogger('Account.freeSpace')
        logger.setLevel(self.__log_level)

        return self.__freeSpace

    @freeSpace.setter
    def freeSpace(self, value):
        """
        Setter for MEGA account free space.

        Args:
            value (str): value to set account free space to.
        """

        logger = getLogger('Account.freeSpace')
        logger.setLevel(self.__log_level)

        self.__freeSpace = value

    @property
    def totalSpace(self):
        """
        Getter for MEGA account total space.

        Returns:
            String: Returns MEGA account total space
        """

        logger = getLogger('Account.totalSpace')
        logger.setLevel(self.__log_level)

        return self.__totalSpace

    @totalSpace.setter
    def totalSpace(self, value):
        """
        Setter for MEGA account free space.

        Args:
            value (str): value to set account total space to.
        """

        logger = getLogger('Account.totalSpace')
        logger.setLevel(self.__log_level)

        self.__totalSpace = value


    @property
    def usedSpace(self):
        """
        Getter for MEGA account used space.

        Returns:
            String: Returns MEGA account used space
        """

        logger = getLogger('Account.usedSpace')
        logger.setLevel(self.__log_level)

        return self.__usedSpace

    @usedSpace.setter
    def usedSpace(self, value):
        """
        Setter for MEGA account used space.

        Args:
            value (str): value to set account used space to.
        """

        logger = getLogger('Account.usedSpace')
        logger.setLevel(self.__log_level)

        self.__usedSpace = value

    @property
    def password(self):
        """
        Getter for MEGA account password.

        Returns:
            String: Returns MEGA account password
        """

        logger = getLogger('Account.password')
        logger.setLevel(self.__log_level)

        return self.__password

    @password.setter
    def password(self, value):
        """
        Setter for MEGA account password.

        Args:
            value (str): value to set password to.
        """

        logger = getLogger('Account.password')
        logger.setLevel(self.__log_level)

        self.__password = value

    @property
    def username(self):
        """
        Getter for MEGA account username.

        Returns:
            String: Returns MEGA account username
        """

        logger = getLogger('Account.username')
        logger.setLevel(self.__log_level)

        return self.__username

    @username.setter
    def username(self, value):
        """
        Setter for MEGA account username.

        Args:
            value (str): value to set username to.
        """

        logger = getLogger('Account.username')
        logger.setLevel(self.__log_level)

        self.__username = value

