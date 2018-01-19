import os
import re
import time
#引入去重复函数
def removed_repeated(listname2):
    blank =[]
    for i in listname2:
        if i !='' and i not in blank:
            blank.append(i)
    return blank

#引入获取转录本相对位置函数
def get_mRNA_range(listname):       #同一转录本内计算
    if type(listname) == list:
        listname.sort(key=lambda x:int(x[6]))#按照外显子序号排序
        if listname[0][7] == '+' or listname[0][7] == '-' :
            a=0
            b=0
            for i in range(0,len(listname)):
                a,b = b+1,b+int(listname[i][4])-int(listname[i][3])+1
                listname[i].append(str(a))
                listname[i].append(str(b))
        else:
            print('list ERROR!!')
    return listname
#从以过滤出来的融合基因转录本里抽取需要获得外显子坐标的转录本
filename = 'CosmicFusionExport-Translocation-filtered'
path = 'D://360安全浏览器下载/Cosmic'
os.chdir(path)
with open('%s.tsv'%filename,'r',encoding='utf-8') as f:
    f.readline()
    text = f.read()
    results = re.findall(r'(ENST\d+)',text)

print(removed_repeated(results))
list_results = removed_repeated(results)

os.chdir('C://Users/Administrator/Desktop')
#选用非CDS的外显子坐标因为cosmic数据中融合的转录本坐标均以转录本序列而不是CDS来计算
#抽取出需要计算的转录本外显子坐标信息，形成二维列表
with open('Homo_sapiens.GRCh37.75_基因外显子坐标.tsv','r',encoding='utf-8') as f2:
    f2.readline()
    list_exon_data = []
    list_selected_gene_exon = []
    for line in f2:
        line = line[:-1].split()
        if line[1] in list_results:
            list_exon_data.append(line)
#对每一个需要计算的转录本，从上一步二维列表中抽取出该转录本的项，排序后计算位置
for j in list_results:
    list_selected_gene =[]
    for i in list_exon_data:
        if i == []:
            continue
        else:
            if i[1] == j :
                list_selected_gene.append(i)
    find_mRNA_range = get_mRNA_range(list_selected_gene)
    for line in find_mRNA_range:
        list_selected_gene_exon.append(line)
print(list_selected_gene_exon)


title = ['gene_name','transcript_ID','chromosome','start','stop','exon','number','strand','mRNA_position_start','mRNA_position_stop']

list_selected_gene_exon.insert(0,title)
intermediatelist = []
for j in list_selected_gene_exon:
    j='\t'.join(j)
    intermediatelist.append(j)
list_final = '\n'.join(intermediatelist)
with open('%s_exon_location.tsv'%filename,'w',encoding= 'utf-8') as f_list:
    f_list.write(list_final)
    f_list.close()
print('Done!')
