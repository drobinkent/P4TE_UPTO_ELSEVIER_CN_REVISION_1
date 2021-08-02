from os import listdir
from os.path import isfile, join
import testAndMeasurement.ResultProcessor as rp
import numpy as np

import ConfigConst


def getAllFilesInDirectory(folderPath):

    # r=root, d=directories, f = files
    onlyfiles = [f for f in listdir(folderPath) if (isfile(join(folderPath, f)))]
    # print("Total files in this directory is ", len(onlyfiles))
    return onlyfiles


def getAVGFCTByFolderOld(folderName):
    # files = getAllFilesInDirectory(folderName)
    flowTypeVsFCTMap = {}
    flowTypeVsFlowCountMap = {}
    flowTypeVsSendBytesMap = {}
    # for flowVolume in ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB:
    #     # flowTypeVsFCTMap[flowVolume]  = 0
    #     flowTypeVsFCTMap[flowVolume]  = []
    #     flowTypeVsFlowCountMap[flowVolume] = 0
    start, end, iperfResultsAsList = rp.parseIperfResultsFromFolder(folderName)
    iperfResultsAsList = iperfResultsAsList.iperfResults
    # print("Result is ", iperfResultsAsList.iperfResultsAsList)

    totalBytesSent = 0
    for r in iperfResultsAsList:
        flowSize = r[0].end.sum_received.bytes
        fct = r[0].end.sum_received.seconds
        totalBytesSent = totalBytesSent + flowSize
    totalBytesSent = totalBytesSent/1024
    print("totalBytesSent (in KB) =",totalBytesSent )
    print("Total flows "+str(len(iperfResultsAsList)))
    for r in iperfResultsAsList:
        flowSize = r[0].end.sum_received.bytes
        # print(flowSize)
        fct = r[0].end.sum_received.seconds
        for flowVolume in ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB:
            if abs(flowVolume*1024 - flowSize) <= (20*1024):
                # flowTypeVsFCTMap[flowVolume] = flowTypeVsFCTMap.get(flowVolume) + fct
                if (flowTypeVsFCTMap.get(flowVolume) == None):
                    flowTypeVsFCTMap[flowVolume] = []
                    flowTypeVsFlowCountMap[flowVolume] = 0
                    flowTypeVsSendBytesMap[flowVolume] = []
                    pass
                else:
                    flowTypeVsFCTMap.get(flowVolume).append(fct)
                    flowTypeVsFlowCountMap[flowVolume] = flowTypeVsFlowCountMap.get(flowVolume) + 1
                    flowTypeVsSendBytesMap.get(flowVolume).append(flowSize)
    totalFlowsize = 0
    totalOfFlowSizeMultipliedByAvgFct=0
    for f in flowTypeVsFCTMap:
        # print(str(f) + " -- ",np.percentile(flowTypeVsFCTMap.get(f), 80))
        # print(str(f) + " -- ",flowTypeVsFlowCountMap.get(f))

        print(str(f) + " -- ",(flowTypeVsFlowCountMap.get(f)))
        weightedFct = np.average(flowTypeVsFCTMap.get(f))
        # weightedFct = np.percentile(flowTypeVsFCTMap.get(f),90)
        print(str(f) + " -- ",weightedFct)
        # print(str(f) + " -- ",np.std(flowTypeVsFCTMap.get(f)))
        # print(flowTypeVsFCTMap.get(f))
        totalFlowsize= totalFlowsize+ float(f)
        totalOfFlowSizeMultipliedByAvgFct = totalOfFlowSizeMultipliedByAvgFct + ( float(f) * weightedFct)
    print("Average FCT  = ", totalOfFlowSizeMultipliedByAvgFct/totalFlowsize)
    pass

