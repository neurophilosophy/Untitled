from colorama import Fore, Back, Style
print(Fore.GREEN + 50*'-')
import time
import os
import re
import tqdm
from pprint import pprint

from Fileconvert import Fileconvert
time0 = time.time()
from bs4 import BeautifulSoup

# 输入的Document 既可以是Document也可以是Element

def get_Text_Within_Tags(parentTag, childTag, Document):
    if Document.getElementsByTagName(parentTag):
        return getTagText(Document.getElementsByTagName(parentTag), childTag)
    return ''

# getElementsByTagName返回一个Nodeslist，其中的元素均为Element属性，仅Element属性方能以index用childNodes[0].data获取内容
# Nodeslist为标签相同的所有节点，Element由一对标签头尾包绕，与Document相似。
# 获取所有该父标签下，同一子标签的所有内容

def getTagText(Nodeslist, childTag, separater = '|'):
    if len(Nodeslist)>=1:
        # 元素下getElementsByTagName(tag)不一定依然有标签 故需要if判断 True,同时get到的不止1个
        texts = []
        for Element in Nodeslist:
            # 如果Element有tag，则从Element获取Nodeslist后遍历 获取内容
            if Element.getElementsByTagName(childTag):
                content = Element.getElementsByTagName(childTag)
                if len(content) > 1 :
                    text = [x.childNodes[0].data.strip() for x in content if x]
                    texts.append('{}'.format(separater).join(text))
                else:
                    texts.append(content[0].childNodes[0].data)
        result = list(filter(lambda x:x ,texts))
        if result != []:
            return '{}'.format(separater).join(result)
    return ''


path = 'C://Users/Administrator/Desktop'  # WIN10 PATH

fc = Fileconvert(path)
"""
import xml.sax

class MovieHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.type = ""
        self.format = ""

    # 元素开始调用
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "drug":
            print("*****Drugs*****")

    # 元素结束调用
    def endElement(self, tag):
        if self.CurrentData == "name":
            print("Name:", self.type)

        self.CurrentData = ""

    # 读取字符时调用
    def characters(self, content):
        if self.CurrentData == "name":
            self.type = content




if (__name__ == "__main__"):
    # 创建一个 XMLReader
    parser = xml.sax.make_parser()
    # 关闭命名空间
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # 重写 ContextHandler
    Handler = MovieHandler()
    parser.setContentHandler(Handler)

    parser.parse("full database.xml")
"""

def DrugBank():
    drugbank = open('full database.xml','r', encoding='utf-8')

    soupdrug = BeautifulSoup(drugbank,'lxml')
    durgs = soupdrug.select('gene-sequence')

    title = """<?xml version="1.0" encoding="UTF-8"?>
<drugbank xmlns="http://www.drugbank.ca" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.drugbank.ca http://www.drugbank.ca/docs/drugbank.xsd" version="5.1" exported-on="2018-07-03">
"""
    drugbank = open('full database.xml','r', encoding='utf-8')
    new = open('drugbank0.xml','w',encoding='utf-8')
    new.write(title)
    num = 0
    wirte_right = False
    plus =''
    right = False
    count = 0
    for line in drugbank:

        if line.strip().startswith('<drug '):
            right =True
        if right:
            num += 1
            plus += line

        if line.startswith('</drug>') :
            right = False
            groups = ['approved', 'experimental', 'investigational']
            for group in groups:
                if '>{}<'.format(group) in plus:
                    wirte_right =True
            if wirte_right:
                if num // 500000 > count :
                    new.write("\n</drugbank>\n")
                    new.close()
                    print('drugbank%s.xml Done!!'%str(count))
                    count = num // 500000
                    new = open('drugbank%s.xml'%str(count), 'w', encoding='utf-8')
                    new.write(title)
                new.write(plus)
                wirte_right = False
                plus = ''
    new.write("\n</drugbank>\n")
    new.close()


#DrugBank()

time1 = time.time()
print('当前运行耗时%a秒' % (time1 - time0))

from xml.dom.minidom import parse
import xml.dom.minidom

# 使用minidom解析器打开 XML 文档
def xml_element(text,data):
    try:
        # 获取drugdata里的tag标签里的内容
        content = []
        # nodelist由element构成
        # data为一个nodelist，getElementsByTagName即为获取data目录下，以text为两端标签的内容， 不论text是否为data的子节点或text为data一个子节点的子节点
        # childNodes为获取nodelist的子节点，childNodes[y].data为获取nodelist子节点中第y个的内容
        for x in data.getElementsByTagName(text):
            if len(x.childNodes) > 1:
                print(x.childNodes)
                print('这个标签里子节点大于1个', [y.data for y in x.childNodes if y])
            line = x.childNodes[0].data
            content.append(line)
        content = '|'.join(content)
        out = ''.join(content.split('\r\n'))
        return out
    except IndexError:
        return ''
drugTags = ['name','description','groups','indication','mechanism-of-action','synonyms','targets']
chimericTags = ['groups','synonyms','targets']
innerTags = ['group','synonym','gene-name']
innerTag_dict = dict(zip(chimericTags, innerTags))
tag_dict = { y : x for x, y in enumerate(drugTags)}

def xml_dom(filename, newfile):
    DOMTree = xml.dom.minidom.parse(filename)
    collection = DOMTree.documentElement
    # 在drugbank集合中获取所有药物数据
    drugs = collection.getElementsByTagName("drug")
    # 打印每个药物的详细信息中需要的部分，drug汇总所有药物信息，drugdata为单项药物信息。
    # drugdata.getElementsByTagName(tag)意味着在drugdata这个药物信息下获取直属的标签tag里的信息，后者可以是仅包含字符串且无内在嵌套标签的可以是嵌套标签的
    # 单项药物信息drugdata.getElementsByTagName(tag)，即获取tag标签内信息后，是一个列表，需要对其内部的每一项调用
    for drugdata in drugs:
        plus = (len(drugTags) +1) * ['-']
        # 获取药物类型，是小分子或者其他化合药的信息
        if drugdata.hasAttribute("type"):
            plus[-1] = drugdata.getAttribute("type")
        # 列表中的每个标签获取数据，
        for tag in drugTags:
            if tag in chimericTags:
                groups = drugdata.getElementsByTagName(tag)
                if len(groups) >= 1:
                    # 获取group里的innertag的内容，并且汇总
                    tagcontent = list(filter(lambda x:x, [xml_element(innerTag_dict[tag], group) for group in groups]))
                    pluscontent = '|'.join(tagcontent)
                    #print('当前标签', tag, innerTag_dict[tag], '获取的内容是：', pluscontent)
                else:
                    pluscontent = ''
            else:
                pluscontent = xml_element(tag, drugdata)
            plus[tag_dict[tag]]= pluscontent
        if 'approved' in plus[tag_dict['groups']].lower() or 'experimental' in plus[tag_dict['groups']].lower() or 'investigational' in plus[tag_dict['groups']].lower() :
            newfile.write('\t'.join(plus) + '\n')
    time1 = time.time()
    print('{} Done!!!'.format(filename),"运行总共耗时为%a秒" % (time1 - time0))
def main():
    newfile = open('drugbank.tsv', 'w', encoding='utf-8')
    newfile.write('\t'.join(drugTags + ['type']) + '\n')
    for i in range(40):
        xml_dom('drugbank%s.xml' % str(i), newfile)
tqdm.tqdm(main())

time1 = time.time()
print("运行总共耗时为%a秒" % (time1 - time0))