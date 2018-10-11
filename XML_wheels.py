import time

time0 = time.time()
from xml_to_json import *
from xml.etree import ElementTree
from Fileconvert import  Fileconvert

# 过滤空值
def filter_null(somelist):

    return list(filter(lambda x:x, somelist))


# html字符替换
def html_character():
    html_dict =  {'&nbsp;': ' ','&lt;': '<','&gt;': '>','&amp;': '&','&quot;': '"','&apos;': '\'','&cent;': '￠',
                '&pound;': '£','&yen;': '¥','&euro;': '€','&sect;': '§','&copy;': '©','&reg;': '®','&trade;': '™',
                '&times;': '×','&divide;': '÷'}

    return html_dict


# 清除制表符等特殊字符
def clear_spacer(text, sep=' '):
    """
    清除文本中的特殊制表符
    """
    html_dict = html_character()
    _text = text
    for x,y in html_dict.items():
        _=_text.split(x)
        if len(_)>=2:
            _text = y.join(_)

    spacer = ''
    existance = False
    spacers = ['\n', '  ','\t\t', '\r\r', '\n\n']
    for x in spacers:
        if x in _text :
            existance = True
            spacer = x
            break
    if existance:
        pieces = filter(lambda x:x ,[x.strip() for x in _text.split(spacer)])
        return sep.join(pieces)
    return _text


# 测试是否在json数据里可以返回, 字符串或者字典
def try_key_value(key, _dict):
    """
    # 字典函数, 不存在键时返回值为''
    :param key: 键
    :param _dict: 迭代字典
    :return: 如果键不存在于字典, 返回'',存在则返回值
    """
    try:
        result = _dict[key]
        if type(result) == dict:
            return result
        return _dict[key].strip()
    except :
        return ''


"""
对于<唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属>, 
输入通过<唯一的属>标签所获得的直属的文本'张翠山','殷素素'不会返回
"""
def get_directText(uniqueTag, element):
    """
    对于<唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属>,
    输入通过<唯一的属>标签所获得的直属的文本'张翠山','殷素素'不会返回
    """
    try:
        return list(element.iter(uniqueTag))[0].text.strip()
    except IndexError:
        return ''

"""
转化json 获取<唯一的属>张翠山<唯一的种>张无忌</唯一的种></唯一的属>中的{'唯一的种':'张无忌'}
"""
def get_uniqueTagText(uniqueTag, element):
    """
    :param uniqueTag: 唯一性标签, 标签无重复, 且确定标签后有内容, 可以是字典也可以是文本
    :param element: 大的element
    :return: 用xml2json解析具有唯一性标签的element后去该标签圈定的内容
    """
    # 获取唯一标签后面的内容, 可以是文本也可以是字典, 但是不会按"唯一的属"获取<唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属>中的张翠山,后者可以考虑element.text.strip()获取
    try:
        return xml2json(list(element.iter(uniqueTag))[0])[uniqueTag]
    except IndexError:
        return ''


def get_uniqueChildTagText(uniqueTag, ChildTag, element):
    """
    #获取唯一子标签后面的内容, 可以是文本也可以是字典, 但是不会按"唯一的属"获取<唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属>中的张翠山,后者可以考虑element.text.strip()获取
    :param uniqueTag: 唯一性标签, 标签无重复, 且确定标签后有内容, 可以是字典也可以是文本
    :param element: 大的element
    :return: 用xml2json解析具有唯一性标签的element后去该标签圈定的内容
    """
    try:
        return xml2json(list(element.iter(uniqueTag))[0])[uniqueTag][ChildTag]
    except TypeError:
        tag_type = type(xml2json(list(element.iter(uniqueTag))[0])[uniqueTag])
        if tag_type == list:
            print('父标签<{}>圈定内容的类型是{},所以映射失败'.format(uniqueTag, tag_type))
        elif tag_type == str:
            print('父标签<{}>圈定内容的类型是{},所以映射失败'.format(uniqueTag, tag_type))
        else:
            print('父标签<{}>并不唯一或者没有父标签<{}>, 父标签的类型是{}'.format(uniqueTag, uniqueTag, tag_type))
        return ''
    except KeyError:
        print('<{}>并没有这个子标签'.format(ChildTag))
        return ''
    except IndexError:
        print('<{}>父标签下只有文本没有json'.format(uniqueTag))
        return ''


