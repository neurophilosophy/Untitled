# -*- coding: UTF-8 -*-
from colorama import Fore, Back, Style
print(Fore.GREEN + '--' * 100)
import os


class Fileconvert(object):
    def __init__(self, path):
        self.path = path
        os.chdir(self.path)

    def spl(self, text):
        # 分割由tab或者换行隔开的字符串
        if '\t' in text:
            result = text.strip('\n').split('\t')
        else:
            result = [text.strip('\n')]
        return result

    # 小型文件tsv转二维列表
    def tsv2list(self, filename, skipline=1, mode='r'):
        os.chdir(self.path)
        with open("%s" % filename, mode=mode, encoding='utf-8') as f:
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

    def splfilename(self, filename, sep='.'):
        # 分割文件名，返回（文件名，扩展名）
        fileformat = filename.split(sep)[-1]
        length = len(filename) - len(fileformat) - 1
        name = filename[:length]
        return (name, fileformat)

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
        if type(text) == str:
            line = text.strip().split('\t')
        else:
            line = text
        return {x: line.index(x) for x in line}


    def del_NAN(self, text):
        #去除NaN，替换为空字符
        if text.upper() == 'NAN':
            return ''
        else:
            return text

    def tsvline(self, inputlist):
        """
        输入列表或者元组，输出按tsv格式来并能写入文件的字符串
        :param inputlist:列表或者元组
        :return:按tsv格式来并能写入文件的字符串
        """
        plus = [del_NAN(x) for x in inputlist]
        return '\t'.join(plus) + '\n'

    def rev_split(self, text, spacer, num=None):
        return text[::-1].split(spacer=spacer, num=num)[-1][::-1]

    def appendToDict(self, key, value, dic):
        # 默认不需要去重，且对增加顺序有要求
        try:
            dic[key].append(value)
        except KeyError:
            dic[key] = [value]

    def addToDict(self, key, value, dic):
        # 每个键对应的一系列值的元素有重复 但是无顺序要求
        try:
            dic[key].add(value)
        except KeyError:
            dic[key] = {value}

    def fastTsv2dict_multi_values(self, inputlist, key_num, value_num, valueType=list):
        """
        输出字典的key和value在二维列表中的来源分别通过输入的key_num和value_num来指定，汇集键对应的所有值，不是one-to-one mapping
        :param inputlist: 二维列表
        :param key_num: 键值的index，可以是数字构成的元组
        :param value_num: 键值的index，可以是数字构成的元组，列表
        :param valueType: 确定最终字典的值是列表亦或是集合，若已确定为一一映射，则可以选择fastSelectTsv函数
        :return: 字典
        """
        dic = {}
        if valueType == list:
            func = self.appendToDict
        else:
            func = self.addToDict
        for x in inputlist:
            func(key=self.select_iter(loci=key_num, iter=x), value=self.select_iter(loci=value_num, iter=x), dic=dic)
        return dic

    def fastSelectTsv(self, filename, *kwag):
        """
        按照输入参数的要求，截取tsv文件中的每一列按照输入参数的类型输出
        :param filename: tsv文件全名
        :param kwag: 由代表index的数字构成，可以是字典元组或列表
        :return: 按kwag的类型输出
        """
        tsv = self.tsv2list(filename=filename)
        if type(*kwag) == dict:
            result = {}
            for x in tsv:
                result.update(select_iter(*kwag, x))
            return result
        else:
            return type(*kwag)(select_iter(*kwag, x) for x in tsv)

    def simple_select_iter(self,loci_list, iter):
        return type(loci_list)(iter[x] for x in loci_list)

    def select_iter(self, loci, iter):
        """
        按照输入的loci截取列表或者元组中的数据，并按loci的类型输出
        :param loci: 由代表index的数字构成，可以是字典元组或列表
        :param iter: 一维列表或者元组
        :return: 按loci的类型输出
        """
        if type(loci) == int or type(loci) == str:
            result = iter[loci]
            print(loci,result)
        elif type(loci) == list or type(loci) == tuple or type(loci) == set:
            result = type(loci)(select_iter(loci=x, iter=iter) for x in loci)
        elif type(loci) == dict:
            result = {select_iter(loci=x, iter=iter): select_iter(loci=y, iter=iter) for x, y in loci.items()}
        else:
            raise TypeError
        return result


    def newname(self, path, name_dict, file, filetype, Olddir, i):
        # 出现文件名相同时, 获取新名字
        try:
            Newdir = os.path.join(path, '{}({}){}'.format(name_dict[file], i, filetype))
            os.rename(Olddir, Newdir)
        except FileExistsError:
            i += 1
            newname(path, name_dict, file, filetype, Olddir, i)


    def rename(self, file, path, name_dict):
        """
        通用 重命名函数, 输入批量替换的字典 源文件, 路径名, 替换, 针对完整文件名替换
        根据字典映射，以值（新文件名）替换键（旧文件全名）
        :param file: 旧文件名
        :param path: 文件所在路径
        :param name_dict: {旧文件全名：新文件名}
        :return:
        """
        (oldname, filetype) = os.path.splitext(file)
        print((oldname, filetype))
        try:
            new_file = name_dict[file] + filetype
            Olddir = os.path.join(path, file)  # 原来的文件路径
            Newdir = os.path.join(path, new_file)
            try:
                os.rename(Olddir, Newdir)  # 重命名
                print('{} 重命名成功!!!'.format(file))
            except FileExistsError:
                # 遇到重复文件
                i = 1
                newname(path=path, name_dict=name_dict, file=file, filetype=filetype, Olddir=Olddir, i=i)
        except KeyError:
            print(file)


