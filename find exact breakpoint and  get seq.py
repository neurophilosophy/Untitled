import os
import re
import time
import pysam
#定义tsv转二维列表
def input_2d_list(path,filename,fileformat):
    os.chdir(path)
    with open('%s.%s'%(filename,fileformat),'r',encoding='utf-8') as f:
        f.readline()
        list_location = []
        for i in f:
            i = i[:-1].split('\t')
            list_location.append(i)
    return list_location

def output_2d_list_to_tsv(list,path,filename):
    joinlist = []
    for i in list:
        i = '\t'.join(i)
        joinlist.append(i)
    finallist = '\n'.join(joinlist)
    os.chdir(path)
    with open('%s.tsv'%filename,'w',encoding='utf-8') as f:
        f.write(finallist)
        f.close()
#定义抓取转录本信息中的相对位置，是否延伸到内含子，是否有插入
def search_for_mRNA_postision(str):
    list_result1 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(1)
    list_result2 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(2)
    list_result3 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(3)
    list_result4 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(4)
    list_result5 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(5)
    return [list_result1,list_result2,list_result3,list_result4,list_result5]
#在找出来分组好的的外显子坐标里，通过融合基因的信息计算断裂点坐标，插入序列，和断裂点所在的链的方向
def breakpoint_position_by_mRNA(fusionlist,exondata,position):
    strand_dict = {'+': 1, '-': -1, 'left':1, 'right':-1}
    for i in exondata:
        strand = i[7]
        a, b, c, d, e = position[0], position[1], position[2], position[3], position[4]
        if int(i[8]) <= int(a) <= int(i[9]):
            A = int(float(i[4])+(float(i[8])-float(i[9]))/2.0+strand_dict[strand]*(float(a)*2.0-(float(i[9])+float(i[8]))/2.0))
            if c == '' and d == None:
                breakpoint = A
                insert_seq = ''
            elif c != '' and d == None:
                breakpoint = A + strand_dict[position[1]] * strand_dict[strand] * int(c)
                insert_seq = ''
            elif c != '' and d != None:
                breakpoint = A + strand_dict[position[1]] * strand_dict[strand] * int(c)
                insert_seq = e
            elif c == '' and d != None:
                breakpoint = A
                insert_seq = e
            B = breakpoint - strand_dict[strand] * strand_dict[position[5]] * 60
            probe_start = str(min(breakpoint,B))
            probe_stop = str(max(breakpoint,B))
            chromosome = i[2]
            exon = i[5]
            number = i[6]
            start = i[3]
            stop = i[4]
        else:
            continue
    return [chromosome,exon,number,start,stop,probe_start,probe_stop,insert_seq,strand]
#定义通过前面获取的信息，计算基因组上断裂点和插入的序列
def determine_breakpoint(fusionlist,datalist):
    if type(fusionlist) == list and type(datalist) == list:
        partner1_exondata = []
        partner2_exondata = []
        #对于输入的融合位点，先获取融合基因的外显子数据
        for line in datalist:
            if fusionlist[1] in line:
                partner1_exondata.append(line)
            if fusionlist[-4] in line:
                partner2_exondata.append(line)
        position1 = search_for_mRNA_postision(fusionlist[2])
        position1.append('left')
        position2 = search_for_mRNA_postision(fusionlist[-3])
        position2.append('right')
        A = breakpoint_position_by_mRNA(fusionlist,partner1_exondata,position1)
        B = breakpoint_position_by_mRNA(fusionlist,partner2_exondata,position2)
    else:
        print('INPUT ERROR!!')
    return fusionlist[0:2]+A+fusionlist[3:5]+B+[fusionlist[-1]]
#定义反向互补函数
def rev_comple_seq(sequence):
    Base_dict = {'A': 'T', 'G': 'C', 'T': 'A', 'C': 'G', 'a': 't', 'g': 'c', 't': 'a', 'c': 'g'}
    if sequence.isalpha() ==True:
        rev_seq = ''.join([Base_dict[k] for k in sequence])
        rev_com_seq = ''.join(reversed(rev_seq))
    else:
        rev_com_seq = "WRONG INPUT!!"
    return rev_com_seq

#定义获取基因组序列函数
def get_genomic_seq(chromosome, startpoint, endpoint, insertion, strand):
    chro = ''.join(['chr',chromosome])
    start = int(startpoint) - 1  # pysam获取序列，输入(a,b)，那么获取的序列是(a,b]，即是[a+1,b]
    end = int(endpoint)
    if strand == "+" and (insertion.isalpha() == True or insertion == '') :
            genomic_sequence = hg19.fetch(chro, start, end) + insertion
    elif strand == '-' and (insertion.isalpha() == True or insertion =='') :
            genomic_sequence = rev_comple_seq(hg19.fetch(chro, start, end)) + insertion
    else:
        genomic_sequence = 'WRONG INPUT!!'

    return genomic_sequence


#————————————————————————————程序主体————————————————————————————————

#获取已经筛选过的外显子坐标数据，获得二维列表
path = 'C://Users/Administrator/Desktop'
#path = '/home/caesar/Desktop'
os.chdir(path)
data_filename = 'CosmicFusionExport-Translocation-filtered_exon_location'
fusion_name = 'TranslocationName-filtered-Inferred Breakpoint'
fileformat = "tsv"

#导入外显子数据列表和融合基因数据并转化为二维列表
list_exon_location = input_2d_list(path,data_filename,fileformat)
fusion_name_data = input_2d_list(path,fusion_name,fileformat)
#导入hg19
hg19 = pysam.FastaFile('hg19.fa')

seq_location_for_probe = []
for i in fusion_name_data:
    C = determine_breakpoint(i,list_exon_location)
    leftseq = get_genomic_seq(C[2],C[7],C[8],C[9],C[10])
    rightseq = get_genomic_seq(C[13],C[18],C[19],C[20],C[21])

    genomic_seq = leftseq + rightseq
    D = C + [leftseq+rightseq] + [rev_comple_seq(genomic_seq)]
    seq_location_for_probe.append(D)
    title_text = 'Fusion_gene1	ID	chromosome	exon	number  start   stop	probe_start	probe_stop	inserted_seq	strand	Fusion_gene1	ID	chromosome	exon	number  start   stop	probe_start	probe_stop	inserted_seq	strand	fusion_name genomic_sequence    probe_seq'
title = title_text.split()
seq_location_for_probe.insert(0,title)

fusion_coordinates_name = fusion_name + ' exact_probe_coordinates'
output_2d_list_to_tsv(seq_location_for_probe,path,fusion_coordinates_name)
print('Done!!')
