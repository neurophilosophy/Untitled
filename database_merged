import os
import time
import re

time0 = time.time()
OncoKB_annotated = 'allAnnotatedVariants'
OncoKB_actionable = 'allActionableVariants'
ckb_NSCLC = 'CKB Variant 介绍'
civic_gene = 'nightly-GeneSummaries'
outputfile = 'OncoKB'
fileformat ='tsv'
txt = 'txt'
CosmicHGNC = 'CosmicHGNC'
CosmicMutantExport = 'CosmicMutantExport'
NSCLC_gene = '非小细胞肺癌基因'
path = 'C://Users/Administrator/Desktop' #WIN10 PATH
os.chdir(path)

#找出列表所有的索引值
def myfind(list,element):
    return [i for i in range(len(list)) if list[i] == element ]

#小型文件tsv转二维列表
def tsv2list (path,filename,fileformat):
    os.chdir(path)
    with open("%s.%s"%(filename,fileformat),'r',encoding= 'utf-8') as f:
        f.readline()
        list_genename = []
        for i in f:
            i = i.rstrip('\n').split('\t')
            list_genename.append(i)
    return list_genename

#二维列表转tsv输出
def list2tsv (path,inputlist,filename,fileformat):
    joinlist = []
    for i in inputlist:
        i = '\t'.join(i)
        joinlist.append(i)
    finallist = '\n'.join(joinlist)
    os.chdir(path)
    with open('%s-merged.%s'%(filename,fileformat),'w',encoding= 'utf-8') as f:
        f.write(finallist)
        f.close()
#——————————————————————————————————————————————程序主体——————————————————————————————————————————————————
#生成多个二维列表
CKB = tsv2list(path,ckb_NSCLC,fileformat)
OnKB_list = tsv2list(path,OncoKB_annotated,txt)
OnKB_drug = tsv2list(path,OncoKB_actionable,txt)
HGNC = tsv2list(path,CosmicHGNC,fileformat)
NSCLC = tsv2list(path,NSCLC_gene,fileformat)
for i in NSCLC:
    i.remove(i[5])
    for j in HGNC:
        if i[0] == j[1] and i[2] == j[2]:
            i.insert(3,j[3])
title = '''Gene Symbol	Synonyms	Entrez_id	HGNC_ID	Chromosome	Map Location	Update Date	Gene Description
'''
title = title.strip().split('\t')
NSCLC.insert(0,title)
#list2tsv(path,NSCLC,NSCLC_gene,fileformat)

genelist = []
for i in NSCLC:
    if NSCLC.index(i) >1:
        genelist.append(i)
print(genelist)

empty = ['' for i in range(17)]

#创建ID字典
Entrez_ID = {i[0]:i[2] for i in genelist}
HGNC_ID = {i[0]:i[3] for i in genelist}
print(Entrez_ID)
print(HGNC_ID)

#创建蛋白功能变化字典
mut_effect_dict = '''loss of function	Loss-of-function
loss of function – predicted	Likely Loss-of-function
gain of function – predicted	Likely Gain-of-function
gain of function	Gain-of-function
no effect - predicted	Likely Neutral
unknown	Inconclusive
no effect	Neutral'''

mut_dict = []
mut_effect_dict = mut_effect_dict.split('\n')
for i in mut_effect_dict:
    i = i.split('\t')
    mut_dict.append(i)
MutDict = {i[0]:i[1] for i in mut_dict}
print(MutDict)


