import json
import logging
import math
import os
import time

import numpy as np
import scipy.stats

import ConfigConst
import ConfigConst as confConst
import sys
import TestConfig as tc
from scipy.stats import uniform, poisson

logger = logging.getLogger('SSHDeployer')
hdlr = logging.FileHandler('../log/TrafficflowGenerator.log')
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logging.StreamHandler(stream=None)
logger.setLevel(logging.INFO)



def makeDirectory(folderPath, accessRights):
    if not os.path.exists(folderPath):
        os.mkdir(folderPath, accessRights)


def calculateFlowArrivalTimes(loadFactor, duration):
    networkRate = int(math.ceil(confConst.queueRateForSpineFacingPortsOfLeafSwitch * loadFactor * ConfigConst.MAX_PORT_COUNT)) # from each tor we need these many flows
    networkRateForFlowType = []
    totalFlowRequiredForFlowType=[]
    lambdaForFlowType=[]
    totalFlowRequiredForFlowTypeOverWholeDuration=[]

    for i in range (0, len(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB)):
        # networkRateForFlowType.append((ConfigConst.FLOW_TYPE_LOAD_RATIO[i] * networkRate * duration * (len(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB) - (i)))/100)
        networkRateForFlowType.append((ConfigConst.FLOW_TYPE_LOAD_RATIO[i] * networkRate * duration*ConfigConst.MAX_PORT_COUNT/4 )/100)  #It shoould be divide by 4. bcz we want only 2 sets off flows
        totalFlowRequiredForFlowType.append(math.ceil((networkRateForFlowType[i])/((ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB[i]*1024)/(ConfigConst.PACKET_SIZE))))
        lambdaForFlowType.append((duration/totalFlowRequiredForFlowType[i]))
        totalFlowRequiredForFlowTypeOverWholeDuration.append(int(1/lambdaForFlowType[i]))
        # totalIterationForFlowType.append(duration/)
        # print(lambdaForFlowType)
        # print(totalFlowRequiredForFlowType)
        # print(networkRateForFlowType)
        # print(totalFlowRequiredForFlowTypeOverWholeDuration)
    flowArrivalTimesByflowType = []
    for i in range (0, len(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB)):
        # data_uniform = uniform.rvs(size=totalFlowRequiredForFlowType[i], loc = 0, scale=duration)
        # flowArrivalTimesByflowType.append(data_uniform)
        # print("Per flow Flow volume"+str(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB[i]))
        # print("Required nbumber of flow "+str(totalFlowRequiredForFlowType[i]))

        for i in range (0, len(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB)):
            # numbPoints = scipy.stats.poisson( int(totalFlowRequiredForFlowType[i])).rvs()#Poisson number of points
            # #val = duration*scipy.stats.uniform.rvs(0,1,((numbPoints,1)))#x coordinates of Poisson points
            # val = duration*numbPoints

            val = poisson.rvs(lambdaForFlowType[i], size=totalFlowRequiredForFlowType[i])
            val = np.sort(val, axis=None)
            print("Poisson numbers" +str(val))
            arrivalTimes = Cumulative(val)
            print("ArrivalTimes "+str(arrivalTimes))
            flowArrivalTimesByflowType.append(arrivalTimes)

    return flowArrivalTimesByflowType


def Cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    return cu_list[1:]
# calculateFlowArrivalTimes(loadFactor=.3, duration = 200)


def makeDirectoryWithIndex(folderPath, accessRights):
    flag = False
    for i in range (0,1000):
        tempFolderPAth = folderPath+"-"+str(i)
        if not os.path.exists(tempFolderPAth):
            print("Folder path in else psection"+str(tempFolderPAth))
            os.mkdir(tempFolderPAth, accessRights)
            return i
    if (flag == False):
        print("Can not make folder : "+str(folderPath))
        print("Exiting")
        exit(1)
