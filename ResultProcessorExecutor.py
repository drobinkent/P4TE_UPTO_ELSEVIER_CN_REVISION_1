#Sole task of this module is to call the resulr processor and that's all

import testAndMeasurement.ResultProcessor as rp
import numpy as np
import ConfigConst as CC
import sys

from testAndMeasurement.ResultParsers import ConfigLoader

if __name__ == '__main__':
    if(len(sys.argv) <4):
        print("Need to pass 5 parameters: Iperf result Folder1, Iperf result folder 2,  alg 1 name, alg2 name, where to store the figure and results")
        config = ConfigLoader(CC.TOPOLOGY_CONFIG_FILE)
        print("Link utilization for P4TE")
        # val = rp.upwardLinkUtilizationAnalyzer(config=config, folderPath = "./testAndMeasurement/TEST_RESULTS/P4TE/l2strideSmallLarge/")
        # print(val)
        # print("Link utilization for ecmp")
        # val = rp.upwardLinkUtilizationAnalyzer(config=config, folderPath = "./testAndMeasurement/TEST_RESULTS/ecmp/l2strideSmallLarge/")
        # print(val)
    else:
        print("Parameters to result processor are: "+str(sys.argv))
        rp.processResults(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

