import pysam
import os
#path = 'C://Users/Administrator/Desktop' #win10 path
path = '/home/caesar/Desktop'
os.chdir(path)
hg19 = pysam.FastaFile('hg19.fa')
Base_dict = {'A':'T','G':'C','T':'A','C':'G','a':'t','g':'c','t':'a','c':'g'}
#定义反向互补函数
def rev_comple_seq(sequence):
    rev_seq = ''.join([Base_dict[k] for k in sequence])
    rev_com_seq = ''.join(reversed(rev_seq))
    return (rev_com_seq)

#定义获取基因组序列函数
def get_genomic_seq(chro, startpoint, endpoint):
    if abs(startpoint - endpoint) < 200:
        # if gtf[6] == '+':
        if startpoint <= endpoint:
            start = startpoint - 60
            end = endpoint + 60
            genomic_sequence = hg19.fetch(chro, start, end)
        else:
            start = endpoint - 60
            end = startpoint + 60
            genomic_sequence = rev_comple_seq(hg19.fetch(chro, start, end))
    else:
        start = startpoint
        end = endpoint
        genomic_sequence = 'Too large sequence,please check the coordinates'
        return genomic_sequence

#example    
JAK2 = (get_genomic_seq('chr9',5073770,5073770))
print(JAK2)
