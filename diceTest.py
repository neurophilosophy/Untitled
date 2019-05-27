
# =======================================================掷骰子测试=======================================================

def diceTest():
	from random import randint
	import time	
	time0 = time.time()	
	def countTest(minNum, maxNum, replicateTime, targetNum=None):
		count = 0
		oldList = [0] * (replicateTime - 1)  # 初始化
		while True:
			newNum = randint(minNum, maxNum)
			count += 1
			oldList.append(newNum)
			if len(set(oldList)) == 1:
				if targetNum:
					if newNum == targetNum:
						break
				else:
					break
			else:
				oldList = oldList[1:]
		return count
	
	def diceTestAverage(maxTimes, minNum=1, maxNum=6, replicateTime=3, targetNum=None):
		return sum(countTest(minNum=minNum, maxNum=maxNum, replicateTime=replicateTime, targetNum=targetNum) for i in
		           range(maxTimes)) / maxTimes
	
	for replicateTime in range(2, 7):
		print('掷骰子连续{}个数相同，平均次数为{}次'.format(replicateTime, diceTestAverage(maxTimes=1000, minNum=1, maxNum=6,
		                                                                   replicateTime=replicateTime,
		                                                                   targetNum=None)))
	time1 = time.time()
	
	print("运行总共耗时为%a秒" % (time1 - time0))

