import os
import time
start_time = time.time()
filename = 'nightly-ClinicalEvidenceSummaries'
exon_file = 'Homo_sapiens.GRCh37.75_基因外显子坐标'
path = 'C://Users/Administrator/Desktop' #win10 path
#path = '/home/caesar/Desktop'
os.chdir(path)
print(os.getcwd())
mutation_exon_list = []
joinlist = []
final_list = []
#summary_info为突变数据来源
#exon_info为外显子坐标数据来源
summary_info = open('%s.tsv' % filename, 'r',encoding="utf-8")
exon_info = open('%s.tsv' % exon_file, 'r',encoding="utf-8")

#跳过表头
summary_info.readline()
exon_info.readline()

#先按照换行符分割成一维列表,再将外显子坐标数据转化成多维列表
exon_text = exon_info.read()
exon_text_list = [i.split() for i in exon_text.split('\n')]

#突变数据中每一行获得转录本ID
for line in summary_info:
    line = line[:-1].split('\t')
    trans = line[23]

    #去掉转录本里小数点后面的部分
    if 'ENST' in trans and len(trans)>13:
        trans_ID = line[23][0:15]

        #突变位点坐标获取
        mutation_start = int(line[19])
        mutation_stop = int(line[20])

        #对于每个转录本，遍历外显子坐标比对获得位置信息
        for exon_line in exon_text_list:
            if trans_ID == exon_line[1]:
                exon_start = int(exon_line[3])
                exon_stop = int(exon_line[4])
                if exon_start<=mutation_start and mutation_stop<=exon_stop :
                    mutation_detail = exon_line+line[2:4]+[line[8]]+line[19:21]
                    if not mutation_detail in mutation_exon_list:
                        mutation_exon_list.append(mutation_detail)
                    break
title = ['Gene','Transcript','chromosome','exon_start','exon_stop','exon','number','strand','mutation','disease','evidence_level','mutation_start','mutation_stop']
mutation_exon_list.insert(0,title)
for k in mutation_exon_list:
    k = "\t".join(k)
    joinlist.append(k)
    # 以换行符整合列表为字符串
final_list = "\n".join(joinlist)
outfile = open('%s-exon-splited.tsv'%filename, 'w',encoding="utf-8")
outfile.write(final_list)
outfile.close()
stop_time = time.time()
print('运行耗时为：%a秒'%(stop_time-start_time))
