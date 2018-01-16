import os
import time
import re
start_time = time.time()
filename = 'nightly-ClinicalEvidenceSummaries'
exon_file = 'Homo_sapiens.GRCh37.75_基因外显子坐标'
path = 'C://Users/Administrator/Desktop' #win10 path
#path = '/home/caesar/Desktop'
os.chdir(path)
print(os.getcwd())
mutation_exon_list = []
exon_data_list = []
trans_ID_list = []
joinlist = []
final_list = []
mutation_No_repeat = []
#列表去重函数
def remove_repeat(listname):
    if isinstance(listname,list):
        blank = []
        for i in listname:
            while listname.count(i)>=1 and not i in blank and i != '':
                blank.append(i)
    return blank


#summary_info为突变数据来源
#exon_info为外显子坐标数据来源

summary_info = open('%s.tsv' % filename, 'r',encoding="utf-8")    #打开ClVic数据文件
text = summary_info.read()                                        #作为字符串读取
search_word = re.compile(r'ENST\d{11}')                           #然后用正则表达式搜索所有转录本
trans_ID_list = list(set(search_word.findall(text)))              #并通过集合形成无重复列表

exon_info = open('%s.tsv' % exon_file, 'r',encoding="utf-8")      #打开外显子坐标数据来源
exon_info.readline()                                              #跳过第一行
for each_exon_line in exon_info:                                  #分割成列表后筛选存在于上一步集合中的转录本条目并集结成列表
    each_exon_line = each_exon_line[:-1].split()
    if each_exon_line[1] in trans_ID_list:
        exon_data_list.append(each_exon_line)

summary_info = open('%s.tsv' % filename, 'r',encoding="utf-8")    #对于每个突变遍历筛选出的外显子列表，通过比较得到外显子所在位置
summary_info.readline()                                           #跳过第一行后，截取突变坐标和外显子坐标列表比对，符合则写入新的突变信息汇总列表
for i in summary_info:
    i=i[:-1].split("\t")
    trans_ID = i[23][0:15]
    if i[19] != '':
        mutation_start = int(i[19])
        mutation_stop  = int(i[20])
        for exon_data_line in exon_data_list:
            if trans_ID == exon_data_line[1]:
                exon_start = int(exon_data_line[3])
                exon_stop = int(exon_data_line[4])
                if exon_start<=mutation_start <= mutation_stop<=exon_stop:
                    mutation_detail = exon_data_line+i[2:4]+i[8:12]+i[19:21]+i[30:32]
                    if not mutation_detail in mutation_exon_list:
                        mutation_exon_list.append(mutation_detail)


#对于筛选出来的突变所在外显子坐标，去掉重复项
mutation_selected_exon = []
for j in mutation_exon_list:
    if not j[0:8] in mutation_selected_exon:
        mutation_selected_exon.append(j[0:8])
    else:
        pass
        
        
#对每个去重之后的突变所在外显子坐标，遍历突变信息汇总列表
for n in mutation_selected_exon:
    mutation = []
    disease = []
    evidence_level = []
    clinical_significance = []
    evidence_statement = []
    pubmed_id = []
    mutation_start = []
    mutation_stop = []
    variant_summary = []
    mutation_type = []
    
    #将符合外显子坐标的所有选项都找出来，并且合并同类项
    for m in mutation_exon_list:
        if n == m[0:8]:
            mutation.append(m[8])
            disease.append(m[9])
            evidence_level.append(m[10])
            clinical_significance.append(m[11])
            evidence_statement.append(m[12])
            pubmed_id.append(m[13])
            mutation_start.append(int(m[14]))
            mutation_stop.append(int(m[15]))
            variant_summary.append(m[16])
            mutation_type.append(m[17])
    mutation = remove_repeat(mutation)
    disease = remove_repeat(disease)
    evidence_level = remove_repeat(evidence_level)
    clinical_significance = remove_repeat(clinical_significance)
    evidence_statement = remove_repeat(evidence_statement)
    pubmed_id = remove_repeat(pubmed_id)
    mutation_start = remove_repeat(mutation_start)
    mutation_stop = remove_repeat(mutation_stop)
    variant_summary = remove_repeat(variant_summary)
    mutation_type = remove_repeat(mutation_type)
    
    #合并证据级别等同类项
    mutation = ";".join(mutation)
    disease = ";".join(disease)
    evidence_level = ";".join(evidence_level)
    clinical_significance = ";".join(clinical_significance)
    evidence_statement = "------".join(evidence_statement)
    pubmed_id = ";".join(pubmed_id)
    mutation_start = str(min(mutation_start))
    mutation_stop = str(max(mutation_stop))
    variant_summary = "------".join(variant_summary)
    mutation_type = ";".join(mutation_type)
    
    #整合合并后的信息
    information = [mutation,disease,evidence_level,clinical_significance,evidence_statement,pubmed_id,mutation_start,mutation_stop,variant_summary,mutation_type]
    mutation_No_repeat.append(n+information)
    
    
#添加表头
title = ['Gene','Transcript','chromosome','exon_start','exon_stop','exon','number','strand','mutation','disease','evidence_level','clinical_significance','evidence_statement','pubmed_id','mutation_start','mutation_stop','variant_summary','mutation_type']
mutation_No_repeat.insert(0,title)
#以制表符整合每个元素
for k in mutation_No_repeat:
    k = "\t".join(k)
    joinlist.append(k)
# 以换行符整合列表为字符串
final_list = "\n".join(joinlist)
outfile = open('%sselected-exon-information-splited-and-merged.tsv'%filename, 'w',encoding="utf-8")
outfile.write(final_list)
outfile.close()
stop_time = time.time()
print('运行成功，耗时为：%a秒'%(stop_time-start_time))
