from Fileconvert import Fileconvert
from pprint import pprint
import re
import time
import string
import pysam

# -------------------------------------------------写在前面-------------------------------------------------------------
"""
# 打开前手工修正CDH11{ENST00000268603}:r.1_444_USP6{ENST00000250066}:r.1-3177_r.1-3119_USP6{ENST00000250066}:r.1545_7976 ，中间多了个r.
# DNAJB1{ENST00000254322}:r.1_282+320_PRKACA{ENST00000308677}:r244-3566_2677 少了个r.
# 以下的8条为坐标不确定，有1-3碱基的波动，那么按照探针最短来选择
# TMPRSS2{ENST00000332149}:r.1-8047_1-8000_ETV4{ENST00000319349}:r.322-19_2391
# EWSR1{ENST00000397938}:r.1_1112+523_DDIT3{ENST00000547303}:r.76-604_872
# FUS{ENST00000254108}:r.1_866_ERG{ENST00000442448}:r.1141-1575_5034
# TMPRSS2{ENST00000332149}:r.1-1500_373_ETV5{ENST00000306376}:r.174_4111
# NAB2{ENST00000300131}:r.1_1556_STAT6{ENST00000300134}:r.306-4000_4034
# NAB2{ENST00000300131}:r.1_1543_STAT6{ENST00000300134}:r.306-4900_4034
# EML4{ENST00000318522}:r.1_1751+3600_ALK{ENST00000389048}:r.4080-297_6220
# EML4{ENST00000318522}:r.1_929+7320_ALK{ENST00000389048}:r.4080_6220

-----------------------------准备文件-------------------------------------
'Translocation_Name.tsv'
'Homo_sapiens.GRCh37.87.chr基因外显子坐标和外显子相对位置-merged.tsv'
'VEP_strand.tsv'




"""

path = 'C:/Users/Administrator/Desktop'  # WIN10 PATH
# path = '/home/caesar/Desktop'             # Linux PATH


fc = Fileconvert(path)
time0 = time.time()


def modify_aliase(gene):  # 修正基因名字
    gene_aliase_dict = {'C15orf55': 'NUTM1', 'FAM22A': 'NUTM2A', 'FAM22B': 'NUTM2B', 'KIAA0284': 'CEP170B'}
    try:
        return gene_aliase_dict[gene]
    except KeyError:
        return gene


# 获取外显子和正负链文件信息

def get_exon_strand_dict(exonsDataFile='Homo_sapiens.GRCh37.87.chr基因外显子坐标和外显子相对位置-merged.tsv',
                         strandFile='VEP_strand.tsv'):
    exons_dict = {}
    strand_dict = {x[0]: x[2] for x in fc.tsv2list(strandFile)}

    for x in fc.tsv2list(exonsDataFile):
        key = (x[0], x[1])
        value = tuple(x[2:5] + x[6:9])
        fc.appendToDict(key=key, value=value, dic=exons_dict)
        strand_dict[x[0]] = x[5]
    return exons_dict, strand_dict


# 定义反向互补函数
def rev_comple_seq(sequence):
    Base_dict = {'A': 'T', 'G': 'C', 'T': 'A', 'C': 'G', 'a': 't', 'g': 'c', 't': 'a', 'c': 'g', 'N': 'N'}
    if sequence.isalpha():
        rev_com_seq = ''.join([Base_dict[k] for k in sequence[::-1]])
    elif sequence == '':
        rev_com_seq = ''
    else:
        rev_com_seq = "WRONG INPUT!!"
    return rev_com_seq


# 定义用pysam获取基因组序列函数
def get_genomic_seq(chromosome, startpoint, endpoint, insertion, strand, hg19):
    chro = ''.join(['chr', chromosome])
    start = int(startpoint) - 1  # pysam获取序列，输入(a,b)，那么获取的序列是(a,b]，即是[a+1,b]<--即1based
    end = int(endpoint)
    if insertion.isalpha() or insertion == '':
        if strand == '+':
            genomic_sequence = ''.join([hg19.fetch(chro, start, end), insertion])
        elif strand == '-':
            genomic_sequence = ''.join([rev_comple_seq(hg19.fetch(chro, start, end)), insertion])
        else:
            genomic_sequence = 'WRONG INPUT!!'
    else:
        genomic_sequence = 'WRONG INPUT!!'
    return genomic_sequence


