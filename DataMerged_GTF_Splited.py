import os
import time
from Fileconvert import Fileconvert
from pprint import pprint
import pandas as pd


class GTF(object):
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        if self.filename.startswith('gencode'):
            self.tsp_type = 'transcript_type'
            self.gtf_title_dict = {'transcript': ('gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand',
                                                  'transcript_name', 'ccdsid'),
                                   'exon': ('gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand',
                                            'exon_number', 'transcript_name', 'ccdsid'),
                                   'CDS': ('gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand',
                                           'exon_number', 'transcript_name', 'ccdsid')}
        else:
            self.tsp_type = 'transcript_biotype'
            self.gtf_title_dict = {'transcript': (
                'gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand', 'transcript_name', 'ccds_id'),
                'exon': ('gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand',
                         'exon_number', 'transcript_name', 'ccds_id'),
                'CDS': ('gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand',
                        'exon_number', 'transcript_name', 'ccds_id')}
        os.chdir(path=self.path)

    def line2dict_gtf(self, line):
        """
        以 gene_id "ENSG00000228463"; gene_version "10"; transcript_id "ENST00000441866"; transcript_version "2"; exon_number "1"; gene_name "AP006222.1"
        为例，内容均为 (str1 "str2";)n,以此创建字典，{str1：str2}
        :param line: 字符串 格式为 (\w+ "\w+";)*n
        :return:字典
        """
        dic = {}
        for x in line.replace('"', '').split(';'):
            if x:
                (key, value) = tuple(x.strip().split(' ', 1))
                try:
                    if dic[key]:
                        old_value = dic[key]
                        dic[key] = '|'.join([old_value, value])
                except KeyError:
                    dic[key] = value
        return dic


    def map_dict(self, keylist, dict):
        """
        根据字典获取一个列表各元素为键后对应的值，生成值的元组输出，不存在的键以空字符串输出
        :param keylist: 键的列表
        :param dict: 字典
        :return: 值的元组
        """
        plus = []
        for key in keylist:
            try:
                plus.append(dict[key])
            except KeyError:
                plus.append('')
        return tuple(plus)


    def condition(self, line_dict, feature_type, chromosome=None, start=None, stop=None, strand=None, gene_name=None,
                  gene_id=None,transcript_id=None, exon_number=None, transcript_name=None, ccdsid=None, tag=None):
        keylist = (chromosome, start, stop, strand, gene_name, gene_id, transcript_id, exon_number, transcript_name,
                   ccdsid, tag)
        title = ('chromosome', 'start', 'stop', 'strand', 'gene_name', 'gene_id', 'transcript_id', 'exon_number',
                 'transcript_name', 'ccdsid', 'tag')
        t_dict = dict(zip(title, keylist))
        key_dict = {x: y for x, y in t_dict.items() if y in set(self.gtf_title_dict[feature_type])}

        if 'CCDS' in line_dict['tag'] and 'appris' in line_dict['tag'] and 'NF' not in line_dict['tag']:
            pass

        return

    def gtf2tsv(self):
        # 转化相应的行至tsv
        # 筛选行进行输出的过滤条件是 'transcript_biotype' == 'protein_coding'; ‘feature_type’ in 'transcript','exon','CDS'
        fc = Fileconvert(self.path)
        file = open('{}.gtf'.format(self.filename), 'r', encoding='utf-8')
        print(self.filename, '开始')
        tag_dict = set()
        for x in file:
            if x.startswith('#'):
                continue
            else:
                line = x.strip().split('\t')
                chrom, source, feature_type, start, stop, score, strand, phase, annotation = tuple(line)
                if feature_type in {'transcript', 'exon', 'CDS'}:
                    line_dict = dict(chromosome=chrom.strip('chr'), start=start, stop=stop, strand=strand)
                    line_dict.update(self.line2dict_gtf(annotation))
                    # 过滤条件
                    if line_dict[self.tsp_type] == 'protein_coding' and 'CCDS' in line_dict['tag'] and 'basic' in \
                            line_dict['tag'] and 'NF' not in line_dict['tag']:
                        line_dict['transcript_id'] = line_dict['transcript_id'].split('.')[0]
                        title = self.gtf_title_dict[feature_type]
                        tag_dict.add(line_dict['tag'])

                        plus = fc.tsvline(self.map_dict(title, line_dict))
                        newFileName = '{}_{}.tsv'.format(self.filename, feature_type)
                        if os.path.isfile(newFileName):
                            out = open(newFileName, 'a', encoding='utf-8')
                            out.write(plus)
                        else:
                            out = open(newFileName, 'a', encoding='utf-8')
                            out.write(fc.tsvline(title))
                            out.write(plus)
        print(tag_dict)

    def operate_exon_data_line(self, line, start, stop, last_exon_stop, exon_start, exon_start_num, is_cds=True):
        """
        输入生成的gtf一行数据，计算相对cds位置或者转录本位置
        :param line: 输入的一行exon或cds的信息
        :param start: exon的开始坐标
        :param stop: exon的开始坐标
        :param last_exon_stop: 上一行的外显子右端相对位置
        :param exon_start: 这个外显子的左端相对位置
        :param exon_start_num: 外显子左端的index
        :param is_cds: 是否为cds
        :return: 输出插入exon或者cds相对位置计算结果的行
        """
        exon_stop = int(stop) - int(start) + int(last_exon_stop) + 1
        this_exon_start = str(exon_start)
        this_exon_stop = str(exon_stop)
        if is_cds:
            this_aa_start = self.calcu_aa_num(exon_start, is_start=True)
            this_aa_stop = self.calcu_aa_num(exon_stop, is_start=False)
            return line[:exon_start_num] + [this_exon_start, this_exon_stop] + line[exon_start_num:] + [this_aa_start,
                                                                                                        this_aa_stop]
        else:
            return line[:exon_start_num] + [this_exon_start, this_exon_stop] + line[exon_start_num:]

    # 插入两列
    def insert_start_stop(self, exon_line, exon_start, exon_stop, exon_start_num=7, exon_stop_num=8, is_cds=True,
                          aa_start_num=11, aa_stop_num=12):
        exon_line.insert(exon_start_num, exon_start)
        exon_line.insert(exon_stop_num, exon_stop)
        if is_cds:
            exon_line.insert(aa_start_num, self.calcu_aa_num(int(exon_start), is_start=True))
            exon_line.insert(aa_stop_num, self.calcu_aa_num(int(exon_stop), is_start=False))

    def calcu_aa_num(self, base_site, is_start=True):
        """
        根据cds碱基位置计算相应氨基酸位置，外显子右端被3整除时的商，不考虑余数；左端被整除时按商来，不能整除时按商+1
        :param base_site: cds碱基位置
        :param is_start: 是否在外显子左端
        :return: AA的序数，int
        """
        if isinstance(base_site, int):
            if is_start:
                if base_site % 3 == 0:
                    return base_site // 3
                else:
                    return base_site // 3 + 1
            else:
                return base_site // 3
        else:
            try:
                num = int(base_site)
                return self.calcu_aa_num(base_site=num, is_start=is_start)
            except ValueError:
                raise TypeError('base_site必须是整数')

    # 计算每个外显子相对于转录本或者CDS的位置
    def calcuExons(self, exons_data, start_num, stop_num, exon_num, tsp_id, is_cds=True):
        """
        计算每个外显子相对于转录本或者CDS的位置
        :param exons_data: 读取的整张外显子信息表格
        :param start_num: 外显子起始坐标信息列
        :param stop_num: 外显子终止坐标信息列
        :param exon_num: 外显子序号所在列
        :param tsp_id: 转录本号所在列
        :return: 完成末尾追加信息后的列
        """
        fc = Fileconvert(path=self.path)
        first_line = exons_data[0]
        exons_data[0][tsp_id] = first_line[tsp_id].split('.')[0]

        exon_stop = str(int(first_line[stop_num]) - int(first_line[start_num]) + 1)
        exon_start = '1'
        self.insert_start_stop(exon_line=exons_data[0],
                               exon_start=exon_start, exon_stop=exon_stop,
                               exon_start_num=exon_num + 1, exon_stop_num=exon_num + 2,
                               is_cds=is_cds, aa_start_num=exon_num + 5, aa_stop_num=exon_num + 6)
        last_line = exons_data[0]
        i = 1
        while 0 < i <= len(exons_data) - 1:
            this_line = exons_data[i]
            start, stop, this_exon_num, this_enst = fc.simple_select_iter(
                loci_list=(start_num, stop_num, exon_num, tsp_id), iter=this_line)
            last_exon_stop, last_exon_num, last_enst = fc.simple_select_iter(loci_list=(exon_num + 2, exon_num, tsp_id),
                                                                             iter=last_line)
            # 若和上一条的ENST不一样,则重新开始计数；一样则利用上一条的数据计算exon的起止
            this_enst = exons_data[i][tsp_id] = this_enst.split('.')[0]
            if this_enst != last_enst:
                exon_start, last_exon_stop = 1, 0
            elif int(this_exon_num) > int(last_exon_num) and this_enst == last_enst:
                exon_start = int(last_exon_stop) + 1
            else:
                # 默认已经排好序 以防万一
                print('Error: 发生在第{}行'.format(i), exons_data[i])
                break

            exons_data[i] = self.operate_exon_data_line(line=this_line, start=start, stop=stop,
                                                        last_exon_stop=last_exon_stop,
                                                        exon_start=exon_start, exon_start_num=exon_num + 1,
                                                        is_cds=is_cds)
            last_line = exons_data[i]
            i += 1
        return exons_data

    # 对于已合成的外显子CDS坐标文件,计算每个外显子对应的CDS位置,并输出文件
    def calcuExons_to_file(self, source_file, target_file, is_cds=True):
        fc = Fileconvert(path=self.path)
        exons_data = fc.tsv2list(filename=source_file)
        new_exons = self.calcuExons(exons_data=exons_data, start_num=3, stop_num=4, exon_num=6, tsp_id=1, is_cds=is_cds)
        if is_cds:
            title = ['gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand', 'exon_number', 'exon_start',
                     'exon_stop', 'transcript_name', 'ccds_id', 'AA_start', 'AA_stop']
        else:
            title = ['gene_name', 'transcript_id', 'chromosome', 'start', 'stop', 'strand', 'exon_number', 'exon_start',
                     'exon_stop', 'transcript_name', 'ccds_id']
        df = pd.DataFrame(new_exons, columns=title)
        df.to_csv(target_file, sep='\t', header=True, index=None)


def gtf_split(path, filename):
    os.chdir(path=path)
    gtf = GTF(path=path, filename=filename)
    gtf.gtf2tsv()
    gtf.calcuExons_to_file('{}_CDS.tsv'.format(filename), '{}_CDS和相对位置.tsv'.format(filename), is_cds=True)
    gtf.calcuExons_to_file('{}_exon.tsv'.format(filename), '{}_exon和相对位置.tsv'.format(filename), is_cds=False)


#==================================================程序主体=============================================================
# path = '/home/caesar/Desktop' #ubuntu path
path = 'C://Users/Administrator/Desktop'  # win10 path
filename = 'Homo_sapiens.GRCh38.94.chr'


start_time = time.time()
gtf_split(path=path, filename=filename)

stop_time = time.time()
print('运行耗时为：%a秒' % (stop_time - start_time))