#整合COSMIC,用其他数据库来补全COSMIC
"""
lll =[]
ttt = []
tttt = []
Variant = []
with open('%s.tsv'%CosmicMutantExport,'r',encoding='utf-8') as f :
    f.readline()
    for i in f:
        i= i[:-1].split('\t')
        #去掉DNA和氨基酸变异均不明确的

        if '?' in i[17] and '?' in i[18] and i[19] =='Unknown':
            AA = 1
        elif i[17] =='?' and i[18] == '?':
            AA = 1
        elif 'coding silent' in i[19] :
            AA = 1
        elif i[18] == '>':
            AA = 1
        else:
            AA = 0
        #去掉同义突变或者无法理解的符号的
        if  AA== 0 :
            #转换COSMIC上基因名带ENST的转录本的突变到正常格式
            if '_' in i[0]:
                ii = re.split('[_]', i[0])
                iii = ii[0]
                iiii = ii[1]
                if iii == 'TP53' or iii == 'RET':
                    if i[0] not in lll:
                        lll.append(i[0])
            else:
                iii = i[0]
            #生成空列表，根据基因名字获取ID，并补充转录本及CHGVS PGVS 坐标 pubmed ID等信息
            if iii in HGNC_ID:
                E = ['' for i in range(18)]
                E[0] = iii
                if i[1].startswith('E') == True:
                    E[1] = i[1]
                elif '_' in i[0]:
                    E[1] = iiii
                else:
                    E[2] = i[1]
                E[3] = Entrez_ID[iii]
                E[4] = HGNC_ID[iii]
                E[5] = i[17][2:]
                E[6] = i[18][2:]
                E[13] = i[19]
                if i[23] == '':
                    pass
                elif i[23][0].isalnum() == True:
                    s = re.split('[:-]', i[23])
                    E[7] = s[0]
                    E[8] = s[1]
                    E[9] = s[2]
                E[12] = i[24]
                E[16] = i[30]
                t = [E[0],E[5],E[6]]  # 基因名+cDNA+氨基酸三元
                tt = [E[0], E[6]]  # 基因名+氨基酸 二元
                #防止重复 同时辅助记录每个突变在列表的index
                if t not in ttt:
                    if '?' in t[1] and tt not in tttt:
                        Variant.append(E)
                        ttt.append(t)
                        tttt.append(tt)
                    elif '?' not in t[1]:
                        Variant.append(E)
                        ttt.append(t)
                        tttt.append(tt)
title = '''Gene Symbol	ENST	RefSeq	Entrez Gene ID	HGNC_ID	Mutation CDS	Mutation AA	chromosome	start	stop	reference_bases	variant_bases	Mutation strand	Mutation type	Oncogenicity	Mutation Effect	PMIDs for Mutation Effect	Abstracts for Mutation Effect'''
title = title.split('\t')
Variant.insert(0,title)
title_ttt = ['gene','CHGVS','PHGVS']
title_tttt = ['gene','PHGVS']
ttt.insert(0,title_ttt)
tttt.insert(0,title_tttt)

list2tsv(path, Variant, 'COSMIC', 'tsv')
list2tsv(path, ttt, 'COSMIC_ttt', 'tsv')
list2tsv(path, tttt, 'COSMIC_tttt', 'tsv')
"""


#整合CKB
"""
COSMIC_merged = 'COSMIC-merged'
COSMIC_merged = tsv2list(path,COSMIC_merged,fileformat)
COSMIC_ttt_merged = 'COSMIC_ttt-merged'
ttt = tsv2list(path,COSMIC_ttt_merged,fileformat)
COSMIC_tttt_merged = 'COSMIC_tttt-merged'
tttt = tsv2list(path,COSMIC_tttt_merged,fileformat)

with open('%s.tsv'%ckb_NSCLC,'r',encoding='utf-8') as f :
    f.readline()
    for i in f:
        i = i[:-1].split('\t')
        #排除不符合条件的突变，但凡突变类型未知
        exception = ['wild-type','fusion']
        if i[1].islower() == True and i[1] not in exception :
            exclusive = 1
        else:
            exclusive = 0
        if i[0] in Entrez_ID and exclusive == 0 :
            #生成基因名+PHGVS的列表，在前一步生成的COSMIC突变辅助记录index列表中找寻index，通过index替换蛋白功能变化和解释等信息
            tt = [i[0],i[1]]
            if tt in tttt:
                tt_index = myfind(tttt,tt)
                for j in tt_index:
                    if COSMIC_merged[j][15] == '':
                        COSMIC_merged[j][15] = MutDict[i[3]]
                    if COSMIC_merged[j][13] == '':
                        COSMIC_merged[j][13] = i[2]
                    COSMIC_merged[j][17] = i[4]+'(CKB)'
            #未出现在前一步列表里的突变，在末尾重新添加
            elif '-' in i[1] :
                search = re.search(r'(\S+) ?(-) ?(\S+)', i[1])
                search = [search.group(1), search.group(2), search.group(3)]
                s = ''.join(search)
                i[1] = s
                tt = [i[0],i[1]]
                tttt.append(tt)
                ttt.append([tt[0],'?',tt[1]])
                E = ['' for i in range(18)]
                E[15] = MutDict[i[3]]
                E[13] = i[2]
                E[17] = i[4] + '(CKB)'
                E[6] = tt[1]
                E[0] = tt[0]
                E[4] = HGNC_ID[tt[0]]
                E[3] = Entrez_ID[tt[0]]
                COSMIC_merged.append(E)
            elif i[1][1].islower() == True :
                tttt.append(tt)
                ttt.append([tt[0],'?',tt[1]])
                E = ['' for i in range(18)]
                E[15] = MutDict[i[3]]
                E[13] = i[2]
                E[17] = i[4] + '(CKB)'
                E[6] = tt[1]
                E[0] = tt[0]
                E[4] = HGNC_ID[tt[0]]
                E[3] = Entrez_ID[tt[0]]
                COSMIC_merged.append(E)

title = '''Gene Symbol	ENST	RefSeq	Entrez Gene ID	HGNC_ID	Mutation CDS	Mutation AA	chromosome	start	stop	reference_bases	variant_bases	Mutation strand	Mutation type	Oncogenicity	Mutation Effect	PMIDs for Mutation Effect	Abstracts for Mutation Effect'''
title = title.split('\t')
COSMIC_merged.insert(0, title)
list2tsv(path, COSMIC_merged, 'COSMIC_CKB', 'tsv')

title_ttt = ['gene','CHGVS','PHGVS']
title_tttt = ['gene','PHGVS']
ttt.insert(0,title_ttt)
tttt.insert(0,title_tttt)
list2tsv(path, ttt, 'COSMIC_CKB_ttt', 'tsv')
list2tsv(path, tttt, 'COSMIC_CKB_tttt', 'tsv')
"""


