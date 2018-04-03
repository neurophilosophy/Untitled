# -*- coding: UTF-8 -*-
import os
import time

time0 = time.time()

#字符串写入vcf文件
def str2vcf(chromosome,text):
    with open('CosmicCodingMuts-chro%s.%s'%(chromosome,'vcf'),'w',encoding= 'utf-8') as f:
        f.write(text)
        f.close()
        
path = 'C://Users/Administrator/Desktop' #WIN10 PATH
os.chdir(path)

chro = [str(i+1) for i in range(22)] + ['X'] + ['Y'] + ['MT']

#输入表头
header ='''##fileformat=VCFv4.1
##source=COSMICv84
##reference=GRCh38
##fileDate=20180213
##comment="Missing nucleotide details indicate ambiguity during curation process"
##comment="URL stub for COSM ID field (use numeric portion of ID)='http://cancer.sanger.ac.uk/cosmic/mutation/overview?id='"
##comment="REF and ALT sequences are both forward strand
##INFO=<ID=GENE,Number=1,Type=String,Description="Gene name">
##INFO=<ID=STRAND,Number=1,Type=String,Description="Gene strand">
##INFO=<ID=CDS,Number=1,Type=String,Description="CDS annotation">
##INFO=<ID=AA,Number=1,Type=String,Description="Peptide annotation">
##INFO=<ID=CNT,Number=1,Type=Integer,Description="How many samples have this mutation">
##INFO=<ID=SNP,Number=0,Type=Flag,Description="classified as SNP">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
'''

name = locals()
for x in chro:                           #利用locals函数批量创建变量
    name['chro%s'%x] = [header]

with open('CosmicCodingMuts.vcf','r',encoding='utf-8') as vcf:
    for i in range(14):
        vcf.readline()                  #跳过表头
    for x in vcf:
        head = x.split('\t')[0]        #按分割后第一个元素判断染色体
        if head in chro:                #属于[1-22,X,Y,MT]的直接在对应的变量后面加上这一行字符串
            name['chro%s' % head].append(x)
        else:
            print(x)
    for y in chro:                      #按照染色体分别输出文件
        name['chro%s' % y] = ''.join(name['chro%s' % y])
        str2vcf(y,name['chro%s' % y])

time1 = time.time()
print("运行总共耗时为%a秒"%(time1-time0))
