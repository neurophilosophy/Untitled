import os
import re
import time
start_time = time.time()
path = 'D://360安全浏览器下载/Cosmic' #win10 path
#path = '/home/caesar/Desktop' #linux path

filename = 'CosmicFusionExport'
tissue = 'lung'


#定义一个列表去重复的函数
def remove_repeat(listname):
    if isinstance(listname,list):
        blank = []
        for i in listname:
            while listname.count(i)>=1 and not i in blank and i != '':
                blank.append(i)
    return blank

#列表元素均需占一列导出TSV
def two_dimension_list_to_tsv_line(path,filename,list):
    os.chdir(path)
    joinlist = []
    for s in filtered_fusion:
        s = '\n'.join(s)
        s = s + '\n'
        joinlist.append(s)
    final_fusion_list = '\t'.join(joinlist)
    output_fusion_file = open('%s-filtered.tsv'%filename,'w',encoding='utf-8')
    output_fusion_file.write(final_fusion_list)
    output_fusion_file.close()
    return 'tranformation done!'

#列表元素均需占一行,导出TSV
def two_dimension_list_to_tsv_row(path,filename,list):
    os.chdir(path)
    joinlist = []
    for s in filtered_fusion:
        s = '\t'.join(s)
        joinlist.append(s)
    final_fusion_list = '\n'.join(joinlist)
    output_fusion_file = open('%s-filtered.tsv'%filename,'w',encoding='utf-8')
    output_fusion_file.write(final_fusion_list)
    output_fusion_file.close()
    return 'tranformation done!'

#对于已知的NM ENST ID转换创建字典
ID_dict = {'NM_004304':'ENST00000389048', 'NM_002944':'ENST00000368508','NM_020975':'ENST00000355710'}
#创建替换列表中元素函数
def replace_element_in_list(dict,list):
    for p in list:
        if p in dict:
            list[int(list.index(p))] = dict[p]


#获取融合基因partner列表，用原发部位来缩小筛选范围,同时输出符合的易位列表
def get_fusiongene_list(path,filename,tissue):
    os.chdir(path)
    fusion_data = open('%s.tsv'%filename,'r',encoding='utf-8')
    fusion_data.readline()    #跳过第一行
    fusion_partner1 = []
    fusion_partner2 = []
    Translocation_Name = []
    for i in fusion_data:
        i = i[:-1].split('\t')
        if i[2] == tissue and i[12] =='Inferred Breakpoint' :
            if i[11] != ''and '?' not in i[11]:    #跳过空行和数据不明确的条目
                if i[11] not in Translocation_Name:
                    Translocation_Name.append(i[11])
                gene_list = re.findall(r'(\w+)\.?\w*}',i[11],flags= 0) #搜索符合ID格式的字符，去重复后汇入列表
                for j in gene_list[:-1]:
                    if j not in fusion_partner1:
                        fusion_partner1.append(j)
                if gene_list[-1] not in fusion_partner2:
                    fusion_partner2.append(gene_list[-1])
            else:
                continue
    #替换NM格式为ENST格式
    for a in ID_dict:
        for b in Translocation_Name:
            Translocation_Name[int(Translocation_Name.index(b))] = b.replace(a,ID_dict[a])
    Translocation_Name = remove_repeat(Translocation_Name)
    #输出Cosmic上的融合转录本结果
    Translocation = '\n'.join(Translocation_Name)
    output_Translocation_file = open('%s-TranslocationName-filtered-Inferred Breakpoint.tsv'%filename,'w',encoding='utf-8')
    output_Translocation_file.write(Translocation)
    output_Translocation_file.close()
    return [fusion_partner1,fusion_partner2]

#单独抽取出融合基因的基因转录本名列表
filtered_fusion = get_fusiongene_list(path,filename,tissue)

for r in filtered_fusion:
    replace_element_in_list(ID_dict,r)

filtered_fusion[0].insert(0,'fusion_partner_1')
filtered_fusion[1].insert(1,'fusion_partner_2')

two_dimension_list_to_tsv_line(path,filename,filtered_fusion)
stop_time = time.time()
print('运行完成，总共耗时为%s秒'%(stop_time - start_time))