# 定义抓取转录本信息中的相对位置，是否延伸到内含子，是否有插入
def parse_CosmicFusion(text):
    # 解析融合基因格式，返回构成为(gene, enst, start, end, ins)的列表，代表融合mRNA上的几段序列的信息。
    re_num = '[0-9\+\-_]+'
    re_enst = '[NM0-9\._|ENST0-9]+'
    re_gene = '[{}]+'.format(string.ascii_letters + string.digits + '\-')
    re_insert = 'ins[ACTG|0-9]+'

    all_position = re.findall(r'(%s){(%s)}:r\.(%s)(%s)?' % (re_gene, re_enst, re_num, re_insert), text)
    all_parts = []
    for each in all_position:
        gene, enst = each[:2]
        # 修正基因名
        gene = modify_aliase(gene)
        if enst.startswith('NM'):
            try:
                gene, enst = gene_NMtoENST_dict[(gene, enst)]
            except KeyError:
                pass
        else:
            pass
        # enst_dict[enst] = gene
        start, end = tuple(each[2].strip('_').split('_'))
        if each[3]:
            ins = each[3].lstrip('ins')
        else:
            ins = ''

        part = (gene, enst, start, end, ins)
        all_parts.append(part)
    return all_parts


# 输入1877+10或者1999-11或者222，返回(1877,'+',10)|(1999,-,11)|(222,'',0)首尾元素均为int
def search_pos(pos):
    result = list(re.findall(r'(\d+)([+|-])?(\d+)?', pos)[0])
    result[0] = int(result[0])
    if result[2] == '':
        result[2] = 0
    else:
        result[2] = int(result[2])
    return tuple(result)


# 输入位点在mRNA上的位置信息，如1877+10，推断精确染色体坐标
def get_abs_pos(mRNA_pos, exonsdata, strand):
    """
    输入位点在mRNA上的位置信息，如1877+10，推断精确染色体坐标
    :param mRNA_pos: 1877+10或者1999-11或者222
    :param exonsdata: 该转录本所有外显子信息
    :param strand: 正负链
    :return:
    """
    relpos, mid, move_len = search_pos(mRNA_pos)
    if mid == '+':
        move_dir = 1
    elif mid == '-':
        move_dir = -1
    else:
        move_dir = 0

    for exon_info in exonsdata:
        chro_start, chro_stop, exon_num, exon_start, exon_stop = tuple(int(x) for x in exon_info[1:])
        if exon_start <= relpos <= exon_stop:
            position = int(float((exon_stop - exon_start) + (2 * relpos - exon_start - exon_stop) * strand) / 2.0) \
                       + chro_start + move_len * move_dir * strand
            return exon_info, position
    print(mRNA_pos, exonsdata, 'WRONG INPUT EXONDATA!!!')
    return 'WRONG INPUT EXONDATA!!!'


