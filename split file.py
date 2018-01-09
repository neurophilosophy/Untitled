import os
print(os.getcwd())
def split_file(filename,path):
    # 转换到指定目录，并显示确认
    os.chdir('C://Users/Administrator/Downloads/cBioportal')
    # 对于tsv格式的文件，其内容读取为一整个字符串读取后，用split方法分割成一个多维列表
    t = open('%s.tsv'% filename, 'r')
    text = t.read()
    list1 = text.split('\n')  # 先按照换行符分割成一维列表
    if list1[-1] == "":
        del list1[-1]  # 删除最后一行空行
    list2 = [i.split('\t') for i in list1]  # 再将一维列表里的每个元素都按照制表符分割成列表
    list = []  # 创建空列表
    # 对多维列表中的元素进行截取拼接
    for j in list2:
        jiequ1 = [j[0]]
        jiequ2 = [j[2]]
        jiequ3 = j[12:15]
        jiequ = jiequ1 + jiequ2 + jiequ3
        list.append(jiequ)
    endlist = []
    for k in list:
        k = ", ".join(k)
        endlist.append(k)
    end = "\n ".join(endlist)
    outfile = open('%s - splited.csv'%filename, 'w')
    outfile.write(end)
    outfile.close()
    return '%s.csv Done!'%filename


print(split_file('ALK','ALK.tsv'))