# for each src destination in stride pair deloy these flows
# def getL2StrdePeerHostName(hostIndex, leafSwitchIndex, podIndex , portCount):
#     peerHostIndex = int((int(hostIndex)+1+ int(portCount)/2) % (int(portCount)/2))
#     peerLeafSwitchIndex = int( (int(leafSwitchIndex)+1+ (int(portCount)/2)) % int((portCount)/2))
#     peerPodIndex = int(podIndex)
#     peerHostName = "h"+str(peerHostIndex)+"p"+str(peerPodIndex)+"l"+str(peerLeafSwitchIndex)
#     return peerHostName

def getPeerIndex(index):
    index = int(index)
    if(index == 0):
        return 1
    if(index == 1):
        return 2
    if(index == 2):
        return 3
    if(index == 3):
        return 0


def getL2StrdePeerHostName(hostIndex, leafSwitchIndex, podIndex , portCount):
    peerHostIndex = getPeerIndex(hostIndex)
    peerLeafSwitchIndex = getPeerIndex(leafSwitchIndex)
    peerPodIndex = int(podIndex)
    peerHostName = "h"+str(peerHostIndex)+"p"+str(peerPodIndex)+"l"+str(peerLeafSwitchIndex)
    return peerHostName

def l2StridePatternTestPairCreator(nameToHostMap, maxPortcountInSwitch):

    srcList = []
    destList=[]
    count = 0
    for srcHostName in nameToHostMap:
        srcHost = nameToHostMap.get(srcHostName)
        hostIndex, leafSwitchIndex, podIndex = srcHost.getLocationIndexes()
        peerName = getL2StrdePeerHostName(hostIndex, leafSwitchIndex, podIndex, maxPortcountInSwitch)
        peerHostObject = nameToHostMap.get(peerName)
        # if (srcHost!=None) and (peerHostObject != None) and (not(srcHost  in srcList)) and (not(srcHost  in destList)) and (not(peerName in srcList)) and (not(peerName  in destList)):
        if (srcHost!=None) and (peerHostObject != None) :
            srcList.append(srcHost)
            destList.append((peerHostObject))
            count = count+1
            print("Src: "+srcHostName+" peer host:"+peerName)

        if(count>=((len(nameToHostMap)))):
            break;


    return srcList, destList

def buildOneDeploymentPair(nameToHostMap, srcName, dstName, testCaseName, testStartDelay, flowsizeInpacket, trafficClass, rateInKBPS):
    src = nameToHostMap.get(srcName)
    dst = nameToHostMap.get(dstName)
    newDeploymentPair = tc.IPerfDeplymentPair(src, dst, src.getNextIPerf3ClientPort(),
                                              dst.getNextIPerf3ServerPort(), testCaseName = testCaseName,
                                              srcHostName=src.hostName, destHostName= dst.hostName,
                                              startTime=float(testStartDelay), flowSizeinPackets= flowsizeInpacket,
                                              trafficClass = trafficClass, bitrate = rateInKBPS)
    return newDeploymentPair

def getQoSTestDeploymentDeploymentPairs(nameToHostMap,testCaseName, testDuration,testStartDelay ):
    deploymentPairList = []
    deploymentPairList.append(buildOneDeploymentPair(nameToHostMap, srcName="h0p0l0", dstName="h0p0l2", testCaseName=testCaseName, testStartDelay=testStartDelay,
                           flowsizeInpacket = 8*testDuration, trafficClass = ConfigConst.QOS_TRAFFIC_CLASS[0], rateInKBPS= 10240))
    deploymentPairList.append(buildOneDeploymentPair(nameToHostMap, srcName="h1p0l0", dstName="h1p0l2", testCaseName=testCaseName, testStartDelay=testStartDelay,
                         flowsizeInpacket = 16*testDuration, trafficClass = ConfigConst.QOS_TRAFFIC_CLASS[1], rateInKBPS= 8192))

    # deploymentPairList.append(buildOneDeploymentPair(nameToHostMap, srcName="h2p0l0", dstName="h2p0l2", testCaseName=testCaseName, testStartDelay=testStartDelay,
    #                                                  flowsizeInpacket = 8*testDuration, trafficClass = ConfigConst.QOS_TRAFFIC_CLASS[0], rateInKBPS= 8192))
    # deploymentPairList.append(buildOneDeploymentPair(nameToHostMap, srcName="h3p0l0", dstName="h2p0l2", testCaseName=testCaseName, testStartDelay=testStartDelay,
    #                                                  flowsizeInpacket = 16*testDuration, trafficClass = ConfigConst.QOS_TRAFFIC_CLASS[1], rateInKBPS= 32768))
    return deploymentPairList

