#斐波那契数列
n, a, b = 0, 0, 1
f = []
while n < 5:
    f.append(b)
    a, b = b , a + b
    n = n + 1
print(b)


#杨辉三角
import time
start_time = time.time()
def yanghui(n):
    m = 0
    a = [1]
    b = a.copy()
    print(a)
    while m<n:
        for i in range(1,len(b)):
            b[i] = a[i]+a[i-1]
        b.append(1)
        a=b.copy()
        m += 1
        #print(b)
    return b
yanghui(1000)
stop_time = time.time()
print('运行耗时为：%a秒'%(stop_time-start_time))

#杨辉三角 生成器 来自网上

start_time2 = time.time()
def triangles():
    N=[1]
    while True:
        yield N
        N.append(0)
        N=[N[i-1] + N[i] for i in range(len(N))]
n=0
for t in triangles():
    #print(t)
    n=n+1
    if n == 1000:
        break
stop_time2 = time.time()
print('运行耗时为：%a秒'%(stop_time2-start_time2))
