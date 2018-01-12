def trans_input():
    list_del = []
    while True:
        # 输入信息 并消去首尾空格，然后转换成列表
        list_input = input('请输入您要操作的列，并以英文标点逗号或空格隔开：')
        list_split = ((list_input.strip()).replace(" ", ",")).split(",")
        # 消去列表空元素
        while '' in list_split:
            list_split.remove('')
        # 列表为纯粹整型数值，则增加到列表
        for i in list_split:
            if i.isdecimal() == True:
                i = int(i)
                list_del.append(i)
            else:
                list_del = []
                print('输入有误请，请重新输入')
        if list_del != []:
            break
    print(list_del)
trans_input()
