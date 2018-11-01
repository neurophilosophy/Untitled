from XML_wheels import *
from fuzzywuzzy import fuzz
from pprint import pprint
import re
import time
time0 = time.time()
# 是否有关键字的选择器, 有则True
def feature_selector(keyword, result):
    if keyword in result:
        return True
    else:
        return False

def get_genes_dict(path = 'C://Users/Administrator/Desktop', filename= '基因介绍列表-merged-merged.tsv'):
    global fc
    fc = Fileconvert(path)
    genes = fc.tsv2list(filename)
    genes_dict = {x[0]:'-' for x in genes}
    new_dict = {'PD-L1':'-', 'HER2':'-', 'T790M':'-'}
    genes_dict.update(new_dict)
    return genes_dict

# 文本筛选器
def selector(textlist, genes_dict):
    _new ={}
    # 按分割符号分割后的列表, 遍历各单词, 是基因的录入,HER2需要特殊替换
    for i in range(len(textlist)):
        x = textlist[i]
        if x.isupper():
            try:
                exclu_word = ['negative', 'Negative', 'Wildtype']
                exclu_words = [('fusion', 'negative'), ('rearrangement', 'negative'), ('wild', 'type')]
                aliase_dict = {'BIM': 'BCL2L11', 'NY-ESO-1': 'CTAG1B', 'HER2': 'ERBB2', 'HER4': 'ERBB4',
                               'HER3': 'ERBB3', 'ROS': 'ROS1', 'PI3K': 'PIK3CA', 'T790M': 'EGFR T790M'}
                condition1 = (i<len(textlist)-2 and genes_dict[x] and textlist[i+1] not in exclu_word and textlist[i+1: i+3] not in exclu_words)
                condition2 = (genes_dict[x] and i == len(textlist)-1)
                if condition1 or condition2:
                    try:
                        _new[aliase_dict[x]] = '-'
                    except:
                        _new[x] = '-'
            except KeyError:
                pass

    #返回基因列表字典
    return _new

"""
获取生物标志物的函数,输入文本和分隔符, 返回合并的标志物总和字符串
"""
def get_biomaker(text, therapy, genes_dict, spacer = ', '):
    """
    获取生物标志物的函数,输入文本和分隔符, 返回合并的标志物总和字符串
    """
    if not text:
        return '-'
    _text = text
    # 先替换掉希腊字母,再文本分割后进行选择
    Greek_dict = {'α': 'A', 'β': 'B', 'δ': 'D', 'ε': 'E', 'η': 'H', 'γ': 'G', 'ι': 'I', 'θ': 'Q', 'ζ': 'Z', 'κ': 'K',
                  'Θ': 'Q', 'alpha': 'A', 'Alpha': 'A', 'beta': 'B', 'Beta': 'B', 'delta': 'D', 'Delta': 'D',
                  'epsilon': 'E', 'Epsilon': 'E', 'eta': 'H', 'Eta': 'H', 'gamma': 'G', 'Gamma': 'G',
                  'iota': 'I', 'Iota': 'I', 'theta': 'Q', 'Theta': 'Q', 'zeta': 'Z', 'Zeta': 'Z', 'kappa': 'K',
                  'Kappa': 'K'}
    SpecBiomarker_dict = {'NTRK':{'NTRK1':'-','NTRK2':'-','NTRK3':'-'}, 'FGFR1/2/3': {'FGFR1':'-','FGFR2':'-','FGFR3':'-'},
                     'PD-L1':{'PD-L1':'-'}, 'AKT':{'AKT1','-','AKT2','-','AKT3','-'} }


    for x,y in Greek_dict.items():
        if x in _text:
            _text = _text.replace(x, y)
    _text =tuple( filter( lambda x:x, re.split(r'[, :\-\./\'\?\(\)\\\,\"\:\;]', _text)))
    _result = selector(_text, genes_dict)

    # 对于多个基因可能写在一起的特殊格式处理
    immuno = {}


    if 'PD-L1' in _text:
        immuno.update( {'PD-L1':'-'})


    try:
        if immuno['PD-l1']:
            pass
    except KeyError:
        drugs = therapy.split(' | ')
        for drug in drugs:
            if drug.title() in ['Durvalumab', 'Atezolizumab', 'Nivolumab', 'Pembrolizumab']:
                immuno.update({'PD-L1': '-'})

    search = re.search(r'exon 20( \S+)? insertion', text, re.IGNORECASE)
    if search:
        try:
            if _result['EGFR']:
                immuno.update({'EGFR Exon 20 Insertions':'-'})
        except KeyError:
            pass

    _result.update(immuno)

    return spacer.join(_result.keys())


