
list1 = [7,' ',' ',' ',' ',' ',' ','    ',' ',' ',' ',' ',' ',' ', 9,' ']
list2 = [' ','  ']
list = []
for i in list1:
    if i not in list2:
        list.append(i)
print(list)

a = [1, 2, 3, 12,11,12,12,11,12, 5, 6, 8, 9]
b = a
for i in a:
    if i % 2 == 0 and i % 3 == 0:
        b.remove(i) #始终在删除第一个匹配项而不受i在次序上遍历至哪个元素的影响
    print(a,'-----',b)
a = b
print(a)


list1 = [7,' ',' ',' ',' ',' ',' ','    ','  ',' ',' ',' ',' ',' ',' ', 9,' ']
list2 = [' ','  ']
blank = []
print(list[0] in list1)

for i in list2:
    while i in list1:
        list1.remove(i)
print(list1)
