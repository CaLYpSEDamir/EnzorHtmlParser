# coding: utf-8

from __future__ import unicode_literals

import sys


def sys_exit(msg):
    """
    Аварийный выход
    msg - str, message
    """
    sys.stdout.write(msg+'\n')
    sys.exit()
