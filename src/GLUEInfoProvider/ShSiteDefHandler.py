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
from threading import Thread

from GLUEInfoProvider import CommonUtils


class SiteInfoHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.errList = list()
        self.pRegex = re.compile('^\s*([^=\s]+)\s*=([^$]+)$')

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
                    print value
                    
            finally:
                line = self.stream.readline()


def parse(fileList):
    
    tempExec = '/tmp/print-siteinfo-defs'
    outFile = None
    inFile = None
    
    try:
        outFile = open(tempExec,'w')
        for fileItem in fileList:
            inFile = open(fileItem)
            for line in inFile:
                outFile.write(line)
            inFile.close()
        
        outFile.write('\nset\n')
        
    finally:
        if outFile:
            outFile.close()
        if inFile:
            inFile.close()
    
    os.chmod(tempExec, stat.S_IRUSR | stat.S_IXUSR)
        
    container = SiteInfoHandler()
    CommonUtils.parseStream(tempExec, container)
    return container