def get_indication(Indication, spacer = ' | '):
    _indication = Indication.split(spacer)
    final_disease = []
    for i in range(len(_indication)):
        each  = _indication[i]
        each = re.sub(r'AJCC v\d( and v\d)?', '', each, re.IGNORECASE)
        each = re.sub(r'NP_\d+\.\d:p\.', '', each, re.IGNORECASE)
        _indication[i] = each
    return spacer.join(_indication)


def clear_criteria(text):
    if text.startswith('Criteria') or text.startswith('criteria') or text.startswith('CRITERIA'):
        return text[8:].strip(' :-')
    return text

def get_inclu_exclu_criteria(criteria):
    # 入组标准和排除标准
    search_Exclusion = re.findall(r'Exclusion', criteria, re.IGNORECASE)
    search_Inclusion = re.findall(r'Inclusion', criteria, re.IGNORECASE)
    if search_Exclusion:
        _criteria = criteria.split(search_Exclusion[0])
    else:
        _criteria = [criteria, '-']
    try:
        (Inclusion_Criteria , Exclusion_Criteria) = (clear_criteria(_criteria[0].split(search_Inclusion[0])[1].strip(':- ')),
                                                     clear_criteria(_criteria[1].strip(':- ')))
        if not Inclusion_Criteria:
            print('Inclusion_Criteria是空值')
        elif not Exclusion_Criteria:
            print('Exclusion_Criteria是空值')
        return (Inclusion_Criteria , Exclusion_Criteria)
    except IndexError:
        print('IndexError!!!: {}'.format(criteria))
        return (criteria, '-')


# 地点联系方式的获取


def loci_value(city_state, country, cutoff, maincity='Shenzhen', mainstate = 'Guangdong'):

    if country == 'China':
        if fuzz.partial_ratio(maincity, city_state)> cutoff:
            value = 12
        elif fuzz.partial_ratio(mainstate, city_state) > cutoff:
            value = 11
        elif fuzz.partial_ratio('Jiangsu', city_state)> cutoff:
            value = 10
        elif fuzz.partial_ratio('Shanghai', city_state)> cutoff:
            value = 9
        elif fuzz.partial_ratio('Beijing', city_state)> cutoff:
            value = 8
        elif fuzz.partial_ratio('Chengdu', city_state)> cutoff:
            value = 7
        elif fuzz.partial_ratio('Changsha', city_state)> cutoff:
            value = 6
        elif fuzz.partial_ratio('Wuhan', city_state)> cutoff:
            value = 5
        elif fuzz.partial_ratio('Hangzhou', city_state)> cutoff:
            value = 5
        else:
            value = 4
    elif 'Hong Kong' == country:
        value = 3
    elif 'Taiwan' == country:
        value = 2
    elif 'United States' == country:
        value = 1
    else:
        value = 0
    return value

def loci_contact(element):
    # 输入一个location的 Element
    _location = get_uniqueTagText('location', element)
    # 解决location中两个PI导致不能生成字典的问题
    if type(_location) == list:
        new = {}
        for x in _location:
            new.update(x)
        _location = new

    # 获取招募状态
    _status = try_key_value('status', _location)
    if _status == 'Compeleted':
        return

    # 获取地址,并给予地址赋分
    facility = _location['facility']
    (hospital, address) = tuple(try_key_value(y, facility) for y in ['name', 'address'])
    (city, state, zip, country) = tuple(try_key_value(y, address) for y in address_list)
    city_state = city + ' ' + state
    value = loci_value(city_state, country, 80)

    # 获取联系方式
    try:
        _contact = _location['contact']
        (last_name, phone, email) = (try_key_value(y, _contact) for y in contact_list)
        if last_name == 'Study Coordinator':
            try:
                last_name = _location['investigator']['last_name']
            except KeyError:
                pass
    except KeyError:
        (last_name, phone, email) = ('', '', '')

    # 根据联系方式是否完整来打分
    if phone == email == '':
        contact_value = 0
    elif phone != '' and  email != '':
        contact_value = 2
    else:
        contact_value = 1

    return (hospital, city, state, country, _status, last_name, phone, email, contact_value, value)

def get_best_loci_contact(location, overall_contact):
    # 输入的location是个列表, 而overall_contact是字典
    global contact_list, address_list

    address_list = ['city', 'state', 'zip', 'country']
    contact_list = ['last_name', 'phone', 'email']

    # location 不为空, 则汇总location中的地址 状态 和联系方式,按规则排序后取第一项,若第一项的联系房事后为空
    if list(location) != []:
        # 汇总试验地点列表
        loci_contact_list = [loci_contact(x) for x in location if loci_contact(x)]

        # 超过1项, 则根据排序规则排序
        if len(loci_contact_list) > 1:
            loci_contact_list.sort(key=lambda x: (x[-1], x[-2], x[4], x[7], x[6]), reverse=True)

        # 取第一项为最佳项
        best_loci_contact = loci_contact_list[0]

        # 过滤掉中间的空值项
        loci, contact = filter_null(best_loci_contact[:4]), filter_null(best_loci_contact[5:-2])

        if best_loci_contact[-2] == 0 and type(overall_contact) != str:
            overall = [try_key_value(y, overall_contact) for y in contact_list]
            # 过滤掉中间的空值项
            contact = filter_null(overall)

        return ('; '.join(loci), ', '.join(contact))

    elif type(overall_contact) != str:
        overall = [try_key_value(y, overall_contact) for y in contact_list]
        contact = filter_null(overall)

        return ('', ', '.join(contact))

    else:
        return ('', '')




