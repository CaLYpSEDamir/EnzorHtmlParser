# coding: utf-8

from __future__ import unicode_literals

import socket
from urlparse import urlparse

from helpers import sys_exit
from config import ALLOW_PROTOCOLS


class UrlValidator(object):
    """
    """
    DEFAULT_PORT = 80

    def __init__(self, url):
        self.connector = urlparse(url)

    def validate(self):
        """
        """
        connector = self.connector
        if connector.hostname is None:
            sys_exit("ERROR: INVALID URL! SET PROTOCOL AND HOSTNAME")

        if connector.scheme not in ALLOW_PROTOCOLS:
            sys_exit("ERROR: PROTOCOL IS NOT SUPPORTED!")

        self.tcp_connect()

    def tcp_connect(self):
        """
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
        except socket.error as err:
            sys_exit('Failed to create socket! Error: {0}'.format(err.message))

        connector = self.connector
        try:
            ip = socket.gethostbyname(connector.hostname)
        except socket.gaierror:
            sys_exit('Hostname could not be resolved!')

        try:
            s.connect((ip, connector.port or self.DEFAULT_PORT))
        except socket.error as err:
            sys_exit('Failed to create socket! Error: {0}'.format(err.message))


class ArgsValidator(object):
    """
    Валидатор входных параметров
    """
    @classmethod
    def validate(cls, args):
        """

        """
        if len(args) == 1:
            sys_exit('Please enter site url as second argument!')

        url = args[1]

        url_checker = UrlValidator(url=url)
        url_checker.validate()

        return url
