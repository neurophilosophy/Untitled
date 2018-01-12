blank = []
list1 = [7,' ',' ',' ',' ',' ',' ','    ','','  ',' ',' ',' ',' ',' ',' ', 9,' ']
for j in list1:
    while list1.count(j)>=1 and not j in blank and j != '' :
        print(j)
        blank.append(j)
        print(blank)
