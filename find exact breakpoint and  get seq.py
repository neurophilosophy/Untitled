import os
import re
import time

path = 'C://Users/Administrator/Desktop'
data_filename = 'CosmicFusionExport-Translocation-filtered_exon_location'
fileformat = "tsv"
#定义tsv转二维列表
def input_2d_list(path,filename,fileformat):
    os.chdir(path)
    with open('%s.%s'%(filename,fileformat),'r',encoding='utf-8') as f:
        f.readline()
        list_location = []
        for i in f:
            i = i[:-1].split('\t')
            list_location.append(i)
    return list_location

list_exon_location = input_2d_list(path,data_filename,fileformat)
print(list_exon_location)


a = ['EML4','ENST00000318522','1903insATATGCTGGAT','ALK','ENST00000389048','4129','6220']
b = ['EML4','ENST00000318522','2229+222','ALK','ENST00000389048','4126','6220']
c = ['EML4','ENST00000318522','2229ins68','ALK','ENST00000389048','4080','6220']
d = ['EML4','ENST00000318522','2318+654insT','ALK','ENST00000389048','4080-172','6220']

fusion = [a,b,c,d]
#定义抓取转录本信息中的相对位置，是否延伸到内含子，是否有插入
def search_for_mRNA_postision(str):
    list_result1 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(1)
    list_result2 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(2)
    list_result3 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(3)
    list_result4 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(4)
    list_result5 = re.search(r'(\d+)(\+?\-?)(\d*)(ins)?(\w+)*', str).group(5)
    return [list_result1,list_result2,list_result3,list_result4,list_result5]

#定义通过前面获取的信息，计算基因组上断裂点和插入的序列
def determine_breakpoint(fusionlist,datalist):
    strand_dict = {'+':1,'-':-1}
    if type(fusionlist) == list and type(datalist) == list:
        partner1_exondata = []
        partner2_exondata = []
        #对于输入的融合位点，先获取融合基因的外显子数据
        for line in datalist:
            if fusionlist[1] in line:
                partner1_exondata.append(line)
            if fusionlist[-3] in line:
                partner2_exondata.append(line)
        print(partner1_exondata)
        print(partner2_exondata)
        for i in partner1_exondata:
            position = search_for_mRNA_postision(fusionlist[2])
            strand1 = i[7]
            a,b,c,d,e = position[0],position[1],position[2],position[3],position[4]
            if int(i[8])<= int(a) <=int(i[9]):
                print(i)
                print(position)
                A =  int(i[4]) - int(a) + int((float(i[8])+float(i[9]))/2 + strand_dict[strand1]*(float(i[9])-float(i[8]))/2)
                print(A)
                if c =='' and d == None:
                    breakpoint_A = A ; insert_seq_A = ''
                elif c != '' and d ==None:
                    breakpoint_A = A + strand_dict[position[1]]*strand_dict[strand1]*int(c); insert_seq_A =''
                elif c != '' and d != None:
                    breakpoint_A = A + strand_dict[position[1]]*strand_dict[strand1]*int(c); insert_seq_A = e
                elif c=='' and d != None:
                    breakpoint_A = A; insert_seq_A = e
                strand_A = strand1
                print(breakpoint_A)
        for i in partner2_exondata:
            position = search_for_mRNA_postision(fusionlist[-2])
            strand2 = i[7]
            a,b,c,d,e = position[0],position[1],position[2],position[3],position[4]
            if int(i[8])<= int(a) <=int(i[9]):
                print(i)
                print(position)
                B =  int(i[4]) - int(a) + int((float(i[8])+float(i[9]))/2 + strand_dict[strand2]*(float(i[9])-float(i[8]))/2)
                print(B)
                if c =='' and d == None:
                    breakpoint_B = B ; insert_seq_B = ''
                elif c != '' and d ==None:
                    breakpoint_B = B + strand_dict[position[1]]*strand_dict[strand2]*int(c); insert_seq_B =''
                elif c != '' and d != None:
                    breakpoint_B = B + strand_dict[position[1]]*strand_dict[strand2]*int(c); insert_seq_B = e
                elif c=='' and d != None:
                    breakpoint_B = B; insert_seq_B = e
                strand_B = strand2
                print(breakpoint_B)


        b=0
        final_coordinate = [breakpoint_A,strand_A,insert_seq_A,breakpoint_B,strand_B,insert_seq_B]

    else:
        print('INPUT ERROR!!')
    return final_coordinate
C = determine_breakpoint(d,list_exon_location)
print(C)