def getStrideDeploymentPairs(nameToHostMap,maxPortcountInSwitch,testCaseName, loadFactor, testDuration,testStartDelay ):
    # foreach scrc-dest-pair
    #       login to src
    #       foreach of the flows
    #               build corresponding cmdString and deploy
    srcList, destList= l2StridePatternTestPairCreator(nameToHostMap,maxPortcountInSwitch)
    # print("Srclist is ",srcList)
    # print("destList is ",destList)
    deploymentPairList= []

    if (len(srcList) != len(destList)):
        logger.error("Srclist and dest list is not equal in length. Printing them and exiting")
        logger.error(srcList)
        logger.error(destList)
        exit(1)
    else:
        flowArrivalTimesByflowType = calculateFlowArrivalTimes(loadFactor, testDuration)
        for i in range (0, len(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB)):
            totalFlowForThisFlowType = len(flowArrivalTimesByflowType[i])
            flowsizeAsPacketCount = math.ceil(((ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB[i]*1024)/(ConfigConst.PACKET_SIZE)))
            for j in range (0,totalFlowForThisFlowType):
                k = j % len(srcList)
                newDeploymentPair = tc.IPerfDeplymentPair(srcList[k], destList[k], srcList[k].getNextIPerf3ClientPort(),
                                  destList[k].getNextIPerf3ServerPort(),testCaseName = testCaseName,
                                  srcHostName=srcList[k].hostName, destHostName= destList[k].hostName,
                                  startTime= flowArrivalTimesByflowType[i][j]+float(testStartDelay),flowSizeinPackets= flowsizeAsPacketCount,
                                  trafficClass = ConfigConst.FLOW_TYPE_TRAFFIC_CLASS_TAG[i], bitrate = ConfigConst.FLOW_TYPE_BITRATE[i])
                deploymentPairList.append(newDeploymentPair)
        # testDurationScaled = loadFactor * 2 * testDuration
        # qosDeploymentPair = getQoSTestDeploymentDeploymentPairs(nameToHostMap,testCaseName, testDuration=testDurationScaled,testStartDelay= testStartDelay)
        # for k in qosDeploymentPair:
        #     deploymentPairList.append(k)
        # src = nameToHostMap.get("h0p0l0")
        # dst = nameToHostMap.get("h1p0l1")
        # flowSize = testDuration * ConfigConst.queueRateForSpineFacingPortsOfLeafSwitch
        # # print("Spoecial flow size is "+str(flowSize))
        # bitrate = ConfigConst.queueRateForSpineFacingPortsOfLeafSwitch * 1024
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                   dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                   srcHostName=src.hostName, destHostName= dst.hostName,
        #                   startTime= 10+float(testStartDelay),flowSizeinPackets= flowSize,
        #                   trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                                           dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                           srcHostName=src.hostName, destHostName= dst.hostName,
        #                                           startTime= 10+float(testStartDelay+testDuration/3),flowSizeinPackets= flowSize,
        #                                           trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                                           dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                           srcHostName=src.hostName, destHostName= dst.hostName,
        #                                           startTime= 10+float(testStartDelay+testDuration*2/3),flowSizeinPackets= flowSize,
        #                                           trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                                           dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                           srcHostName=src.hostName, destHostName= dst.hostName,
        #                                           startTime= 10+float(testStartDelay+testDuration),flowSizeinPackets= flowSize,
        #                                           trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # src = nameToHostMap.get("h0p0l2")
        # dst = nameToHostMap.get("h1p0l3")
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                   dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                   srcHostName=src.hostName, destHostName= dst.hostName,
        #                   startTime= 10+float(testStartDelay),flowSizeinPackets= flowSize,
        #                   trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                                           dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                           srcHostName=src.hostName, destHostName= dst.hostName,
        #                                           startTime= 10+float(testStartDelay+testDuration/3),flowSizeinPackets= flowSize,
        #                                           trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                                           dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                           srcHostName=src.hostName, destHostName= dst.hostName,
        #                                           startTime= 10+float(testStartDelay+testDuration*2/3),flowSizeinPackets= flowSize,
        #                                           trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)
        # newDeploymentPair = tc.IPerfDeplymentPair(src,dst, src.getNextIPerf3ClientPort(),
        #                                           dst.getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                           srcHostName=src.hostName, destHostName= dst.hostName,
        #                                           startTime= 10+float(testStartDelay+testDuration),flowSizeinPackets= flowSize,
        #                                           trafficClass = ConfigConst.tunnelTrafficClass, bitrate = bitrate)
        # deploymentPairList.append(newDeploymentPair)

        # i = 0
        # j=0
        # for i in range(0, len(srcList)):
        #     flowArrivalTimesByflowType = calculateFlowArrivalTimes(loadFactor, testDuration)
        #     for j in range (0, len(ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB)):
        #         flowsizeAsPacketCount = math.ceil(((ConfigConst.FLOW_TYPE_IDENTIFIER_BY_FLOW_VOLUME_IN_KB[j]*1024)/(ConfigConst.PACKET_SIZE)))
        #         for k in range (0, len(flowArrivalTimesByflowType[j])):
        #             flowArraivalTime = flowArrivalTimesByflowType[j][k]
        #             newDeploymentPair = tc.IPerfDeplymentPair(srcList[i], destList[i], srcList[i].getNextIPerf3ClientPort(),
        #                                                       destList[i].getNextIPerf3ServerPort(),testCaseName = testCaseName,
        #                                                       srcHostName=srcList[i].hostName, destHostName= destList[i].hostName,
        #                                                       startTime= flowArraivalTime+float(testStartDelay),flowSizeinPackets= flowsizeAsPacketCount,
        #                                                       trafficClass = ConfigConst.FLOW_TYPE_TRAFFIC_CLASS[j], bitrate = ConfigConst.FLOW_TYPE_BITRATE[j])
        #             deploymentPairList.append(newDeploymentPair)
        #             # print(newDeploymentPair.getServerCommand())
    return deploymentPairList

