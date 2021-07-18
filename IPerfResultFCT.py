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


def getAVGFCTByFolder(folderName):
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
            if abs(flowVolume*1024 - flowSize) <= (30*1024):
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

print("P4TE")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS_DATA_MINING_WORKLOAD_RESULTS/P4TE_RESULTS/WebSearchWorkLoad_load_factor_0.2/client-logs-0")
print("\n\n")

print("ECMP")
getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.2/client-logs-0")
print("\n\n")
#

# print("P4TE")
# getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.8/client-logs-2")
# print("\n\n")
# #
# print("P4TE")
# getAVGFCTByFolder(folderName= "/home/deba/Desktop/P4TE/testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.8/client-logs-2")
# print("\n\n")