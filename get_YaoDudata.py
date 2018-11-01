from Fileconvert import *
import pandas as pd
import numpy as np
import time
import json
import requests
from bs4 import BeautifulSoup
import bs4
import string

print(string.ascii_letters)
time0 = time.time()

path = 'C://Users/Administrator/Desktop'
fc = Fileconvert(path=path)
url = 'https://www.mycancergenome.org/content/molecular-medicine/anticancer-agents'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}


def tryReplace(key, a_dict):
    try:
        return a_dict[key]
    except KeyError:
        return key


def get_aa_num(text):
    return re.findall(r'([A-Z](\d+))[A-Z]', text)[0]


def multi_num(text_list):
    for x in text_list:
        print(get_aa_num(x))


def joinlist(text, sep='; '):
    return sep.join(text.split('\t'))


def get_EnstDict(OncoKbFile='OncoKB_ENST.tsv', CuraFile='精选ENST.tsv', VEPFile='VEP采用的ENST.tsv'):
    OncoKb_dict = {x[0]: x[2] for x in fc.tsv2list(OncoKbFile)}
    Cura_dict = {x[0]: x[2] for x in fc.tsv2list(CuraFile)}
    VEP_dict = {x[0]: x[2] for x in fc.tsv2list(VEPFile)}


txt = '''2	3	6	7	8	12	13	15	17
'''


def unify_all(text, sep=','):
    return sep.join([x.strip() for x in text.split('\t')])





# -------------------------------------------------解析网页的分割线-------------------------------------------------------
"""
解析保存到本地的网页。
"""


def get_ElementTag(url_file, tag, is_url=True):
    if is_url:
        page = requests.post(url_file, headers=header).text
        # print('Conection OK!!')
    else:
        page = open(url_file, 'r', encoding='utf-8')
    soup = BeautifulSoup(page, 'lxml')
    # 不一定所有的都有tag数据
    tab = soup.select(tag)
    return tab

    # 获取第一个有文本的标签对中的内容,用于获取已经被td或者th标签对圈定的内容中的文本


def get_tag_Text(element_Tag, sep=' '):
    """
    用于获取<td>te<td>text《》<a>65+5+6<th>mmmmmm</th><a></td>xt</td>中的'te', 'text'，td也可以是列表
    td标签对中的a可以被获取但是tr th等不能被获取
    :param element_Tag: 已经被td或者th标签对圈定的文本，可以是列表也可以是bs4.element.Tag
    :return: 均返回一个列表
    """
    if type(element_Tag) == list:
        return [clear_spacer(x.getText(), sep=sep) for x in element_Tag if x]
    elif type(element_Tag) == bs4.element.Tag:
        return [clear_spacer(element_Tag.getText(), sep=sep)]
    else:
        raise TypeError


# 针对行长短不一的表格，选择tag标签对,长度超过给定长度的按给定长度选取, 不足的pass
def get_line_tag(line, tag, length):
    """
    针对line的内容,选择tag标签对,长度超过给定长度的按给定长度选取, 不足的pass
    :param line:line的内容, 类型为 bs4.element.Tag
    :param tag:选择的tag标签对
    :param length:给定长度
    :return: 有则返回文本,无则None
    """
    if len(get_tag_Text(line.select(tag))) >= length:
        return get_tag_Text(line.select(tag))[:length]
    else:
        print(line)
        return None


def append_plus(plus, gene_name, data_type, df_title):
    """
    一行的列表转为df后，第一列插入基因名，后面
    :param plus:输入的需要写入tsv的列
    :param df_title:表头
    :param gene_name:基因名
    :param data_type: 表格归属于variant还是evidence等
    :param add_title: 是否加标题，默认不加
    :return:
    """
    df = pd.DataFrame([gene_name] + plus).T
    df.columns = ['Gene'] + df_title
    if os.path.isfile('.\\CKB_{}.tsv'.format(data_type)):
        add_title = None
    else:
        add_title = True
    df.to_csv('CKB_{}.tsv'.format(data_type), sep='\t', index=None, header=add_title, mode='a+')