class TestCommandDeployer:

    def __init__(self,topologyConfigFilePath,resultFolder , clientPortStart,serverPortStart, testStartDelay):
        '''

        :param topologyConfigFilePath:
        :param testConfigFilePath:
        :param testStartDelay: This is a delay period for starting the tests. We need this to handle the delay in starting ssh sessions
        '''
        self.testStartDelay = testStartDelay
        self.serverPortStart = serverPortStart
        self.clientPortStart = clientPortStart
        print("Topology  config path is ", topologyConfigFilePath)
        self.nameToHostMap = tc.loadCFG(topologyConfigFilePath,self.clientPortStart, self.serverPortStart )
        self.resultFolder = resultFolder


    def setupTestCaseFolder(self):

        #Create folder for atoring result
        logger.info("Creating folder for test case")
        path = os.getcwd()
        access_rights = 0o777
        logger.info("Current working Directory is "+path)
        fh = None
        allcommandAsString= ""
        original_umask = 0
        testIterationNumber = "-"
        try:
            original_umask = os.umask(0)
            logger.info("Original mask is "+str(original_umask))
            folderTobecreated = confConst.TEST_RESULT_FOLDER
            makeDirectory(folderTobecreated, access_rights)
            folderTobecreated = folderTobecreated+ "/"+ str(self.resultFolder)
            makeDirectory(folderTobecreated, access_rights)
            self.resultFolder = folderTobecreated
            # logger.info("folderTobecreated is :"+folderTobecreated)
            # serverFolderTobecreated = folderTobecreated  + confConst.TEST_RESULT_FOLDER_SERVER
            # makeDirectory(serverFolderTobecreated, access_rights)
            # clientFolderTobecreated = folderTobecreated  + confConst.TEST_RESULT_FOLDER_CLIENT
            # makeDirectory(clientFolderTobecreated, access_rights)
            print("folder creation completed")
            os.umask(original_umask)
        except Exception as e:
            logger.error("Exception occured in creating folder for test case results. ", e)
        finally:
            if(fh != None):
                fh.close()
                print("Timer file closed ")

    def generateTestCommands(self, testCaseNAme,loadFactor,testDuration, maxPortcountInSwitch):
        deploymentPairsAsList = getStrideDeploymentPairs(nameToHostMap = self.nameToHostMap,maxPortcountInSwitch = maxPortcountInSwitch,testCaseName = testCaseNAme,
                                                         loadFactor=loadFactor, testDuration=testDuration, testStartDelay = self.testStartDelay)
        access_rights = 0o777
        self.testCaseNAme = testCaseNAme
        try:
            original_umask = os.umask(0)
            logger.info("Original mask is "+str(original_umask))
            folderTobecreated = confConst.TEST_RESULT_FOLDER+"/"+self.testCaseNAme

            print("folder creation completed")
            os.umask(original_umask)
        except Exception as e:
            logger.error("Exception occured in creating folder for test case results. ", e)

        try:
            original_umask = os.umask(0)
            fh = open(self.resultFolder + "/"+testCaseNAme+".serverdat", 'w+')
            for d in deploymentPairsAsList:
                fh.write(str(d.getServerCommand()))
                fh.write("\n")
            os.umask(original_umask)
        except Exception as e:
                logger.error("Exception occured in creating serverside flow scheduler configuration for . "+testCaseNAme+". Exception is ", e)
        finally:
            if(fh != None):
                fh.close()
                print("Serverdat file closed ")
        try:
            original_umask = os.umask(0)
            fh = open(self.resultFolder + "/"+testCaseNAme+".clientdat", 'w+')
            for d in deploymentPairsAsList:
                fh.write(str(d.getCleintCommand()))
                fh.write("\n")
            os.umask(original_umask)
        except Exception as e:
            logger.error("Exception occurred in creating cleintside flow scheduler configuration for . "+testCaseNAme+". Exception is ", e)
        finally:
            if(fh != None):
                fh.close()
                print("clientdat file closed ")




