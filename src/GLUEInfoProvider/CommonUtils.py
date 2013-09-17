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
import re
import subprocess
import traceback
import time
import ConfigParser
from threading import Thread

providerName = 'info-glue-provider'
providerVersion = '1.0'

pRegex = re.compile('^\s*([^=\s]+)\s*=\s*(.+)$')

class ErrorHandler(Thread):

    def __init__(self, err_stream):
        Thread.__init__(self)
        self.stream = err_stream
        self.message = ""
    
    def run(self):
        line = self.stream.readline()
        while line:
            self.message = self.message + line
            line = self.stream.readline()


def parseStream(cmd, container):

    processErr = None
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        container.setStream(process.stdout)
        stderr_thread = ErrorHandler(process.stderr)
    
        container.start()
        stderr_thread.start()
    
        ret_code = process.wait()
    
        container.join()
        stderr_thread.join()
        
        if ret_code <> 0:
            processErr = stderr_thread.message
            
        if len(container.errList) > 0:
            processErr = container.errList[0]

    except:
        raise Exception(errorMsgFromTrace())

    if processErr:
        raise Exception(processErr)

def readConfigFile(configFile):

    conffile = None
    config = dict()
    
    try:
    
        conffile = open(configFile)
        tmpConf = ConfigParser.ConfigParser()
        tmpConf.readfp(conffile)
            
        if tmpConf.has_option('Main','outputformat'):
            config['outputformat'] = tmpConf.get('Main', 'outputformat')
                
        if tmpConf.has_option('Main','siteinfo-defs'):
            config['siteinfo-defs'] = tmpConf.get('Main', 'siteinfo-defs')

        if tmpConf.has_option('Main','vo-defs-dir'):
            config['vo-defs-dir'] = tmpConf.get('Main', 'vo-defs-dir')

    finally:
        if conffile:
            conffile.close()

    if not "outputformat" in config:
        if "GlueFormat" in config:
            config["outputformat"] = config["GlueFormat"]
        else:
            config["outputformat"] = "both"
    
    if config["outputformat"] not in ["glue1", "glue2", "both"]:
        raise Exception("FATAL: Unknown output format specified in config file:%s" % config["outputformat"])

    return config


def errorMsgFromTrace():

    etype, evalue, etraceback = sys.exc_info()
    trMessage = ''
    
    trList = traceback.extract_tb(etraceback)
    for trArgs in trList:
        if 'GLUEInfoProvider' in trArgs[0]:
            trMessage = '%s: %d' % (trArgs[0], trArgs[1])
    
    result = '%s (%s)' % (evalue, trMessage)
    return result

def getNow():

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class VOData:

    def __init__(self, voRaw):
        tmpl = voRaw.split('/')
        if len(tmpl) == 1 and len(tmpl[0]) > 0:
            self.voname = tmpl[0]
            self.fqan = None
        elif len(tmpl) > 1:
            self.voname = tmpl[0]
            self.fqan = voRaw
            
    def __repr__(self):
        if self.fqan:
            return 'VOMS:' + self.fqan
        return 'VO:' + self.voname
    
    def __cmp__(self, other):
        if self.fqan:
            return cmp(self.fqan, other.fqan)
        return cmp(self.voname, other.voname)
    
    def __hash__(self):
        if self.fqan:
            return hash(self.fqan)
        return hash(self.voname)
        
    def getNormName(self):
        if self.fqan:
            return self.fqan.replace('=','_')
        else:
            return self.voname
            
    def getVOName(self):
        return self.voname

class VOParams:

    def __init__(self):
        self.softDir = None
        self.defaultSE = None

class CEResource:

    def __init__(self):
        self.id = None
        self.name = None
        self.runtimeEnv = list()
        self.smpSize = 0
        self.benchSF00 = 0
        self.benchSI00 = 0
        self.mainMemSize = 0
        self.mainVirtSize = 0
        self.inBound = False
        self.outBound = True
        self.osName = None
        self.osArch = None
        self.osRelease = None
        self.osVersion = None
        self.procSpeed = 0
        self.procModel = None
        self.procVendor = None
        self.procDescr = None
        self.phyCPU = 0
        self.logCPU = 0
        self.tmpDir = None
        self.WNDir = None
        