# 由<table>标签对圈定的表格，获取表格中的内容,一般性地获取， 标题成为df的columns
def get_table(table_tag):
    """
    获取表格内容函数，包含标题和所有行数据,只采用td的原因在于CKB部分数据是没有tr
    :param table_tag: 由<table>标签对圈定的内容，类型为 bs4.element.Tag
    :return: df
    """
    title = get_tag_Text(table_tag.select('th'))
    title_max = len(title)  # 标题长度
    # 整行直观数据获取，最后插入标题
    content = table_tag.select('td')

    if content == []:
        return 'None'
    else:
        line_max = len(content) // title_max  # 总共内容的行数
        # 整行直观数据获取,td的总数量是title长度的整数倍，故行数为两者之商， 以content[ title_max*i : title_max*(i+1) ]来获取每一行，最后插入标题
        final_table = [get_tag_Text(content[title_max * i: title_max * (i + 1)]) for i in range(line_max)]
        df = pd.DataFrame(final_table)
        df.columns = title
        return df


def parse_yaodu(file, final_table, all_drug):
    tables = get_ElementTag(url_file=file, tag='div[class="basicnews_list_bottom_content_left"]', is_url=False)

    # IMG对应的文字字典
    img_dict = {'https://dstatic.pharmacodia.com/drug/highest/20180201135545_SBhC.png': '2018年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170804184718_8GUx.png': '2017年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104609_1d67.jpg': '2016年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104523_TaqK.jpg': '2015年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104549_3C1w.jpg': '2014年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104556_2e9b.jpg': '2013年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104602_iAR1.jpg': '2012年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104535_LWUS.jpg': '2011年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104543_dDTw.jpg': '2010年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104626_7Wyj.jpg': '2009年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104635_LM6w.jpg': '2008年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104642_OAZz.jpg': '2007年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104648_NCie.jpg': '2006年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104656_e814.jpg': '2005年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104705_I6Cc.jpg': '2004年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104713_chA2.jpg': '2003年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104722_BL8a.jpg': '2002年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104732_Ia8K.jpg': '2001年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104741_7wOz.jpg': '2000年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104750_PB64.jpg': '1999年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104806_AfDd.png': '1998年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170804185121_S3fQ.png': '1997年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104816_tyDZ.jpg': '1996年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104826_pqdw.png': '1995年批准',
                'https://dstatic.pharmacodia.com/drug/highest/20170804185207_YIas.png': '批准上市',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104035_ZB1b.png': 'NDA申请',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104149_9tC7.png': 'BLA申请',
                'https://dstatic.pharmacodia.com/drug/highest/20170619103959_drhV.png': 'I期临床',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104015_T5K9.png': 'II期临床',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104025_Zqtf.png': 'III期临床',
                'https://dstatic.pharmacodia.com/drug/highest/20170619104137_rEjS.png': '临床申请',
                }

    for tab in tables:
        p_tags = get_tag_Text(tab.select('p'), sep=' ')

        general_names, commercial_names, indication, targets, company, external_ids, others = tuple(p_tags)

        # 通用名
        if '(' in general_names and general_names != 'Lutetium(177Lu) oxodotreotide':
            general_name_eng, general_name_chn = splfilename(filename=general_names.strip(')'), sep=' (')
        else:
            general_name_eng, general_name_chn = general_names, ''

        # 商品名
        status = ''
        if '/' in commercial_names:
            commercial_names = commercial_names.replace('®', '').strip('()')
            commercial_name_eng, commercial_name_chn = commercial_names.split('/')[0], commercial_names.split('/')[-1]
            final_commercial_name = '{}（{}）'.format(commercial_name_chn, commercial_name_eng)
            if not commercial_names[-2] in string.ascii_letters:
                status = '已中国上市'
        else:
            final_commercial_name = commercial_names.strip('( ®)')

        # 适应症，靶点，研发公司，研发代号，其他
        indication = indication.split('：')[1]
        targets = targets.split('：')[1]
        company = company.split('：')[1]
        external_ids = external_ids.split('：')[1]
        others = others.split('：')[1]

        # 图片判断上市或临床阶段
        try:
            img_tag = img_dict[tab.select('p img')[0].get('src')]
            if img_tag != '批准上市' and '临床' not in img_tag:
                if status == '已中国上市':
                    approved_status = '，'.join(('{}上市'.format(img_tag), status))
                else:
                    approved_status = '{}上市'.format(img_tag)
            else:
                approved_status = img_tag
        except IndexError:
            approved_status = ''

        plus = ('', general_name_eng, final_commercial_name, general_name_chn, targets, approved_status,
                '', indication, '', '', external_ids, '', indication, others, company)
        if not all_drug & {plus}:
            # tsv.write(fc.tsvline(plus))
            all_drug.add(plus)
            final_table.append(plus)


