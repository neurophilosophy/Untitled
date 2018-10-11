from xml.etree import ElementTree
import xml.etree
def xml2json(Elemnt):
    if type(Elemnt) == xml.etree.ElementTree.Element :
    # 传入的为xml.etree.ElementTree.Element类型
        return {Elemnt.tag: _parse(Elemnt)}

    elif type(Elemnt) == xml.etree.ElementTree.ElementTree:
        return {Elemnt.getroot().tag: _parse(Elemnt.getroot()) }

    elif type (Elemnt) == str:
    # 传入的为k可以转化为xml.etree.ElementTree.Element类型
        root = ElementTree.fromstring(Elemnt)
        return {root.tag: _parse(root)}
    else:
        raise TypeError


def _parse(Elemnt):
    # 汇集所有本层子标签
    tags = [child.tag for child in list(Elemnt)]
    # 递归汇集{子标签: 解析内容}
    p_childs = [(child.tag, _parse(child)) for child in list(Elemnt)]
    if not tags:
        # 文本处理
        text = Elemnt.text.strip()

        if text:
            text = text.strip()
        else:
            text = ''
        return text
    if len(set(tags)) < len(tags):
        # 列表处理 子元素存在不同标签则为列表
        result = [dict([x]) for x in p_childs]
    else:
        # 字典处理
        result = dict(p_childs)
    return result