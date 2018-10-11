# -*- coding: UTF-8 -*-
from colorama import Fore, Back, Style

print(Fore.GREEN + '--' * 100)
import re
import os
from pprint import pprint
import time
import string


class Fileconvert(object):
    def __init__(self, path):
        self.path = path
        os.chdir(self.path)

    def spl(self, text):
        if '\t' in text:
            result = text.strip('\n').split('\t')
        else:
            result = [text.strip('\n')]
        return result

    # 小型文件tsv转二维列表
    def tsv2list(self, filename, skipline=1):
        os.chdir(self.path)
        with open("%s" % filename, 'r', encoding='utf-8') as f:
            if skipline <= 0:
                pass
            else:
                for i in range(skipline):
                    f.readline()
            finallist = [self.spl(i) for i in f]
            f.close()
        return finallist

    # 二维列表转tsv输出
    def list2tsv(self, path, inputlist, filename, fileformat='tsv'):
        finallist = '\n'.join(['\t'.join(i) for i in inputlist])
        os.chdir(path)
        with open('%s-merged.%s' % (filename, fileformat), 'w', encoding='utf-8') as f:
            f.write(finallist)
            f.close()

    def splfilename(self, filename):
        fileformat = filename.split('.')[-1]
        length = len(filename) - len(fileformat) - 1
        name = filename[:length]
        return [name, fileformat]

    # 替换字符串中的‘\n’等
    def sub_spacer(self, spacer, new, text):
        if text:
            if spacer in text:
                return text.replace(spacer, new)
            else:
                return text
        else:
            return ''

    def get_title_dict(self, text):
        line = text.strip().split('\t')
        return {x: line.index(x) for x in line}

    def write_tsvline(self, inputlist):
        return '\t'.join(inputlist) + '\n'

    def del_NAN(self, text):
        if text.upper() == 'NAN':
            return ''
        else:
            return text

    def tsvline(self, inputlist):
        plus = [del_NAN(x) for x in inputlist]
        return '\t'.join(plus) + '\n'

    def rev_split(self, text, spacer, num=None):
        return text[::-1].split(spacer, num)[-1][::-1]


def del_NAN(text):
    if text.upper() == 'NAN':
        return ''
    else:
        return text


def tsvline(inputlist):
    plus = [del_NAN(x) for x in inputlist]
    return '\t'.join(plus) + '\n'


def rev_split(text, spacer, num=-1):
    return text[::-1].split(spacer, num)[0][::-1]


def filter_null(somelist):
    """
    过滤掉列表中的空元素
    :param somelist: 输入列表
    :return: 返回列表
    """
    return list(filter(lambda x: x, somelist))


# html字符替换
def html_character():
    html_dict = {'&nbsp;': ' ', '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"', '&apos;': '\'', '&cent;': '￠',
                 '&pound;': '£', '&yen;': '¥', '&euro;': '€', '&sect;': '§', '&copy;': '©', '&reg;': '®',
                 '&trade;': '™', '&times;': '×', '&divide;': '÷'}
    return html_dict


# 清除制表符等特殊字符
def clear_spacer(text, sep=' '):
    """
    清除文本中的特殊制表符
    """
    _text = text.replace('\xa0', ' ')

    html_dict = html_character()
    # 先替换html转有特殊字符
    for x, y in html_dict.items():
        _ = _text.split(x)
        if len(_) >= 2:
            _text = y.join(_)

    # 若存在制表符，则进行过滤， 由于多个制表符常在一起，按一个分割后每个元素strip即可
    _text = ' '.join(filter_null(_text.split()))
    """
    spacer = ''
    existance = False

    spacers = ['\n', '  ', '\t\t', '\r\r', '\n\n', '\xa0']

    for x in spacers:
        if x in _text:
            existance = True
            spacer = x

    if existance:
        pieces = filter(lambda x: x, [x.strip() for x in _text.split(spacer)])
        return sep.join(pieces)
    """

    return _text


def clear_Spacer_inList(somelist):
    """
    一维列表每个字符串清除制表符
    :param somelist:
    :return:
    """
    return [clear_spacer(x) for x in somelist]
