# coding: utf-8

from __future__ import unicode_literals


ALLOW_PROTOCOLS = ["http", "https", ]


# список ненеужных тэгов
# данный момент используются в регул выражениях
EXCLUDE_TAGS = ["<cyfunction", "script", "noscript", "style"]


P_TAG = "p"
S_TAG = "span"
A_TAG = "a"


EDGE_COEF = 10


MIN_TEXT_LEN = 50


MAIN_HEADERS = ["h1", "h2", ]
PURE_HEADERS = ["h3", "h4", "h5", "h6", "h7", ]
HEADERS = MAIN_HEADERS + PURE_HEADERS

CONTENT_TAGS = [P_TAG, S_TAG, ]


ARTICLES_PATH = ''
