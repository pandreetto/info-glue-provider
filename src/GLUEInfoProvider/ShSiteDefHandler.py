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
from threading import Thread

from GLUEInfoProvider import CommonUtils


class SiteInfoHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.errList = list()
        self.pRegex = re.compile('^\s*([^=\s]+)\s*=([^$]+)$')
        
        self.ceHost = None
        self.cePort = 8443
        self.siteName = None
        self.jobmanager = None
        self.batchsys = None
        self.softDir = 'Undefined'
        self.ceDataDir = 'unset'
        
        self.queues = dict()
        self.seList = list()
        self.capabilities = list()
        self.acbrTable = dict()
        
        self.voParams = dict()

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

                if key == 'SITE_NAME':
                    self.siteName = value
                    continue
                
                if key == 'JOB_MANAGER':
                    self.jobmanager = value
                    continue
                
                if key == 'CE_BATCH_SYS':
                    self.batchsys = value
                    continue

                if key.startswith('CE_HOST_'):
                    self.parseHostSection(key, value)
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

                if key.startswith('VOPARAMS'):
                    self.parseVOSection(key, value)
                    continue

            finally:
                line = self.stream.readline()


    def parseHostSection(self, key, value):
    
        if key.endswith('QUEUES'):
            self.queues[self.ceHost] = value.strip('\'"').split()
            
        if key.endswith('CE_AccessControlBaseRule'):
            idx = key.find('QUEUE')
            if idx < 0:
                return
                
            queueUC = key[idx+6:-25]
            #
            # The variable **QUEUES must be read before ACBR !!!
            #
            for tmpq in self.queues[self.ceHost]:
                if tmpq.upper() == queueUC:
                    voRawList = value.strip('\'"').split()
                    self.acbrTable[(self.ceHost, tmpq)] = map(CommonUtils.VOData, voRawList)
                     
        if key.endswith('CE_InfoJobManager'):
            self.jobmanager = value


    def parseVOSection(self, key, value):
    
        idx = key.find('_', 9)
        voLC = key[9:idx]
        
        if not voLC in self.voParams:
            self.voParams[voLC] = CommonUtils.VOParams()
    
        if key.endswith('SW_DIR'):
            self.voParams[voLC].softDir = value
        elif key.endswith('DEFAULT_SE'):
            self.voParams[voLC].defaultSE = value
            
            




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