if __name__ == "__main__":

    # Real deployment configuration
    #This is always the topology configuration.
    topologyConfigFilePath =  confConst.TOPOLOGY_CONFIG_FILE
    testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
                        serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    testEvaluator.setupTestCaseFolder()
    testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_0.2",loadFactor=0.2,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORT_COUNT/2)

    #--------------------

    testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
                                        serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    testEvaluator.setupTestCaseFolder()
    testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_0.4",loadFactor=0.4,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORT_COUNT/2)

    #--------------------
    testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
                                        serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    testEvaluator.setupTestCaseFolder()
    testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_0.6",loadFactor=0.5,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORT_COUNT/2)

    #--------------------
    testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
                                        serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    testEvaluator.setupTestCaseFolder()
    testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_0.7",loadFactor=0.7,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORT_COUNT/2)

    #--------------------
    testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
                                        serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    testEvaluator.setupTestCaseFolder()
    testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_0.8",loadFactor=0.8,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORT_COUNT/2)

    #--------------------
    testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
                                        serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    testEvaluator.setupTestCaseFolder()
    testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_1.0",loadFactor=1,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORT_COUNT/2)


    # #--------------------
    # testEvaluator = TestCommandDeployer(topologyConfigFilePath = confConst.TOPOLOGY_CONFIG_FILE,resultFolder = "FlowInfos" , clientPortStart=confConst.IPERF3_CLIENT_PORT_START,
    #                                     serverPortStart=confConst.IPERF3_SERVER_PORT_START, testStartDelay=10)
    # testEvaluator.setupTestCaseFolder()
    # testEvaluator.generateTestCommands( testCaseNAme= "WebSearchWorkLoad_load_factor_2.0",loadFactor=2.0,testDuration=200,maxPortcountInSwitch=ConfigConst.MAX_PORTS_IN_SWITCH/2)