def del_NAN(text):
    if type(text) == str and text.upper() == 'NAN':
        return ''
    else:
        return '{}'.format(text)


def appendToDict(key, value, dic):
    # 默认不需要去重，且对增加顺序有要求
    try:
        dic[key].append(value)
    except KeyError:
        dic[key] = [value]


def addToDict(key, value, dic):
    # 每个键对应的一系列值的元素有重复 但是无顺序要求
    try:
        dic[key].add(value)
    except KeyError:
        dic[key] = {value}


def tsvline(inputlist):
    plus = [del_NAN(x) for x in inputlist]
    return '\t'.join(plus) + '\n'


def rev_split(text, spacer, num=-1):
    return text[::-1].split(spacer, num)[0][::-1]


def fastSelectTsv(path, filename, *kwag):
    tsv = Fileconvert(path=path).tsv2list(filename=filename)
    return type(*kwag)(select_iter(*kwag, x) for x in tsv if x)


def select_iter(loci, iter):
    if type(loci) == int:
        final = iter[loci]
    elif type(loci) == list or type(loci) == tuple or type(loci) == set:
        final = type(loci)(select_iter(loci=x, iter=iter) for x in loci)
    elif type(loci) == dict:
        final = {select_iter(loci=x, iter=iter): select_iter(loci=y, iter=iter) for x, y in loci.items()}
    else:
        raise TypeError
    return final


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
    _text = text.replace('\xa0', sep)

    html_dict = html_character()
    # 先替换html转有特殊字符
    for x, y in html_dict.items():
        _ = _text.split(x)
        if len(_) >= 2:
            _text = y.join(_)

    # 若存在制表符，则进行过滤， 由于多个制表符常在一起，按一个分割后每个元素strip即可
    _text = sep.join(filter_null(_text.split()))
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


# 出现文件名相同时, 获取新名字
def newname(path, name_dict, file, filetype, Olddir, i):
    try:
        Newdir = os.path.join(path, name_dict[file] + '(' + str(i) + ')' + filetype)
        os.rename(Olddir, Newdir)
    except FileExistsError:
        i += 1
        newname(path, name_dict, file, filetype, Olddir, i)


# 通用 重命名函数, 输入批量替换的字典 源文件, 路径名, 替换, 针对完整文件名替换
def rename(file, path, name_dict):
    """
    根据字典映射，以值（新文件名）替换键（旧文件全名）
    :param file: 旧文件名
    :param path: 文件所在路径
    :param name_dict: {旧文件全名：新文件名}
    :return:
    """
    (oldname, filetype) = os.path.splitext(file)
    print((oldname, filetype))
    try:
        new_file = name_dict[file] + filetype
        Olddir = os.path.join(path, file)  # 原来的文件路径
        Newdir = os.path.join(path, new_file)
        try:
            os.rename(Olddir, Newdir)  # 重命名
            print('{} 重命名成功!!!'.format(file))
        except FileExistsError:
            # 遇到重复文件
            i = 1
            newname(path=path, name_dict=name_dict, file=file, filetype=filetype, Olddir=Olddir, i=i)
    except KeyError:
        print(file)


def splfilename(filename, sep='.'):
    # 分割文件名，返回（文件名，扩展名）
    fileformat = filename.split(sep)[-1]
    length = len(filename) - len(fileformat) - 1
    name = filename[:length]
    return (name, fileformat)