def get_NCT_trails_by_dom(file_path, NCT_output, NCT_number, rank, genes_dict):
    # 打开文件, 不存在则结束.
    try:
        xml_file = ElementTree.parse(file_path)
    except FileNotFoundError:
        print(file_path , 'FileNotFoundError')
        return
    # 核验NCT号
    Register_Num = get_directText('nct_id', xml_file)
    if Register_Num != NCT_number:
        print('这个NCT号有问题:应当是{}, 实际是{}'.format(NCT_number, Register_Num))

    # 试验招募状态
    Status = get_directText('overall_status', xml_file)

    # 试验用药, Therapy 必须要在biomarker前获取, 以防止知名的PD-1抗体药物没有PD-L1的biomarker文本出现
    Therapy = get_allDirectText_byTagName('intervention_name', xml_file)

    # 适应症
    Indication = get_indication(get_allDirectText_byTagName('condition', xml_file), ' | ')


    # 临床试验标题
    Title = get_directText('brief_title', xml_file)

    # 临床试验概述, 需要清除掉特殊的\n 和空格等
    Description = clear_spacer(get_uniqueChildTagText('brief_summary', 'textblock',xml_file))

    # 临床试验阶段
    Phase = get_directText('phase', xml_file)

    # 入组和排除标准的文本获取和分割,需要清除掉特殊的\n 和空格等
    criteria = clear_spacer(get_uniqueChildTagText('criteria', 'textblock', xml_file))
        # 入组和排除标准通常是合在一条文本条目里. 故需根据关键字分割
    (Inclusion_Criteria, Exclusion_Criteria) = get_inclu_exclu_criteria(criteria)

    # 通过标题,适应症,入组标准和概述,来获取基因关键字.
    Biomarker = get_biomaker(' | '.join([Title, Description, Inclusion_Criteria, Indication]), Therapy, genes_dict )

    # 同时获取排除标准的关键字
    neg_bio = get_biomaker(Exclusion_Criteria, Therapy, genes_dict)

    # 由于既存在没有overall_contact的也存在连contact也没有的, 存在的返回字典, 不存在的返回空字符串
    overall_contact = get_uniqueTagText('overall_contact', xml_file)

    # 获取试验地点列表, 若文件中没有试验地点则呈现空列表哦
    location = list(xml_file.iter('location'))

    # 通过location获取全部的facility和contacts, 同时对地点赋值,然后根据赋值排序
    (Location, Contacts) = get_best_loci_contact(location, overall_contact)
    # 集合所有需要的信息 写入输出文件
    plus = [str(rank), Register_Num, Status, Therapy, Indication, Title, Description, Phase, Biomarker,
            Inclusion_Criteria, Exclusion_Criteria, Location, Contacts, neg_bio]
    NCT_output.write('\t'.join(plus) + '\n')

    # 有写入则返回非空字符串, 以区别未写入的
    return 'Done'


def main():
    # 打开汇总NCT号的表格,获取NCT列表
    path = 'C://Users/Administrator/Desktop'
    fc = Fileconvert(path)
    soruce_file = 'SearchResults.tsv'
    outputfile = 'NCT_Clinical_Trials.tsv'
    NSCLC = fc.tsv2list(soruce_file)

    NCT_nums = [x[1] for x in NSCLC]
    genes_dict = get_genes_dict(path = 'C://Users/Administrator/Desktop', filename= '基因介绍列表-merged-merged.tsv')

    # 打开输出文件, 写入标题
    NCT_output = open(outputfile, 'w', encoding= 'utf-8')
    title = 'Rank	Register_Num	Status	Therapy	Indication	Title	Description	Phase	Biomarker	Inclusion_Criteria	Exclusion_Criteria	Location	Contacts\tNegative_Biomarker\n'
    NCT_output.write(title)

    # 每行写入新信息时, 生成序号
    rank = 1
    for NCT_number in  NCT_nums:
        file_path = "D://迅雷下载/AllPublicXML/%sxxxx/%s.xml" % (NCT_number[:-4], NCT_number)
        result = get_NCT_trails_by_dom(file_path, NCT_output, NCT_number, rank, genes_dict)
        if result:
            rank +=1


main()

time1 = time.time()
print("运行总共耗时为%a秒" % (time1 - time0))