def get_seq_by_mRNA_pos(mRNA_pos, exons_dict, strand_dict, probe_length, pos_index, gene_NMtoENST_dict, hg19,
                        o_reverse=False):
    """
    # 计算探针序列末端时需要，探针序列末端=断裂点+长度*正负链｛+：1，-：-1｝*由断裂点起始的探针末端延伸方向｛5'端断裂点:-1,3'端断裂点：1｝
    # 哪一端的断裂点判断 取决于融合基因解析后的index，解析后有3个元素，则中间的按照插入序列获取,pos_index 0 代表5‘端，其余3‘端，999代表计算插入序列
    :param RNA_pos: (gene, enst, start, end, insertion)
    :param exons_dict:{(gene,enst):[(a,b,exon_num)]}
    :param strand_dict:
    :param reverse:
    :return:
    """
    # 计算探针序列末端时需要，探针序列末端=断裂点+长度*正负链｛+：1，-：-1｝*由断裂点起始的探针末端延伸方向｛5'端断裂点:-1,3'端断裂点：1｝
    # 哪一端的断裂点判断 取决于融合基因解析后的index，解析后有3个元素，则中间的按照插入序列获取,pos_index 0 代表5‘端，其余3‘端，999代表计算插入序列
    pos_index_value_dict = {0: -1, 2: 1, -1: 1, 1: 1, 999: 999}
    strand_value_dict = {'+': 1, '-': -1}
    gene, enst, mRNA_start, mRNA_end, insertion = mRNA_pos

    if gene.startswith('o'):
        rev_dict = {'+': '-', '-': '+', 1: -1, -1: 1}
        o_reverse = True
        strand = strand_dict[gene[1:]]
        gene = gene[1:]
    else:
        # 修正基因名后尚未发现无正负链信息的情况
        strand = strand_dict[gene]

    strand_value = strand_value_dict[strand]

    # 获取该转录本的所有外显子信息
    try:
        exonsdata = exons_dict[(gene, enst)]
    except KeyError:
        try:
            exonsdata = exons_dict[gene_NMtoENST_dict[(gene, enst)]]
        except KeyError:
            # print((gene, enst), '无可获取转录本')
            return ['NONE'] * 3
    # 根据索引判断是5'还是3'端的序列，5'端则选择mRNA_end坐标计算，3'端则选择mRNA_start坐标计算。中间序列则计算两端然后获取序列。
    if pos_index == 0:

        breakpoint_exon_info, breakpoint_pos = get_abs_pos(mRNA_pos=mRNA_end, exonsdata=exonsdata, strand=strand_value)
    elif pos_index != 999:
        breakpoint_exon_info, breakpoint_pos = get_abs_pos(mRNA_pos=mRNA_start, exonsdata=exonsdata,
                                                           strand=strand_value)
    else:
        exon_info_start, mRNA_start_abs_pos = get_abs_pos(mRNA_pos=mRNA_start, exonsdata=exonsdata, strand=strand_value)
        exon_info_end, mRNA_end_abs_pos = get_abs_pos(mRNA_pos=mRNA_end, exonsdata=exonsdata, strand=strand_value)

        chro = exon_info_start[0]
        startpoint = min(mRNA_start_abs_pos, mRNA_end_abs_pos)
        endpoint = max(mRNA_start_abs_pos, mRNA_end_abs_pos)
        insert_seq = get_genomic_seq(chromosome=chro, startpoint=startpoint, endpoint=endpoint, insertion=insertion,
                                     strand=strand, hg19=hg19)
        if o_reverse:
            insert_seq = rev_comple_seq(insert_seq)
        return insert_seq

    probe_end_pos = breakpoint_pos + strand_value_dict[strand] * pos_index_value_dict[pos_index] * probe_length

    return ([gene, enst] + list(breakpoint_exon_info) + [strand, mRNA_start, mRNA_end, insertion, breakpoint_pos,
                                                         probe_end_pos])


def get_seq_by_breakpoint(breakpoint):
    gene, enst, chromosome, start, stop, exon_number, exon_start, exon_stop, strand, mRNA_start, mRNA_end, insertion, breakpoint_pos, probe_end_pos = breakpoint
    seq = get_genomic_seq(chromosome=chromosome, startpoint=min(breakpoint_pos, probe_end_pos),
                          endpoint=max(breakpoint_pos, probe_end_pos), insertion=insertion, strand=strand, hg19=hg19)
    return seq


def findAllseq(all_fusion, exception_enst_union, gene_NMtoENST_dict, output):
    exons_dict, strand_dict = get_exon_strand_dict()
    for text in all_fusion:
        test = parse_CosmicFusion(text=text)
        gene_enst_union = {(x[0], x[1]) for x in test}
        # 确认（基因，转录本）不属于例外后，获取序列
        if gene_enst_union & exception_enst_union:
            continue
        else:
            if len(test) == 3:  # 将中间部分作为插入序列处理
                insert_seq = get_seq_by_mRNA_pos(mRNA_pos=test[1], exons_dict=exons_dict, strand_dict=strand_dict,
                                                 gene_NMtoENST_dict=gene_NMtoENST_dict, hg19=hg19, probe_length=150,
                                                 pos_index=999)
                test0_uptdate = list(test[0])
                test0_uptdate[4] += insert_seq
                test = [tuple(test0_uptdate), test[2]]

            all_parts = [get_seq_by_mRNA_pos(mRNA_pos=test[i], exons_dict=exons_dict, strand_dict=strand_dict,
                                             gene_NMtoENST_dict=gene_NMtoENST_dict, hg19=hg19, probe_length=150,
                                             pos_index=i)
                                            for i in range(len(test))]

            leftSeq = get_seq_by_breakpoint(all_parts[0])
            rightSeq = get_seq_by_breakpoint(all_parts[1])
            genomicSeq = ''.join((leftSeq, rightSeq))
            probeSeq = rev_comple_seq((genomicSeq))
            # 写入输出文件
            line = list(all_parts[0]) + list(all_parts[1]) + [text, genomicSeq, leftSeq, rightSeq, probeSeq]
            output.write(fc.tsvline(line))
            print(text, 'Done!!')


