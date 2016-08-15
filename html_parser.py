# coding: utf-8

from __future__ import unicode_literals, division

import sys
import os
import re
import requests
import operator
import numpy as np
import codecs

from urlparse import urlparse
from io import StringIO
from lxml import etree
from pandas import DataFrame


from validators import ArgsValidator
from config import (
    EXCLUDE_TAGS, P_TAG, A_TAG, EDGE_COEF, MIN_TEXT_LEN, MAIN_HEADERS,
    HEADERS, CONTENT_TAGS, ARTICLES_PATH
)
from helpers import sys_exit


class PTRNS(object):
    """
    Паттерны для работы со строками
    """
    # избавление от пустоты(\n\t\r\f\v)
    text_ptrn = re.compile(r'\s+$')
    # избавление от тэгов
    tag_ptrn = re.compile(r'|'.join(EXCLUDE_TAGS))
    # деление текста для записи
    split_ptrn = re.compile(r'.{,80}[ .!?>»:”…]+')
    # dotted
    dot_ptrn = re.compile(r'.+[.!?>»:”…]$')


class ContentTree(object):
    """
    Парсер сайта
    """
    def __init__(self, url):
        """
        url - str, адрес
        tree - контент сайта в виде дерева
        data - list, отфильтрованный контент
        """
        self.url = url
        self.tree = None
        self.data = None

    def build_tree(self):
        """
        Строим дерево
        """
        resp = requests.get(self.url, verify=False)
        parser_ = etree.HTMLParser()
        self.tree = etree.parse(StringIO(resp.text), parser_)

    def get_tree_content(self):
        """
        Фильтрация дерева, исключение ненужного
        """
        tree = self.tree
        data = []

        if tree is None:
            raise Exception("Build tree firstly!")

        body = tree.getroot().find('body')
        iter_ = body.getiterator()

        for ind, el in enumerate(iter_):
            if re.match(PTRNS.tag_ptrn, str(el.tag)) is None:

                text = el.text or ''

                if el.tag in CONTENT_TAGS + HEADERS:
                    text = self.get_full_text(el)

                data.append(
                    (ind, el.tag, len(text),
                     re.match(PTRNS.dot_ptrn, text) is not None,
                     text or ''))
        self.data = data

    def get_full_text(self, element):
        """
        Текст элемента дерева с текстами всех его детей
        """
        full_text = self.clear(element.text or '')

        chs = element.getchildren()
        for ch in chs:
            full_text += ' '+self.get_full_text(ch)

        full_text += self.clear(self.get_tail(element))

        # Избавляемся от дублей, текст перекинули главному элементу,
        # у дочерних все обнуляем
        element.text = element.tail = None

        return full_text

    def get_tail(self, element):
        """
        Текст, расположенный после элемента дерева
        """
        if element.tag == A_TAG:
            return "[{0}] {1}".format(element.get("href"), element.tail or '')

        return element.tail or ''

    @staticmethod
    def clear(text):
        """
        Избавление от пустоты
        """
        return text.strip('\t\n\r\f\v ')


class FileBuilder(object):
    """
    Писарь
    """
    def __init__(self, url):
        """
        """
        self.url = url

    def get_directory(self):
        """
        Директория для файла
        """
        pars = urlparse(self.url)
        host = pars.hostname
        path = pars.path.strip('/').split('/')

        filename = path[-1].split('.')[0] + '.txt'
        path = filter(None, [ARTICLES_PATH, host, ] + path[:-1])

        return os.path.join(*path), filename

    def write_content(self, data):
        """
        Пишем в файл!
        data - list of str, список текстов, который надо записать
        """
        direcoty, filename = self.get_directory()
        if not os.path.exists(direcoty):
            os.makedirs(direcoty)

        with codecs.open(os.path.join(direcoty, filename), 'w', 'utf-8') as f:
            for text in data:
                if re.match(PTRNS.dot_ptrn, text) is None:
                    text += '.'
                f.write('\n'.join(re.findall(PTRNS.split_ptrn, text)) + '\n\n')


class DataMiner(object):
    """
    Добыватель данных с сайтов
    """
    def __init__(self, url):
        """
        tree_builder - отвечает за дерево
        file_builder - отвечает за файл
        """
        self.tree_builder = ContentTree(url)
        self.file_builder = FileBuilder(url)

    def prepare(self):
        """
        Строим дерево, фильтруем данные
        """
        t_builder = self.tree_builder
        t_builder.build_tree()
        t_builder.get_tree_content()

    def mine(self, method=None):
        """
        Фабрика методов
        """
        if method is None:
            return self.mine_by_df()
        else:
            sys_exit("Unknown mining method {0}!".format(method))

    def mine_by_df(self):
        """
        Добыча с помощью DataFrame
        """
        df = DataFrame(self.tree_builder.data,
                       columns=['ind', 'tag', 'len', 'dot', 'text', ])

        head = self.get_headers_df(df)

        # заголовка нет
        if head is None:
            pass
            # ищем медиану, она же центр статьи
            # если статья имеет единственный вес, то медиана правильна

        else:

            main_tag_df = df[
                (df.tag.isin([P_TAG])) &
                (df['dot']) &
                (df.len > MIN_TEXT_LEN)
            ]

            if not main_tag_df.empty:
                edge = self.get_edge(main_tag_df.ind.tolist())
                edged_df = df[(df.ind >= head) & (df.ind <= edge)]

                article = edged_df[
                    (df.tag.isin(HEADERS)) |
                    ((df.tag.isin(CONTENT_TAGS)) & (df['dot']) & (df.len > 0))
                ]
                return article['text'].values
            else:
                print "OOUCH!!! S**T HAPPENS"

    @staticmethod
    def get_edge(indexes):
        """
        Из списка индексов возвращаем индекс, являющийся концом статьи
        """
        IND = 50

        l = len(indexes)

        if l < 3:
            f = indexes[0]
            s = indexes[1]
            indexes.append(f+IND)
            return f if s-f >= IND else s

        ranges = [indexes[i+1] - indexes[i] for i in xrange(l-1)]

        for i, r in enumerate(ranges[1:]):

            if r/np.mean(ranges[:i+1]) > EDGE_COEF:
                return indexes[i+1]

        return indexes[-1]

    def get_headers_df(self, df):
        """
        Индекс заголовка из DataFrame df
        """
        for h_tag in MAIN_HEADERS:
            h_df = df[df.tag == h_tag]
            if not h_df.empty:
                head = h_df.iloc[0]['ind']
                return head
        return None

    def output(self, data):
        """
        Запись
        """
        self.file_builder.write_content(data)


if __name__ == '__main__':

    url_ = ArgsValidator.validate(sys.argv)

    miner = DataMiner(url_)
    miner.prepare()
    data = miner.mine()
    miner.output(data)
