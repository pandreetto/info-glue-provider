# Copyright (c) Members of the EGEE Collaboration. 2004. 
# See http://www.eu-egee.org/partners/ for details on the copyright
# holders.  
#
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
#
#     http://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.


import sys
import os
import stat
import re
import tempfile
import socket
from threading import Thread

from GLUEInfoProvider import CommonUtils


class SiteInfoHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.errList = list()
        self.mRegex = re.compile('([^:]+):([^,]+),(.+)')
        
        self.ceParamTable = dict()
        self.qParamTable = dict()
        self.voParamTable = dict()
        self.scParamTable = dict()
        
        self.ceHost = socket.getfqdn()
        self.cePort = 8443
        self.compServiceID = None
        self.siteName = None
        self.jobmanager = None
        self.batchsys = None
        self.batchsysVer = None
        self.softDir = 'Undefined'
        self.ceDataDir = 'unset'
        self.argusEnabled = True

        self.clusterHost = None
        self.clusterId = None
        self.clusterName = None
        self.clusterSite = None
        self.clusterCEList = list()
        
        self.capabilities = list()
        self.ruleTable = CommonUtils.ResourceRuleTable()
        
        self.voParams = dict()
        self.resourceTable = dict()
        # temporary register the "anonymous" resource
        self.resourceTable['--'] = CommonUtils.CEResource()
        
        self.seAccess = dict()      # one item per SE host!!
        self.seRank = 1
        
        self.wAreaShared = None
        self.wAreaGuaranteed = None
        self.wAreaTotal = -1
        self.wAreaFree = -1
        self.wAreaLifeTime = -1
        self.wAreaMultiSlotTotal = -1
        self.wAreaMultiSlotFree = -1
        self.wAreaMultiSlotLifeTime = -1
        

    def setStream(self, stream):
        self.stream = stream

    def run(self):
    
        line = self.stream.readline()
        
        while line:
            try:
            
                parsed = CommonUtils.pRegex.match(line)
                if not parsed:
                    continue
                
                key = parsed.group(1)
                value = parsed.group(2).strip()
                
                if key.startswith('PARAM_CE_'):
                    self.ceParamTable[key[9:]] = value
                    continue
                
                if key.startswith('PARAM_QUEUE_'):
                    self.qParamTable[key[12:]] = value
                    continue
                
                if key.startswith('PARAM_VO_'):
                    self.voParamTable[key[9:]] = value
                    continue
                
                if key.startswith('PARAM_SC_'):
                    self.scParamTable[key[9:]] = value
                    continue
                
                if key == 'CE_HOST':
                    self.ceHost = value
                    continue

                if key == 'COMPUTING_SERVICE_ID':
                    self.compServiceID = value
                    continue

                if key == 'SITE_NAME':
                    self.siteName = value
                    continue
                
                if key == 'JOB_MANAGER':
                    self.jobmanager = value
                    continue
                
                if key == 'CE_BATCH_SYS':
                    self.batchsys = value
                    continue
                
                if key == 'BATCH_VERSION':
                    self.batchsysVer = value
                    continue

                if self.parseCEHostSection(key, value):
                    continue
                
                if key == 'CE_DATADIR':
                    self.ceDataDir = value
                    continue

                if key == 'CE_CAPABILITY':
                    self.capabilities += value.strip('\'"').split()
                    continue

                if self.parseOldSubClusterVars(key, value):
                    continue
                    
                if self.parseVOSection(key, value):
                    continue
                    
                if key == 'CLUSTERS' and len(value.split()) > 1:
                    self.errList.append("Multiple clusters not supported")
                    continue
                
                if self.parseClusterSection(key, value):
                    continue
                    
                if self.parseSubClusterSection(key, value):
                    continue

                if key == 'SE_LIST':
                    for seItem in value.strip('\'"').split():
                        self.seAccess[seItem] = CommonUtils.SEData(seItem)
                        self.seAccess[seItem].rank = self.seRank
                        self.seRank += 1
                    continue

                if self.parseSEAccess(key, value):
                    continue
                    
                if self.parseWorkingArea(key, value):
                    continue
                    
                if key == 'USE_ARGUS':
                    self.argusEnabled = value.lower() == 'yes'
                
                if key == 'CREAM_CLUSTER_MODE' and value.lower() == 'no':
                    self.clusterHost = None
                
            finally:
                line = self.stream.readline()

        #post processing
        if not self.clusterId:
            self.clusterId = self.ceHost
        if not self.clusterName:
            self.clusterName = self.ceHost
        if not self.clusterSite:
            self.clusterSite = self.siteName
            
        if len(self.resourceTable) > 1:
            #remove anonymous resource
            del(self.resourceTable['--'])
        else:
            self.resourceTable['--'].id = self.ceHost
            self.resourceTable['--'].name = self.ceHost
            self.resourceTable['--'].tmpDir = '/tmp'
            self.resourceTable['--'].WNDir = '/tmp'

        #
        # TODO merge resource tags from files (replace lcg-info-dynamic-software)
        #
        
        if not self.compServiceID:
            self.compServiceID = self.ceHost + '_ComputingElement'
        
        if not self.batchsys:
            self.batchsys = self.jobmanager

    def parseCEHostSection(self, key, value):
    
        if not key.startswith('CE_HOST_'):
            return False
    
        if key.endswith('_CE_AccessControlBaseRule'):
            idx = key.find('_QUEUE_')
            if idx < 0:
                return True
                
            queueNorm = key[idx+7:-25]
            hostNorm = key[8:idx]
            
            voRawList = value.strip('\'"').split()
            
            for vogrp in voRawList:
                self.ruleTable.add(self.ceParamTable[hostNorm], 
                                   self.qParamTable[queueNorm], 
                                   CommonUtils.VOData(vogrp))
            
            return True
                     
        if key.endswith('_CE_InfoJobManager'):
            self.jobmanager = value
        
        return True


    def parseVOSection(self, key, value):
    
        if not key.startswith('VO_'):
            return False
    
        if key == 'VO_SW_DIR':
            self.softDir = value
            return True

        if key.endswith('_SW_DIR'):
        
            voName = self.voParamTable[key[3:-7]]
            if not voName in self.voParams:
                self.voParams[voName] = CommonUtils.VOParams()
            self.voParams[voName].softDir = value
                       
        elif key.endswith('_DEFAULT_SE'):
            voName = self.voParamTable[key[3:-11]]
            if not voName in self.voParams:
                self.voParams[voName] = CommonUtils.VOParams()
            self.voParams[voName].defaultSE = value
        
        return True
            
    def parseClusterSection(self, key, value):

        if not key.startswith('CLUSTER_'):
            return False
    
        if key == 'CLUSTER_HOST':
            self.clusterHost = value
            return True

        if key.endswith('_CLUSTER_UniqueID'):
            self.clusterId = value
            return True

        if key.endswith('_CLUSTER_Name'):
            self.clusterName = value
            return True

        if key.endswith('_SITE_UniqueID'):
            self.clusterSite = value
            return True

        if key.endswith('_CE_HOSTS'):
            self.clusterCEList += value.strip('\'"').split()
            return True

        if key.endswith('_SUBCLUSTERS'):
            for scId in value.strip('\'"').split():
                self.resourceTable[scId] = CommonUtils.CEResource()

        return True
        
    def parseSubClusterSection(self, key, value):
    
        if not key.startswith('SUBCLUSTER_'):
            return False
        
        if key.endswith('_SUBCLUSTER_UniqueID'):
            scId = self.scParamTable[key[11:-20]]
            self.resourceTable[scId].id = value
            return True

        if key.endswith('_HOST_ApplicationSoftwareRunTimeEnvironment'):
            scId = self.scParamTable[key[11:-43]]
            for item in value.strip('$\'"').split():
                if item.endswith("\\n"):
                    item = item[:-2]
                if len(item) > 0:
                    self.resourceTable[scId].runtimeEnv.append(item)
            return True

        if key.endswith('_HOST_ArchitectureSMPSize'):
            scId = self.scParamTable[key[11:-25]]
            self.resourceTable[scId].smpSize = int(value)
            return True

        if key.endswith('_HOST_ArchitecturePlatformType'):
            scId = self.scParamTable[key[11:-30]]
            self.resourceTable[scId].osArch = value
            return True

        if key.endswith('_HOST_BenchmarkSF00'):
            scId = self.scParamTable[key[11:-19]]
            self.resourceTable[scId].benchSF00 = float(value)
            return True

        if key.endswith('_HOST_BenchmarkSI00'):
            scId = self.scParamTable[key[11:-19]]
            self.resourceTable[scId].benchSI00 = float(value)
            return True

        if key.endswith('_HOST_MainMemoryRAMSize'):
            scId = self.scParamTable[key[11:-23]]
            self.resourceTable[scId].mainMemSize = int(value)
            return True

        if key.endswith('_HOST_MainMemoryVirtualSize'):
            scId = self.scParamTable[key[11:-27]]
            self.resourceTable[scId].mainVirtSize = int(value)
            return True

        if key.endswith('_HOST_NetworkAdapterInboundIP'):
            scId = self.scParamTable[key[11:-29]]
            self.resourceTable[scId].inBound = value.upper() == 'TRUE'
            return True

        if key.endswith('_HOST_NetworkAdapterOutboundIP'):
            scId = self.scParamTable[key[11:-30]]
            self.resourceTable[scId].outBound  = value.upper() == 'TRUE'
            return True

        if key.endswith('_HOST_OperatingSystemName'):
            scId = self.scParamTable[key[11:-25]]
            self.resourceTable[scId].osName = value
            return True

        if key.endswith('_HOST_OperatingSystemRelease'):
            scId = self.scParamTable[key[11:-28]]
            self.resourceTable[scId].osRelease = value
            return True

        if key.endswith('_HOST_OperatingSystemVersion'):
            scId = self.scParamTable[key[11:-28]]
            self.resourceTable[scId].osVersion = value
            return True

        if key.endswith('_HOST_ProcessorClockSpeed'):
            scId = self.scParamTable[key[11:-25]]
            self.resourceTable[scId].procSpeed = int(value)
            return True

        if key.endswith('_HOST_ProcessorModel'):
            scId = self.scParamTable[key[11:-20]]
            self.resourceTable[scId].procModel = value
            return True

        if key.endswith('_HOST_ProcessorOtherDescription'):
            scId = self.scParamTable[key[11:-31]]
            self.resourceTable[scId].procDescr = value
            return True

        if key.endswith('_HOST_ProcessorVendor'):
            scId = self.scParamTable[key[11:-21]]
            self.resourceTable[scId].procVendor = value
            return True

        if key.endswith('_SUBCLUSTER_Name'):
            scId = self.scParamTable[key[11:-16]]
            self.resourceTable[scId].name = value
            return True

        if key.endswith('_SUBCLUSTER_PhysicalCPUs'):
            scId = self.scParamTable[key[11:-24]]
            self.resourceTable[scId].phyCPU = int(value)
            return True

        if key.endswith('_SUBCLUSTER_LogicalCPUs'):
            scId = self.scParamTable[key[11:-23]]
            self.resourceTable[scId].logCPU = int(value)
            return True

        if key.endswith('_SUBCLUSTER_TmpDir'):
            scId = self.scParamTable[key[11:-18]]
            self.resourceTable[scId].tmpDir = value
            return True

        if key.endswith('_SUBCLUSTER_WNTmpDir'):
            scId = self.scParamTable[key[11:-20]]
            self.resourceTable[scId].WNDir = value
            return True

        return True
        
    def parseOldSubClusterVars(self, key, value):
    
        if key == 'CE_RUNTIMEENV':
            for item in value.strip('$\'"').split():
                if item.endswith("\\n"):
                    item = item[:-2]
                if len(item) > 0:
                    self.resourceTable['--'].runtimeEnv.append(item)
            return True
        
        if key == 'CE_SMPSIZE':
            self.resourceTable['--'].smpSize = int(value)
            return True
        
        if key == 'CE_OS_ARCH':
            self.resourceTable['--'].osArch = value
            return True
        
        if key == 'CE_SF00':
            self.resourceTable['--'].benchSF00 = float(value)
            return True
        
        if key == 'CE_SI00':
            self.resourceTable['--'].benchSI00 = float(value)
            return True
        
        if key == 'CE_MINPHYSMEM':
            self.resourceTable['--'].mainMemSize = int(value)
            return True
        
        if key == 'CE_MINVIRTMEM':
            self.resourceTable['--'].mainVirtSize = int(value)
            return True
        
        if key == 'CE_INBOUNDIP':
            self.resourceTable['--'].inBound = value.upper() == 'TRUE'
            return True
        
        if key == 'CE_OUTBOUNDIP':
            self.resourceTable['--'].outBound  = value.upper() == 'TRUE'
            return True
        
        if key == 'CE_OS':
            self.resourceTable['--'].osName = value
            return True
        
        if key == 'CE_OS_RELEASE':
            self.resourceTable['--'].osRelease = value
            return True
        
        if key == 'CE_OS_VERSION':
            self.resourceTable['--'].osVersion = value
            return True
        
        if key == 'CE_CPU_SPEED':
            self.resourceTable['--'].procSpeed = int(value)
            return True
        
        if key == 'CE_CPU_MODEL':
            self.resourceTable['--'].procModel = value
            return True
        
        if key == 'CE_CPU_VENDOR':
            self.resourceTable['--'].procVendor = value
            return True
        
        if key == 'CE_OTHERDESCR':
            self.resourceTable['--'].procDescr = value
            return True
        
        if key == 'CE_PHYSCPU':
            self.resourceTable['--'].phyCPU = int(value)
            return True
        
        if key == 'CE_LOGCPU':
            self.resourceTable['--'].logCPU = int(value)
            return True
                
        return False


    def parseSEAccess(self, key, value):
        if key <> 'SE_MOUNT_INFO_LIST':
            return False
        
        if value.lower() == 'none':
            return True
        
        for mItem in value.strip('\'"').split():
            parsed = self.mRegex.match(mItem)
            if parsed:
                seItem = parsed.group(1)
                if not seItem in self.seAccess:
                    self.seAccess[seItem] = CommonUtils.SEData(seItem)
                    self.seAccess[seItem].rank = self.seRank
                    self.seRank += 1
                self.seAccess[seItem].export = parsed.group(2)
                self.seAccess[seItem].mount = parsed.group(3)
                
        return True

    def parseWorkingArea(self, key, value):
        if not key.startswith('WORKING_AREA_'):
            return False
        
        if key == 'WORKING_AREA_SHARED':
            self.wAreaShared = value.lower() == 'true'
        elif key == 'WORKING_AREA_GUARANTEED':
            self.wAreaGuaranteed = value.lower() == 'true'
        elif key == 'WORKING_AREA_TOTAL':
            self.wAreaTotal = int(value)
        elif key == 'WORKING_AREA_FREE':
            self.wAreaFree = int(value)
        elif key == 'WORKING_AREA_LIFETIME':
            self.wAreaLifeTime = int(value)
        elif key == 'WORKING_AREA_MULTISLOT_TOTAL':
            self.wAreaMultiSlotTotal = int(value)
        elif key == 'WORKING_AREA_MULTISLOT_FREE':
            self.wAreaMultiSlotFree = int(value)
        elif key == 'WORKING_AREA_MULTISLOT_LIFETIME':
            self.wAreaMultiSlotLifeTime = int(value)
            
        return True


    def clusterStandAloneMode(self):
        return self.clusterHost and not self.clusterHost in self.ruleTable.getCEHostList()
    
    def creamStandAloneMode(self, creamHost):
        return self.clusterHost and self.clusterHost <> creamHost
    
    def clusterMixedMode(self, creamHost):
        return self.clusterHost and self.clusterHost == creamHost
    
    def noClusterMode(self):
        return not self.clusterHost