# hg19序列文件
hg19 = pysam.FastaFile('hg19.fa')

# 融合位点来源文件
all_fusion = [x[0] for x in fc.tsv2list(filename='Translocation_Name.tsv')]

# 输出文件
output = open('Translocation_breakpoint_seq.tsv', 'w', encoding='utf-8')
title = ['gene_A', 'enst_A', 'chromosome_A', 'start_A', 'stop_A', 'exon_number_A', 'exon_start_A', 'exon_stop_A',
         'strand_A', 'mRNA_start_A', 'mRNA_end_A', 'insertion_A', 'breakpoint_pos_A', 'probe_end_pos_A',
         'gene_B', 'enst_B', 'chromosome_B', 'start_B', 'stop_B', 'exon_number_B', 'exon_start_B', 'exon_stop_B',
         'strand_B', 'mRNA_start_B', 'mRNA_end_B', 'insertion_B', 'breakpoint_pos_B', 'probe_end_pos_B',
         'fusion_name', 'GenomicSeq', 'LeftSeq', 'RightSeq', 'ProbeSeq']
output.write(fc.tsvline(title))

# 排除的基因转录本
exception_enst_union = {('ARFIP1', 'NM_014447.2'), ('ARID1A', 'NM_006015.3'), ('FBXL18', 'NM_024963.2'),
                        ('FHDC1', 'NM_033393.2'), ('HAS2', 'NM_005328.1'), ('NUP107', 'NM_020401.1'),
                        ('PAX8', 'NM_003466.2'), ('PPARG', 'NM_015869.2'), ('SSX2', 'NM_003147.4'),
                        ('WT1', 'NM_024426.2'),  # 以上版本太旧

                        ('FLI1', 'ENST00000429175'), ('KIAA1549', 'ENST00000242365'),
                        ('NFIB', 'ENST00000397581'), ('KTN1', 'ENST00000395309'), ('NFIX', 'ENST00000360105'),
                        ('CIC', 'ENST00000160740'), ('DUX4', 'ENST00000556625'), ('CXorf67', 'ENST00000342995'),
                        ('ZCCHC8', 'ENST00000336229'), ('CASP8AP2', 'ENST00000551025'), ('CT45A2', 'ENST00000612907'),
                        ('RBMS1', 'ENST00000392753'), ('NFIA', 'ENST00000485903'), ('FBXO38', 'ENST00000340253'),
                        # 以上找不到转录本

                        ('CUTA', 'ENST00000440279')  # 转录本长度不一致
                        }

# 需要替换转录本的基因
gene_NMtoENST_dict = {('ALK', 'NM_004304'): ('ALK', 'ENST00000389048'),  # ALK
                      ('FGFR3', 'NM_000142'): ('FGFR3', 'ENST00000440486'),  # FGFR3
                      ('ROS1', 'NM_002944'): ('ROS1', 'ENST00000368508'),  # ROS1
                      ('KMT2A', 'NM_005933.1'): ('KMT2A', 'ENST00000389506'),  # KMT2A
                      # 'NM_014447.2': 'ENST00000405727', ARFIP1版本太旧且不值得获取序列
                      # 'NM_006015.3': 'ENST00000324856', ARID1A版本太旧且不值得获取序列
                      # 'NM_024963.2': 'ENST00000382368', FBXL18版本太旧且不值得获取序列
                      # 'NM_033393.2': 'ENST00000260008', FHDC1版本太旧且不值得获取序列
                      # 'NM_005328.1': 'ENST00000303924', HAS2版本太旧且不值得获取序列
                      # 'NM_020401.1': 'ENST00000229179', NUP107版本太旧且不值得获取序列
                      # 'NM_003466.2': 'ENST00000429538', PAX8这俩以后再计算
                      # 'NM_015869.2': 'ENST00000287820', PPARG这俩以后再计算
                      # 'NM_020975': 'ENST00000355710', RET转录本不一致，故需要手工新增NM_020975.4
                      # 'NM_003147.4': 'ENST00000336777', SSX2以后再计算
                      # 'NM_024426.2': 'ENST00000332351', WT1以后再计算
                      }

findAllseq(all_fusion=all_fusion, exception_enst_union=exception_enst_union, gene_NMtoENST_dict=gene_NMtoENST_dict,
           output=output)

time1 = time.time()
print('当前运行耗时{}秒'.format(time1 - time0))