def getAVGFCTByFolder(folderName):
    # files = getAllFilesInDirectory(folderName)
    flowTypeVsFCTMap = {}
    flowTypeVsFlowCountMap = {}
    flowTypeVsSendBytesMap = {}
    flowTypeVsRetransmissionMap = {}
    # for flowVolume in ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB:
    #     # flowTypeVsFCTMap[flowVolume]  = 0
    #     flowTypeVsFCTMap[flowVolume]  = []
    #     flowTypeVsFlowCountMap[flowVolume] = 0
    start, end, iperfResultsAsList = rp.parseIperfResultsFromFolder(folderName)
    iperfResultsAsList = iperfResultsAsList.iperfResults
    # print("Result is ", iperfResultsAsList.iperfResultsAsList)

    totalBytesSent = 0
    totalTime = 0
    totalRetransmission= 0
    for r in iperfResultsAsList:
        flowSize = r[0].end.sum_received.bytes
        fct = r[0].end.sum_received.seconds
        totalTime = totalTime + fct
        totalBytesSent = totalBytesSent + flowSize
        retransmits = r[0].end.sum_sent.retransmits
        totalRetransmission = totalRetransmission + retransmits
    totalBytesSent = totalBytesSent/1024

    print("Total flows "+str(len(iperfResultsAsList)))
    print("total BytesSent (in KB) =",totalBytesSent )
    print("Total Time "+str(totalTime))
    print("Total Retrasmits "+str(totalRetransmission))
    for r in iperfResultsAsList:
        flowSize = r[0].end.sum_received.bytes
        flowVolume = flowSize
        # print(flowSize)
        fct = r[0].end.sum_received.seconds
        # flowTypeVsFCTMap[flowVolume] = flowTypeVsFCTMap.get(flowVolume) + fct
        if (flowTypeVsFCTMap.get(flowVolume) == None):
            flowTypeVsFCTMap[flowVolume] = [fct]
            flowTypeVsFlowCountMap[flowVolume] = 1
            flowTypeVsSendBytesMap[flowVolume] = [flowVolume]
            flowTypeVsRetransmissionMap[flowVolume] = [r[0].end.sum_sent.retransmits]
            pass
        else:
            flowTypeVsFCTMap.get(flowVolume).append(fct)
            flowTypeVsFlowCountMap[flowVolume] = flowTypeVsFlowCountMap.get(flowVolume) + 1
            flowTypeVsSendBytesMap.get(flowVolume).append(flowSize)
            flowTypeVsRetransmissionMap.get(flowVolume).append(r[0].end.sum_sent.retransmits)
    totalFlowsize = 0
    totalOfFlowSizeMultipliedByAvgFct=0
    shortFlowTotalBytesSent = 0
    shortFlowTotalBytesMultipliedByFCT = 0
    shortFlowTotalBytesMultipledByRetransmission =0
    largeFlowTotalBytesSent = 0
    largeFlowTotalBytesMultipliedByFCT = 0
    largeFlowTotalRetransmission =0
    shortFlowcount = 0
    largeFlowcount = 0
    for f in flowTypeVsFCTMap:
        j=0
        for j in range(0,len(flowTypeVsSendBytesMap.get(f))):
            if (flowTypeVsSendBytesMap.get(f)[j]<1024*1024):
                shortFlowTotalBytesSent = shortFlowTotalBytesSent + float(f)
                shortFlowTotalBytesMultipliedByFCT = shortFlowTotalBytesMultipliedByFCT + float(f) * flowTypeVsFCTMap.get(f)[j]
                shortFlowTotalBytesMultipledByRetransmission = shortFlowTotalBytesMultipledByRetransmission + flowTypeVsRetransmissionMap.get(f)[j]
                shortFlowcount =  shortFlowcount  + 1
            else:
                largeFlowTotalBytesSent = largeFlowTotalBytesSent + float(f)
                largeFlowTotalBytesMultipliedByFCT = largeFlowTotalBytesMultipliedByFCT + float(f) * flowTypeVsFCTMap.get(f)[j]
                largeFlowTotalRetransmission = largeFlowTotalRetransmission + flowTypeVsRetransmissionMap.get(f)[j]
                largeFlowcount = largeFlowcount  + 1
        # weightedFct = np.average(flowTypeVsFCTMap.get(f))
        #
        # totalFlowsize= totalFlowsize+ float(f)
        # totalOfFlowSizeMultipliedByAvgFct = totalOfFlowSizeMultipliedByAvgFct + ( float(f) * weightedFct)
    if (shortFlowTotalBytesSent > 0):
        print("shortFlowcount is "+str(shortFlowcount))
        print("Average FCT for short flow  = ", shortFlowTotalBytesMultipliedByFCT/shortFlowTotalBytesSent)
    if (largeFlowTotalBytesSent > 0):
        print("largeFlowcount is "+str(largeFlowcount))
        print("Average FCT for large flow  = ", largeFlowTotalBytesMultipliedByFCT/largeFlowTotalBytesSent)
    print("Average retransmissions for short flow  = ", shortFlowTotalBytesMultipledByRetransmission/shortFlowcount)
    print("Average retransmissions for large flow  = ", largeFlowTotalRetransmission/largeFlowcount)
    pass


print(" Analyzing average FCT and total retransmissions for data mining workload ")

print("Load factor 0.8")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/ECMP_RESULTS/DataMining_Workload_load_factor_0.8/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/P4TE_RESULTS/DataMining_Workload_load_factor_0.8/client-logs-0")
print("\n\n")




print("Load factor 0.6")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/ECMP_RESULTS/DataMining_Workload_load_factor_0.6/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/P4TE_RESULTS/DataMining_Workload_load_factor_0.6/client-logs-0")
print("\n\n")

print("Load factor 0.4")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/ECMP_RESULTS/DataMining_Workload_load_factor_0.4/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/P4TE_RESULTS/DataMining_Workload_load_factor_0.4/client-logs-0")
print("\n\n")

print("Load factor 0.2")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/ECMP_RESULTS/DataMining_Workload_load_factor_0.2/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/P4TE_RESULTS/DataMining_Workload_load_factor_0.2/client-logs-0")
print("\n\n")
#

print("===================================================================================================================================================")
print(" Analyzing average FCT and total retransmissions for web search workload ")

print("Load factor 0.8")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/ECMP_RESULTS/WebSearchWorkLoad_load_factor_0.8/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/P4TE_RESULTS/WebSearchWorkLoad_load_factor_0.8/client-logs-0")
print("\n\n")

# print("P4TE-variation")
# getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.8/client-logs-0")
# print("\n\n")

print("Load factor 0.6")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/ECMP_RESULTS/WebSearchWorkLoad_load_factor_0.6/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/P4TE_RESULTS/WebSearchWorkLoad_load_factor_0.6/client-logs-0")
print("\n\n")


print("Load factor 0.4")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/ECMP_RESULTS/WebSearchWorkLoad_load_factor_0.4/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/P4TE_RESULTS/WebSearchWorkLoad_load_factor_0.4/client-logs-0")
print("\n\n")


print("Load factor 0.2")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/ECMP_RESULTS/WebSearchWorkLoad_load_factor_0.2/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_WEB_SEARCH_WORKLOAD_RESULTS/P4TE_RESULTS/WebSearchWorkLoad_load_factor_0.2/client-logs-0")
print("\n\n")


print("\n\n\n\n===================================================================================================================================================")
print(" Analyzing average FCT and total retransmissions for incast scneario")

print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_INCAST_WORKLOAD/ecmp/l2-incast/client-logs-0")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_INCAST_WORKLOAD/P4TE/l2-incast/client-logs-0")
print("\n\n")



print("Load factor 0.2")
print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.6/client-logs-1")
print("\n\n")

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.6/client-logs-0")
print("\n\n")

