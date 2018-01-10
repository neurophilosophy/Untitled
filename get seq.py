import os
import pysam
import time
start_time = time.time()
hg19 = pysam.FastaFile('hg19.fa')
Base_dict = {'A':'T','G':'C','T':'A','C':'G'}
filename = 'nightly-ClinicalEvidenceSummaries'
#path = 'C://Users/Administrator/Desktop' #win10 path
path = '/home/caesar/Desktop'
os.chdir(path)
print(os.getcwd())
list = []
endlist = []
final_list = []
# 对于tsv格式的文件，其内容读取为一整个字符串读取后，用split方法分割成一个多维列表
t = open('%s.tsv' % filename, 'r',encoding="utf-8")
#用读取来跳过表头
t.readline()
#从readline之后的一行开始遍历，最后收获【基因名，突变类型，染色体，起始点，终止点，序列】
for line in t:
    array = line[:-1].split('\t')
    #排除掉数值为空或0的行，开始按条件操作，正义链start和end正常操作，反义链则需调换两者位置后进行
    if array[19] != '0'and array[19] != '' and array[20] !='0'and array[19] != '' :
        name = array[0]
        mutations = array[2]
        disease = array[3]
        drugs = array[5]
        evidence_type = array[6]
        evidence_direction = array[7]
        evidence_level = array[8]
        clinical_significance = array[9]
        evidence_statement = array[10]
        pubmed_id = array[11]
        citation = array[12]
        representative_transcript = array[23]
        variant_summary = array[30]
        chro = ''.join(['chr', array[18]])

        # pysam 默认start end 相同就没有，若需要单个碱基则start-1，n-n+1获取的是第n+1个碱基
        if abs(int(array[19])-int(array[20])) < 200:
            #if gtf[6] == '+':
            if array[19]<=array[20]:
                start = int(array[19]) - 60
                end = int(array[20]) + 59
                seq = hg19.fetch(chro, start, end)
            else:
                start = int(array[20]) - 59
                end = int(array[19]) + 60
                seq = ''.join([Base_dict[k] for k in (reversed(hg19.fetch(chro, start, end)))])
        else:
            seq = 'Too large sequence'
        list.append([name, mutations,disease,variant_summary,drugs,evidence_type, evidence_direction, evidence_level, clinical_significance, evidence_statement, pubmed_id,citation, representative_transcript,chro, str(start), str(end), '+ or -', seq])
# 以制表符合并每个列表中的元素
for k in list:
    k = "\t ".join(k)
    endlist.append(k)
# 以换行符整合列表为字符串
final_list = "\n ".join(endlist)
# 输出保存并关闭
outfile = open('%s - splited.tsv' % filename, 'w', encoding="utf-8")
outfile.write(final_list)
outfile.close()
stop_time = time.time()
print('%s.tsv Done!' % filename)
print('运行耗时为：%a秒'%(stop_time-start_time))