def get_allDirectText_byTagName(tagName, element, separater = ' | '):
    """
    #获取子标签后面的直接内容,并通过分隔符加和
    :param tagName:
    :param element:
    :param separater:
    :return:
    """
    try:
        return separater.join([x.text.strip() for x in element.iter(tagName)])
    except IndexError:
        return ''
    except AttributeError:
        return ''
"""

"""
def get_json_text_byUniquePath(json, taglist):
    _json = json
    for x in taglist:
        if type(_json) == dict:
            _json = _json[x]
            continue
        elif type(_json) == list:
            for y in _json:
                try:
                    _json = y[x]
                    break
                except KeyError:
                    continue
        elif type(_json) == str:
            return _json
        else:
            print('有未知错误', _json)
    return _json




"""
对于种, 输入Doc_Element为<九个属>张翠山<其他种></其他种><六个种>张无忌</六个种><其他>张三丰</其他></九个属><其他>张翠山<六个种>张无忌</六个种>殷素素</其他>
若Nodeslist通过<其他>获取的话, 那么,返回张三分|张翠山,用分隔符隔开.
"""

"""
对于<九个属>张翠山<其他种></其他种><六个种>张无忌</六个种><其他></其他></九个属>
Nodelist为以九个属为标签获得的Nodelist,然后返回值是获得了中的六个'张无忌'
"""

"""
对于属和种, 提供Doc_Element为<九个属>张翠山<其他种></其他种><六个种>张无忌</六个种><其他></其他></九个属>后
获取九个属下面的种,返回五十四个张无忌,用分隔符隔开.
"""


"""
获取<唯一的属>张翠山<唯一的种>张无忌</唯一的种></唯一的属>中的'张无忌'
"""


"""
对于种, 提供Doc_Element为<九个属>张翠山<其他种></其他种><六个种>张无忌</六个种><其他></其他></九个属><其他><六个种>张无忌</六个种></其他>
获取九个属和其他下面的种,返回六十个张无忌,用分隔符隔开.
"""


"""
获取<唯一的属>张翠山<唯一的种>张无忌</唯一的种></唯一的属>中的'张翠山'
"""



"""
获取元素内容为<倚天><唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属><唯一的属>张三丰<唯一的种>没啊</唯一的种>郭襄</唯一的属>809</倚天>中的所有文本集合,以分隔符隔开
返回结果"张翠山 | 张无忌 | 殷素素 | 张三丰 | 没啊 | 郭襄 | 809"
"""


"""
获取<唯一的倚天><唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属><唯一的属>张三丰<唯一的种>没啊</唯一的种>郭襄</唯一的属>809</唯一的倚天>中的所有文本集合,以分隔符隔开
"""


"""
获取<唯一的倚天><唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属><唯一的属>张三丰<唯一的种>没啊</唯一的种>郭襄</唯一的属>809</唯一的倚天>中"唯一的倚天"标签内的所有文本集合,以分隔符隔开
返回结果"张翠山 | 张无忌 | 殷素素 | 张三丰 | 没啊 | 郭襄 | 809"
"""

"""
获取<唯一的倚天><唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属><唯一的属>张三丰<唯一的种>没啊</唯一的种>郭襄</唯一的属>809</唯一的倚天>中"唯一的倚天"标签内的所有文本集合,以分隔符隔开
返回结果"张翠山 | 张无忌 | 殷素素 | 张三丰 | 没啊 | 郭襄 | 809"
"""


yitian = ElementTree.fromstring('''<倚天><唯一的属>张翠山<唯一的种>张无忌</唯一的种>殷素素</唯一的属><唯一的属>张三丰<唯一的种>没啊</唯一的种>郭襄</唯一的属>809</倚天>''')
#获取所有的<唯一的属>后面的内容

print(type(yitian))


print(get_allDirectText_byTagName('唯一的属', yitian))


print(get_uniqueChildTagText('唯一的属', '唯一的种', yitian))


print(get_uniqueTagText('唯一的属', yitian))

path = 'C://Users/Administrator/Desktop'

fc = Fileconvert(path)

jinyong = ElementTree.parse('金庸群侠传.xml')

print('当前运行get_uniqueTagText:', get_uniqueTagText('目', jinyong))

print('当前运行get_allData_byTagName:', get_allDirectText_byTagName('目', jinyong))

print('当前运行get_uniqueChildTagText:', get_uniqueChildTagText('科科科', '属', jinyong))

print('当前运行get_uniqueChildTagText:', get_uniqueChildTagText('科科', '属', jinyong))

print('当前运行get_uniqueChildTagText:', get_uniqueChildTagText('科', '属', jinyong))