def parse(config):
    
    if not 'siteinfo-defs' in config:
        raise Exception('Missing site-info definition files')
    
    siteInfoList = config['siteinfo-defs'].split(':')
    
    if 'vo-defs-dir' in config:
        voInfoFileList = os.listdir(config['vo-defs-dir'])
    else:
        voInfoFileList = list()
    
    container = SiteInfoHandler()
    outFile = None
    tempExec = None
    
    try:
    
        tmpfd, tempExec = tempfile.mkstemp(".sh", "print-siteinfo-defs", '/tmp')

        inFile = None
        
        try:
            outFile = os.fdopen(tmpfd,'w+b')
            for fileItem in siteInfoList:
                inFile = open(fileItem)
                for line in inFile:
                    outFile.write(line)
                inFile.close()
        
            for fileItem in voInfoFileList:
                inFile = open(os.path.join(config['vo-defs-dir'], fileItem))
                for line in inFile:
                    tmps = line.strip()
                    if len(tmps) > 0 and not tmps.startswith('#'):
                        normName = fileItem.replace('.', '_').replace('-', '_').upper()
                        outFile.write('VO_%s_%s' % (normName, line))
                inFile.close()

            outFile.write('''
################################################################################
# Normalization table
# for host names, vo names and queues
# see https://twiki.cern.ch/twiki/bin/view/LCG/Site-info_configuration_variables
################################################################################

for CLUSTER_RAW in ${CLUSTERS}; do
    CLUSTER=`echo ${CLUSTER_RAW} | sed -e 's/-/_/g' -e 's/\./_/g' | tr '[:lower:]' '[:upper:]'`
done

if [ ! "x${CE_HOST}" == "x" ] ; then
    CE_name=`echo ${CE_HOST} | sed -e 's/-/_/g' -e 's/\./_/g' | tr '[:upper:]' '[:lower:]'`
    echo "PARAM_CE_${CE_name}=${CE_HOST}"
fi

for CE_RAW in `eval echo "\\\$CLUSTER_${CLUSTER}_CE_HOSTS"`; do
    CE_name=`echo ${CE_RAW} | sed -e 's/-/_/g' -e 's/\./_/g' | tr '[:upper:]' '[:lower:]'`
    echo "PARAM_CE_${CE_name}=${CE_RAW}"
    
    for QUEUE_RAW in `eval echo "\\\$CE_HOST_${CE_name}_QUEUES"`; do
        QUEUE_name=`echo ${QUEUE_RAW} | sed -e 's/[\.-]/_/g' |  tr '[:lower:]' '[:upper:]'`
        echo "PARAM_QUEUE_${QUEUE_name}=${QUEUE_RAW}"
    done

done

for SCLUSTER_RAW in `eval echo "\\\$CLUSTER_${CLUSTER}_SUBCLUSTERS"`; do
    SCLUSTER_name=`echo ${SCLUSTER_RAW} | sed -e 's/-/_/g' -e 's/\./_/g' | tr '[:lower:]' '[:upper:]'`
    echo "PARAM_SC_${SCLUSTER_name}=${SCLUSTER_RAW}"
done

for VO_RAW in `eval echo "\\\$VOS"`; do
    VO_name=`echo ${VO_RAW} | sed -e 's/-/_/g' -e 's/\./_/g' | tr '[:lower:]' '[:upper:]'`
    echo "PARAM_VO_${VO_name}=${VO_RAW}"
done

set

''')
        
        finally:
            if inFile:
                inFile.close()
            if outFile:
                outFile.close()
    
        os.chmod(tempExec, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        
        CommonUtils.parseStream(tempExec, container)
    
    finally:
        os.remove(tempExec)
    
    return container








