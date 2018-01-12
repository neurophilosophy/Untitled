# -*- coding: utf-8 -*-

#去除列表中已知的某些元素
list1 = [7,' ',' ',' ',' ',' ',' ',"",'    ',' ',' ',' ',' ',' ',' ', 9,' ']
list2 = [' ','  ']
list = []
for i in list1:
    if i not in list2 and i != "":
        list.append(i)
print(list)


#替换掉字符串中某一特定字符
a = 'ygewiuihakjdhkashjdhkashdkjsahkd       duplicate            131231      13231321   '
a = a.replace("u"," ").replace("j"," ")
a.replace("dh"," ")
print(a)


#>=2个连续的空格，删除
print(" ".join(a.split()))


#空列表长度为0
L = []
print(len(L))


#删除列表中符合特征要求的元素
a = [1, 2, 3, 12,11,12,12,11,12, 5,"21","21","21" ,6, 8, 9]
b = a.copy()
for i in a:
    if type(i) != int: #仅需判断一次，不需要反复循环判断,type输出的不是字符串
        while i in b :
            b.remove(i)
    elif i % 2 == 0 and i % 3 == 0 :
        while i in b:  #始终在删除第一个匹配项而不受i在次序上遍历至哪个元素的影响
            b.remove(i)
    while b.count(i)>1: #删除重复的元素仅保留一个
        b.remove(i)

print(a,'-----',b)
