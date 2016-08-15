# coding: utf-8

from __future__ import unicode_literals

# разрешенные протоколы
ALLOW_PROTOCOLS = ["http", "https", ]


# список ненеужных тэгов
EXCLUDE_TAGS = ["<cyfunction", "script", "noscript", "style"]

# тэги
P_TAG = "p"
S_TAG = "span"
A_TAG = "a"

MAIN_HEADERS = ["h1", "h2", ]
PURE_HEADERS = ["h3", "h4", "h5", "h6", "h7", ]
HEADERS = MAIN_HEADERS + PURE_HEADERS

CONTENT_TAGS = [P_TAG, S_TAG, ]

# название папки для результатов
ARTICLES_PATH = ''

# коэффициент участвует в определениии конца статьи!
# если разность порядкового номера с предыдущим в EDGE_COEF раз больше,
# чем средняя разность, то скорее всего это уже не часть статьи
EDGE_COEF = 10

# длина минимального текста
MIN_TEXT_LEN = 50