#整合OncoKB

COSMIC_CKB_merged = 'COSMIC_CKB-merged'
COSMIC_merged = tsv2list(path,COSMIC_CKB_merged,fileformat)
COSMIC_CKB_ttt_merged = 'COSMIC_CKB_ttt-merged'
ttt = tsv2list(path,COSMIC_CKB_ttt_merged,fileformat)
COSMIC_CKB_tttt_merged = 'COSMIC_CKB_tttt-merged'
tttt = tsv2list(path,COSMIC_CKB_tttt_merged,fileformat)

for i in OnKB_list:
    if i[3] in Entrez_ID:
        tt = [i[3],i[4]]
        if tt in tttt:
            tt_index = myfind(tttt, tt)
            for j in tt_index:
                COSMIC_merged[j][15] = i[6]
                COSMIC_merged[j][14] = i[5]
                if COSMIC_merged[j][1] == i[0] and COSMIC_merged[j][2] == '':
                    COSMIC_merged[j][2] =i[1]
                if COSMIC_merged[j][2][:-3] == i[1][:-3] and COSMIC_merged[j][1] == '':
                    COSMIC_merged[j][1] = i[0]
                if COSMIC_merged[j][13] == '':
                    COSMIC_merged[j][13] = i[4]
                if COSMIC_merged[j][16] =='':
                    COSMIC_merged[j][16] = i[7]
                else:
                    COSMIC_merged[j][16] = COSMIC_merged[j][16]+'|'+i[7]
                if COSMIC_merged[j][17] == '' and i[8] != '':
                    COSMIC_merged[j][17] = i[8]+' (OncoKB)'
                elif COSMIC_merged[j][17] != '' and i[8] != '' :
                    COSMIC_merged[j][17] = COSMIC_merged[j][17]+'|'+ i[8] +' (OncoKB)'
        else:
            


title = '''Gene Symbol	ENST	RefSeq	Entrez Gene ID	HGNC_ID	Mutation CDS	Mutation AA	chromosome	start	stop	reference_bases	variant_bases	Mutation strand	Mutation type	Oncogenicity	Mutation Effect	PMIDs for Mutation Effect	Abstracts for Mutation Effect'''
title = title.split('\t')
COSMIC_merged.insert(0, title)
list2tsv(path, COSMIC_merged, 'COSMIC_CKB_OncoKB', 'tsv')

title_ttt = ['gene','CHGVS','PHGVS']
title_tttt = ['gene','PHGVS']
ttt.insert(0,title_ttt)
tttt.insert(0,title_tttt)
list2tsv(path, ttt, 'COSMIC_CKB_OncoKB_ttt', 'tsv')
list2tsv(path, tttt, 'COSMIC_CKB_OncoKB_tttt', 'tsv')

#整合CIVIC

time1 = time.time()
print("运行总共耗时为%a秒"%(time1-time0))
