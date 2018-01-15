import os
import re
import time
start_time = time.time()
path = 'C://Users/Administrator/Desktop' #win10 path
#path = '/home/caesar/Desktop' ubuntu path
os.chdir(path)
file_name = 'Homo_sapiens.GRCh37.75'
gtf_data= open('%s.gtf'%file_name, 'r',encoding="utf-8")
j = 0
gtf_list = []
joinlist = []
final_list = []
linear2_3 = ['transcript','exon']
#用读取来跳过表头
gtf_data.readline()
gtf_data.readline()
gtf_data.readline()
gtf_data.readline()
gtf_data.readline()
for linear in gtf_data:
    #跳过空行，分割每行为列表进行操作
    if linear == []:
        pass
    else:
        linear = linear.split("\t")
        #若读取的行包含蛋白编码和转录本或者exon等字样则进行切片操作
        if linear[1] == 'protein_coding' and  linear[2] in linear2_3:
            transcript_id = [re.search(r'transcript_id "(.*?)"', linear[-1]).group(1)]
            gene_name = [re.search(r'gene_name "(.*?)"', linear[-1]).group(1)]
            if linear[2] == 'exon':
                exon_number = re.search(r'exon_number "(.*?)"', linear[-1]).group(1)
                classification = [''.join(linear[2]+' '+ exon_number)]
            else:
                classification = [' ']
            chr = [linear[0]]+linear[3:5]
            strand =[linear[6]]
            vector = gene_name + transcript_id + chr + classification + strand
            gtf_list.append(vector)
title = ['gene_name','transcript_ID','chromosome','start','stop','exon','strand']
gtf_list.insert(0,title)
# 以制表符合并每个列表中的元素
for k in gtf_list:
    k = "\t".join(k)
    joinlist.append(k)
# 以换行符整合列表为字符串
final_list = "\n".join(joinlist)
outputfile = open('%s_基因外显子转录本坐标.tsv'%file_name, 'w',encoding="utf-8")
outputfile.write(final_list)
outputfile.close()
stop_time = time.time()
print('%s.tsv Done!' % file_name)
print('运行耗时为：%a秒'%(stop_time-start_time))
