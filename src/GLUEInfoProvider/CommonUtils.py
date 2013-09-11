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
import ConfigParser
from threading import Thread

pRegex = re.compile('^\s*([^=\s]+)\s*=([^$]+)$')

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


def getCREAMServiceInfo():

    #
    # TODO to be improved
    #
    propFile = None
    implVer = 'Unknown'
    ifaceVer = 'Unknown'
    
    try:
        propFile = open('/etc/glite-ce-cream/service.properties')
        for line in propFile:
            parsed = pRegex.match(line)
            if not parsed:
                continue
            if parsed.group(1) == 'implementation_version':
                implVer = parsed.group(2).strip()
            if parsed.group(1) == 'interface_version':
                ifaceVer = parsed.group(2).strip()
        
    except:
        pass
    
    if propFile:
        propFile.close()

    return (implVer, ifaceVer)
    

