import os
import re
import time
start_time = time.time()
path = 'C://Users/Administrator/Desktop' #win10 path
#path = '/home/caesar/Desktop' #ubuntu path
os.chdir(path)
file_name = 'Homo_sapiens.GRCh37.75'
#小型文件tsv转二维列表
def tsv2list (path,filename,fileformat):
    os.chdir(path)
    with open("%s.%s"%(filename,fileformat),'r',encoding= 'utf-8') as f:
        f.readline()
        list_genename = []
        for i in f:
            if '\t' in i:
                i = i.rstrip('\n').split('\t')
            else:
                i = [i.rstrip('\n')]
            list_genename.append(i)
    return list_genename

#二维列表转tsv输出
def list2tsv (path,inputlist,filename,fileformat):
    finallist = '\n'.join(['\t'.join(i) for i in inputlist])
    os.chdir(path)
    with open('%s-merged.%s'%(filename,fileformat),'w',encoding= 'utf-8') as f:
        f.write(finallist)
        f.close()

#字符串转为字典,以获取简便索引
def createdict(string):
    return {i[0]:i[1] for i in list(enumerate(string.strip().split('\t')))}
#默认0 为蛋白编码基因
genetype = '''protein_coding	miRNA	lincRNA	snRNA	antisense	misc_RNA	snoRNA	rRNA	pseudogene	processed_transcript	transcribed_unprocessed_pseudogene	unprocessed_pseudogene	processed_pseudogene	transcribed_processed_pseudogene	unitary_pseudogene	polymorphic_pseudogene	sense_overlapping	sense_intronic	3prime_overlapping_ncrna	retained_intron	nonsense_mediated_decay	non_stop_decay	IG_V_gene	IG_C_gene	IG_J_gene	IG_V_pseudogene	TR_C_gene	TR_J_gene	TR_V_gene	TR_V_pseudogene'''
GenetypeDict = createdict(genetype)

#默认基因 转录本 外显子 CDS 对应 0 1 2 3
location = '''gene	transcript	exon	CDS	start_codon	stop_codon	UTR	Selenocysteine'''
LocationDict = createdict(location)

#默认抽取元素对应的id代码 转录本 外显子数 基因名 基因id(ENSG) 转录本名字 ccds id  蛋白ID ENSP 分别对应 0 1 2 3 4 5 6
element = '''transcript_id	exon_number	gene_name	gene_id	transcript_name	ccds_id	protein_id'''
ElementDict = createdict(element)

combination = [['基因转录本坐标',['protein_coding', 'transcript'], [2,0,3,4,5]],          #定义各种参数,截取信息的位置
               ['基因外显子坐标',['protein_coding', 'exon'],[2,0,1]],
               ['基因仅含CDS外显子坐标',['protein_coding','CDS'],[2,0,1]]]
primarytile = ['gene_name','transcript_ID','chromosome','start','stop','strand','exon','gene_id', 'transcript_name', 'ccds_id']  #最原始的表头
#—————————————————————————————————————个程序最核心的选择query————————————————————————————————————————————————————

query = combination[1]
suffix = query[0]; infotype = query[1]; elementlist = query[2]  #文件名后缀 基因+位置类型 获取的其他id信息位置

#创建对于GTF文件用正则表达式截取所需数据的函数
#元素列表elementlist规定了用怎样的正则表达式截取元素,以及截取的顺序
def gtfdata(linear, elementlist, GeneType=infotype[0], Location=infotype[1]):
    # 跳过空行，分割每行为列表进行操作
    if linear != []:
        line = linear.strip().split("\t")
        if line[1] == GeneType and line[2] == Location:         # 若读取的行包含蛋白编码和转录本或者exon等字样则进行切片操作
            vector = [findElement(i, ElementDict, line[-1]) for i in elementlist]
            if 'WRONG INPUT!!' not in vector:
                chr = [line[0]] + line[3:5]; strand = [line[6]]  # 染色体坐标
                vector= vector[0:2] + chr + strand + vector[2:]
                return vector

#定义自定义格式的搜索函数,这里必须用s%占位,直接输入字符串不行
def findElement(num,dict,line):
    keyword =dict[num] +' "(.*?)";'                 #正则表达式的搜索公式
    if re.search(r'%s'%keyword,line) != None:
        return re.search(keyword,line).group(1)
    else:
        return 'WRONG INPUT!!'

#————————————————————————————————————————程序主体——————————————————————————————————————
title = [ElementDict[2],ElementDict[0]]+['chromosome','start','stop','strand']+[ElementDict[i] for i in elementlist[2:]]    #表头生成

gtf_data= open('%s.gtf'%file_name, 'r',encoding="utf-8")    #打开gtf文件
gtf_data.readline()                                         #用跳过表头
gtf_data.readline()
gtf_data.readline()
gtf_data.readline()
gtf_data.readline()

#每行进行切片操作
gtflist = [gtfdata(line ,elementlist,GeneType=infotype[0], Location=infotype[1]) for line in gtf_data if (gtfdata(line ,elementlist,GeneType=infotype[0], Location=infotype[1]) !=None)]

gtflist.insert(0,title)                                     #加表头
list2tsv(path,gtflist,file_name+query[0],fileformat='tsv')  #输出表格

stop_time = time.time()
print('%s.tsv Done!' % file_name)
print('运行耗时为：%a秒'%(stop_time-start_time))
