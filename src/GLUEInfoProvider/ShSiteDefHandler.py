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
        self.pRegex = re.compile('^\s*([^=\s]+)\s*=\s*(.+)$')
        self.mRegex = re.compile('([^:]+):([^,]+),(.+)')
        
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
        
        self.queues = dict()
        self.seList = list()
        self.capabilities = list()
        self.acbrTable = dict()
        
        self.voParams = dict()
        self.resourceTable = dict()
        # temporary register the "anonymous" resource
        self.resourceTable['--'] = CommonUtils.CEResource()
        
        self.seAccess = dict()
        
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
            
                parsed = self.pRegex.match(line)
                if not parsed:
                    continue
                
                key = parsed.group(1)
                value = parsed.group(2).strip()
                
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
                
                if key == 'VO_SW_DIR':
                    self.softDir = value
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
                    self.seList += value.strip('\'"').split()
                    continue

                if self.parseSEAccess(key, value):
                    continue
                    
                if self.parseWorkingArea(key, value):
                    continue
                    
                if key == 'USE_ARGUS':
                    self.argusEnabled = value.lower() == 'yes'
                
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
    
        if key.endswith('QUEUES'):
            self.queues[self.ceHost] = value.strip('\'"').split()
            return True
            
        if key.endswith('CE_AccessControlBaseRule'):
            idx = key.find('QUEUE')
            if idx < 0:
                return True
                
            queueUC = key[idx+6:-25]
            #
            # The variable **QUEUES must be read before ACBR !!!
            #
            for tmpq in self.queues[self.ceHost]:
                if tmpq.upper() == queueUC:
                    voRawList = value.strip('\'"').split()
                    self.acbrTable[(self.ceHost, tmpq)] = map(CommonUtils.VOData, voRawList)
            return True
                     
        if key.endswith('CE_InfoJobManager'):
            self.jobmanager = value
        
        return True


    def parseVOSection(self, key, value):
    
        if not key.startswith('VOPARAMS_'):
            return False
    
        idx = key.find('_', 9)
        voLC = key[9:idx]
        
        if not voLC in self.voParams:
            self.voParams[voLC] = CommonUtils.VOParams()
    
        if key.endswith('SW_DIR'):
            self.voParams[voLC].softDir = value           
        elif key.endswith('DEFAULT_SE'):
            self.voParams[voLC].defaultSE = value
        
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
                newId = scId.replace('-','_').replace('.','_').upper()
                self.resourceTable[newId] = CommonUtils.CEResource()

        return True
        
    def parseSubClusterSection(self, key, value):
    
        if not key.startswith('SUBCLUSTER_'):
            return False
        
        if key.endswith('_SUBCLUSTER_UniqueID'):
            scId = key[11:-20]
            self.resourceTable[scId].id = value
            return True

        if key.endswith('_HOST_ApplicationSoftwareRunTimeEnvironment'):
            scId = key[11:-43]
            for item in value.strip('$\'"').split():
                if item.endswith("\\n"):
                    item = item[:-2]
                if len(item) > 0:
                    self.resourceTable[scId].runtimeEnv.append(item)
            return True

        if key.endswith('_HOST_ArchitectureSMPSize'):
            scId = key[11:-25]
            self.resourceTable[scId].smpSize = int(value)
            return True

        if key.endswith('_HOST_ArchitecturePlatformType'):
            scId = key[11:-30]
            self.resourceTable[scId].osArch = value
            return True

        if key.endswith('_HOST_BenchmarkSF00'):
            scId = key[11:-19]
            self.resourceTable[scId].benchSF00 = float(value)
            return True

        if key.endswith('_HOST_BenchmarkSI00'):
            scId = key[11:-19]
            self.resourceTable[scId].benchSI00 = float(value)
            return True

        if key.endswith('_HOST_MainMemoryRAMSize'):
            scId = key[11:-23]
            self.resourceTable[scId].mainMemSize = int(value)
            return True

        if key.endswith('_HOST_MainMemoryVirtualSize'):
            scId = key[11:-27]
            self.resourceTable[scId].mainVirtSize = int(value)
            return True

        if key.endswith('_HOST_NetworkAdapterInboundIP'):
            scId = key[11:-29]
            self.resourceTable[scId].inBound = value.upper() == 'TRUE'
            return True

        if key.endswith('_HOST_NetworkAdapterOutboundIP'):
            scId = key[11:-30]
            self.resourceTable[scId].outBound  = value.upper() == 'TRUE'
            return True

        if key.endswith('_HOST_OperatingSystemName'):
            scId = key[11:-25]
            self.resourceTable[scId].osName = value
            return True

        if key.endswith('_HOST_OperatingSystemRelease'):
            scId = key[11:-28]
            self.resourceTable[scId].osRelease = value
            return True

        if key.endswith('_HOST_OperatingSystemVersion'):
            scId = key[11:-28]
            self.resourceTable[scId].osVersion = value
            return True

        if key.endswith('_HOST_ProcessorClockSpeed'):
            scId = key[11:-25]
            self.resourceTable[scId].procSpeed = int(value)
            return True

        if key.endswith('_HOST_ProcessorModel'):
            scId = key[11:-20]
            self.resourceTable[scId].procModel = value
            return True

        if key.endswith('_HOST_ProcessorOtherDescription'):
            scId = key[11:-31]
            self.resourceTable[scId].procDescr = value
            return True

        if key.endswith('_HOST_ProcessorVendor'):
            scId = key[11:-21]
            self.resourceTable[scId].procVendor = value
            return True

        if key.endswith('_SUBCLUSTER_Name'):
            scId = key[11:-16]
            self.resourceTable[scId].name = value
            return True

        if key.endswith('_SUBCLUSTER_PhysicalCPUs'):
            scId = key[11:-24]
            self.resourceTable[scId].phyCPU = int(value)
            return True

        if key.endswith('_SUBCLUSTER_LogicalCPUs'):
            scId = key[11:-23]
            self.resourceTable[scId].logCPU = int(value)
            return True

        if key.endswith('_SUBCLUSTER_TmpDir'):
            scId = key[11:-18]
            self.resourceTable[scId].tmpDir = value
            return True

        if key.endswith('_SUBCLUSTER_WNTmpDir'):
            scId = key[11:-20]
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
            
        for mItem in value.strip('\'"').split():
            parsed = self.mRegex.match(mItem)
            if parsed:
                self.seAccess[parsed.group(1)] = '%s,%s' % (parsed.group(3), parsed.group(2))
                
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
                        outFile.write('VOPARAMS_%s_%s' % (fileItem.lower(), line))
                inFile.close()

            outFile.write('\nset\n')
        
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








