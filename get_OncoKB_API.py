from Fileconvert import *
from json_parse import *
import json
import time
import requests
import pandas as pd
import numpy as np


time0 = time.time()
path = 'C://Users/Administrator/Desktop'  # WIN10 PATH
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

oncokb_url = 'http://oncokb.org/api/v1/%s' % 'genes'
fc = Fileconvert(path)


def get_url_text(url):
    tables = requests.get(url)  # , headers= header)
    print('开始获取链接。。。')
    if tables.ok:
        print('{} 链接成功！！！'.format(url))
        return tables.content.decode()
    else:
        print('{} 链接失败！！！'.format(url))


def get_OncoKB(url):
    message = get_url_text(url)

    dict_msg = json.loads(message)
    final_dict = parse_mosaic_dict(dict_msg)

    if os.path.isfile('.\\{}'.format('OncoKB_evidences.tsv')):
        add_title = None
    else:
        add_title = True
    for x, y in final_dict.items():
        if isinstance(y, (list, tuple)):
            final_dict[x] = ';'.join(['{}'.format(z) for z in y])

    df = pd.DataFrame(final_dict, index=[0])
    df.to_csv('OncoKB_evidences.tsv', index=None, header=add_title, sep='\t', mode='a')


def get_each_des_OncoKB(entrezGeneIds):
    for each in entrezGeneIds:
        url = 'http://oncokb.org/api/v1/genes/{}/evidences'.format(each)
        get_OncoKB(url)


entrezGeneIds = '''5976
126961
27244
84142
6416
7403
5378
6774
171023
54894
2782
2146
9641
8348
940
8503
57105
2118
23152
6850
7422
4683
440093
5802
387893
4286
7852
10018
9212
2145
10672
974
4824
22800
4869
8085
11122
8726
8241
4595
5584
653604
6926
25
79109
83852
8968
3082
29072
84159
3575
2120
639
8202
8289
9175
1387
8347
253260
4221
5965
10769
56940
1499
545
6657
5979
29086
811
2969
7812
23451
7514
7113
11021
2177
7803
5644
83540
4916
7248
5296
6311
6389
23308
973
367
5424
10957
10498
1871
6256
3815
4915
3480
5594
5921
2534
5045
54904
694
5295
537
2077
6921
3169
257194
9611
1026
668
675
867
2874
1019
79728
8915
6009
4914
369
6391
6794
7010
4067
6662
2078
3586
2033
2903
8438
10892
151987
1058
3065
5914
5426
7157
8452
7249
2073
6390
5894
8339
688
8314
598
1786
207
3418
51755
64326
998
55193
4486
1021
3667
6790
10111
5290
4853
4194
2072
9688
79918
4297
6927
8493
80204
1027
7048
5289
208
3417
3791
5892
7307
5288
324
5885
6199
1846
4854
80243
5927
2071
6392
4193
8969
51750
387
9656
23512
2248
80380
79577
3845
2264
64321
5595
1029
4855
2475
2099
27161
8312
4893
6608
85236
55209
672
7046
83931
8233
1024
2263
51684
4610
5291
5925
54165
8313
63978
2068
57492
1999
333932
9314
596
5889
8929
4613
8242
51742
58508
1031
80312
6237
4261
5926
84231
2066
2249
7525
64109
2261
5366
330
90417
1030
4485
5170
7516
8651
4068
23429
8880
51564
2065
7015
60468
2260
3337
11200
5587
138715
161742
143686
4851
2623
440926
2064
5781
2176
10620
673
1956
83667
5890
8660
355
5727
841
92002
22894
8970
7297
10735
23405
2624
2195
865
2175
4087
4352
3020
8332
3399
1840
1788
4436
999
10019
580
2625
10481
4780
3105
2308
3021
200424
3624
4609
5292
3265
4763
7253
2047
6929
4089
5893
3106
54093
4233
8357
238
4170
29126
2130
8821
3008
5395
695
898
4088
861
124540
613
64324
1977
5336
4437
8358
3009
1441
57144
2045
558
2932
896
3659
55294
5879
604
2321
3017
23067
5294
8336
3716
7128
9869
4292
4921
2044
157570
9401
54949
23013
9020
3091
5293
6602
3394
84444
8334
567
29123
1540
8859
6777
9757
11338
894
6714
27086
5468
10000
331
3718
196528
641
8405
2767
71
1050
2042
8764
54206
6776
8626
5880
5966
4440
2322
4361
5888
1789
3717
4778
2768
6598
7158
256646
54790
1974
4654
657
5071
100271849
5537
8351
3720
1523
242
51185
26585
7849
5573
7468
54855
2956
3662
55252
2324
8352
8036
64283
4771
595
9965
6597
79679
7150
84433
9817
84464
3643
6890
1820
3636
5058
7428
7186
1399
55164
6934
2776
4913
5728
4214
57521
8350
3725
6654
1654
1958
6016
1964
6427
965
3459
6098
2115
5133
23385
9759
64121
5789
8355
4615
5159
3006
463
1111
2778
25937
472
23476
84193
1436
4149
6891
23269
5079
51162
3479
3623
8356
55500
83990
4792
26524
3007
54880
9968
1493
2271
29102
80381
201163
80854
546
10664
90
526
57634
1616
4072
8986
142
8353
8290
9113
5605
5241
3631
64754
5518
27113
2034
64919
3481
10413
10865
55654
7080
8354
7490
5604
4004
139285
5156
2735
63035
22806
10320'''.split('\n')

# get_each_des_OncoKB(entrezGeneIds)

tsv = fc.fastSelectTsv('OncoKB_evidences_origin.tsv', [8, 7, 9, 11, 12, 10, 13, 14, 3])

for line in tsv:
    des = line[-1].replace('.;', '|').replace('"', '').strip()
    if '|' in des:
        full_des, short_des = tuple(des.split('|'))
    else:
        full_des, short_des = des, '-'

    line[-1] = short_des.strip()
    line.append(full_des.strip())

title = '''Gene_Symbol\tEntrez_id\tFull_name\tTranscript\tRefseq\tOncogene\tTumorSuppressGene\tPMIDs\tShort_des\tGene_Description(OncoKB)'''.split(
    '\t')
time0 = time.time()
for i in range(100):
    df = pd.DataFrame(tsv)
    df.columns = title
    df.to_csv('OncoKB_evidences111.tsv', sep='\t', index=None, header=True)
time1 = time.time()
print("运行总共耗时为%a秒" % (time1 - time0))

time0 = time.time()
for i in range(100):
    tsv.insert(0, title)
    fc.list2tsv(path, tsv, 'OncoKB_evidences')

time1 = time.time()
print("运行总共耗时为%a秒" % (time1 - time0))