def get_yaodu_data(yaodu_path='C:\\Users\\Administrator\\Desktop\\药渡数据2018.10.24'):
    rank_dict = {'2018年批准上市，已中国上市': 100,
                 '2018年批准上市': 99,
                 '2017年批准上市，已中国上市': 98,
                 '2017年批准上市': 97,
                 '2016年批准上市，已中国上市': 96,
                 '2016年批准上市': 95,
                 '2015年批准上市，已中国上市': 94,
                 '2015年批准上市': 93,
                 '2014年批准上市，已中国上市': 92,
                 '2014年批准上市': 91,
                 '2013年批准上市，已中国上市': 90,
                 '2013年批准上市': 89,
                 '2012年批准上市，已中国上市': 88,
                 '2012年批准上市': 87,
                 '2011年批准上市，已中国上市': 86,
                 '2011年批准上市': 85,
                 '2010年批准上市': 84,
                 '2009年批准上市，已中国上市': 83,
                 '2009年批准上市': 82,
                 '2008年批准上市': 81,
                 '2007年批准上市，已中国上市': 80,
                 '2007年批准上市': 79,
                 '2006年批准上市，已中国上市': 78,
                 '2006年批准上市': 77,
                 '2005年批准上市，已中国上市': 76,
                 '2005年批准上市': 75,
                 '2004年批准上市，已中国上市': 74,
                 '2004年批准上市': 73,
                 '2003年批准上市，已中国上市': 72,
                 '2003年批准上市': 71,
                 '2002年批准上市，已中国上市': 70,
                 '2002年批准上市': 69,
                 '2001年批准上市，已中国上市': 68,
                 '2001年批准上市': 67,
                 '2000年批准上市，已中国上市': 66,
                 '2000年批准上市': 65,
                 '1999年批准上市，已中国上市': 64,
                 '1999年批准上市': 63,
                 '1998年批准上市，已中国上市': 62,
                 '1998年批准上市': 61,
                 '1997年批准上市，已中国上市': 60,
                 '1997年批准上市': 59,
                 '1996年批准上市，已中国上市': 58,
                 '1996年批准上市': 51,
                 '1995年批准上市，已中国上市': 50,
                 '1995年批准上市': 10,
                 'NDA申请上市': 9,
                 'BLA申请上市': 8,
                 '批准上市': 7,
                 'III期临床': 6,
                 'II期临床': 5,
                 'I期临床': 4,
                 '临床申请': 3,
                 }

    all_drug = set()

    final_table = []
    fc = Fileconvert(path=yaodu_path)
    files = [x for x in os.listdir(yaodu_path) if x.endswith('html')]
    for file in files:
        parse_yaodu(file=file, final_table=final_table, all_drug=all_drug)
    final_table.sort(key=lambda x: rank_dict[x[5]], reverse=True)
    title = ['Disease', 'General_Name', 'Commercial_Name', 'Chinese_Name', 'Target', 'CFDA_Approved', 'Insurance_Notes',
             'Indication', 'Resistance_Mechanism', 'Final_name', 'Aliase', 'No.', 'Indication_English', 'Pharmacology',
             'Company']
    df = pd.DataFrame(final_table)
    os.chdir(path=path)
    df.to_csv('药渡汇总.tsv', sep='\t', header=title, index=None, mode='w', encoding='utf-8')


get_yaodu_data()
