# -*- coding: utf-8 -*-
import pysam
import os
import time
start_time = time.time()
path = "/home/caesar/Desktop"
os.chdir(path)
#打开外显子CDS坐标文件，并通过转录本过滤出需要查找的基因的所有外显子
gene_data_file_name = 'Homo_sapiens.GRCh37.75_基因仅含CDS外显子坐标'
gene_data = open('%s.tsv' %gene_data_file_name,'r',encoding="utf-8")
gene_data.readline()
hg19 = pysam.FastaFile('hg19.fa')
Base_dict = {'A':'T','G':'C','T':'A','C':'G','a':'t','g':'c','t':'a','c':'g'}
#定义反向互补函数
def rev_comple_seq(sequence):
    rev_seq = ''.join([Base_dict[k] for k in sequence])
    rev_com_seq = ''.join(reversed(rev_seq))
    return (rev_com_seq)

#定义获取基因组序列函数
def get_genomic_seq(chromosome, startpoint, endpoint, strand):
    chro = ''.join(['chr',chromosome])
    start = int(startpoint) - 1  # pysam获取序列，输入(a,b)，那么获取的序列是(a,b]，即是[a+1,b]
    end = int(endpoint)
    if strand == "+" :
            genomic_sequence = hg19.fetch(chro, start, end)
    elif strand == '-' :
            genomic_sequence = rev_comple_seq(hg19.fetch(chro, start, end))
    else:
        pass
    return genomic_sequence

gene_sequence = []
for i in  gene_data:
    i = i[:-1].split('\t')
    exon_sequence = get_genomic_seq(i[2],i[3],i[4],i[6])
    gene_sequence.append(exon_sequence)

gene_cds = ''.join(gene_sequence)
print(gene_cds)


words = '序列转换完成！'
stop_time = time.time()
time_comsumption = stop_time-start_time
print('%s'%words)
print('总共耗时为%a秒'%time_comsumption)
