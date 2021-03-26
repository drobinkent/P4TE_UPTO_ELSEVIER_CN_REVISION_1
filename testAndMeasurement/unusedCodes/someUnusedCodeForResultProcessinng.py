# print(len(iperfResultsSortedByFlowVolume))
# print(len(iPerfResultObjectsForOneFolder.iperfResults))
#return startTimeOfCtrlrStaticticsTobeProcessedForFolder, endTimeOfCtrlrStaticticsTobeProcessedForFolder, processedResultsByFlowtype
# mininet host time and main pc time is different. Hence startime and and etime calculation used here doesn't work correctly
iperfResultsSortedByTimestamp = sorted(iPerfResultObjectsForOneFolder.iperfResults, key=lambda x: x[0].getEndTimeInSec()) # sort by starting time stamp
minTimeStamp = iperfResultsSortedByTimestamp[0][0].start.timestamp.timesecs
maxTimeStamp = iperfResultsSortedByTimestamp[len(iperfResultsSortedByTimestamp)-1][0].getEndTimeInSec()
print("Min time is "+str(minTimeStamp))
print("Max time is "+str(maxTimeStamp))
timeToThroughputMap = {}
step= 1
for t in range( minTimeStamp, maxTimeStamp):
    for r in iperfResultsSortedByTimestamp:
        for i in range(r[0].start.timestamp.timesecs, r[0].getEndTimeInSec()):
            flag = False
            fracVal = 1
            if ((float(i)+1)>r[0].getEndTimeInSec()):
                fracVal =  r[0].getEndTimeInSec() - (i)
                flag = True
            val =timeToThroughputMap.get(i)
            if (val is None):
                if flag == True:
                    timeToThroughputMap[i+1]=fracVal * r[0].end.sum_received.bits_per_second
                    pass
                else:
                    timeToThroughputMap[i+1] = r[0].end.sum_received.bits_per_second
            else:
                if flag == True:
                    timeToThroughputMap[i+1]= val + (fracVal * r[0].end.sum_received.bits_per_second)
                    pass
                else:
                    timeToThroughputMap[i+1] = val+r[0].end.sum_received.bits_per_second


totalData = 0
for k in timeToThroughputMap.keys():
    #print("time is --"+str(k)+" -- cdf is : "+str(timeToThroughputMap.get(k)))
    totalData = totalData+timeToThroughputMap.get(k)
print("TotalData from Map is "+str(totalData))
totalData = 0
for r in iperfResultsSortedByTimestamp:
    totalData = totalData+ r[0].end.sum_received.bytes
print("TotalData is ", totalData)