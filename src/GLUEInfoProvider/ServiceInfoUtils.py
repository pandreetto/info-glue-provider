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
import os, os.path
import time
import glob
import shlex
import subprocess

pRegex = re.compile('^\s*([^=\s]+)\s*=([^$]+)$')

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

def getTomcatStatus():

    try:
        tomcatName = os.path.basename(glob.glob('/var/lib/tomcat*')[0])
        cmd = shlex.split('/sbin/service %s status' % tomcatName)
        process = subprocess.Popen(cmd)
        
        process.communicate()
        if process.returncode == 0:
            return ('OK', 'Tomcat is running')
        elif process.returncode == 3 or process.returncode == 1:
            return ('Critical', 'Tomcat is not running')
        else:
            return ('Unknown', 'Undefined status for tomcat')
    except:
        pass
        
    return ('Unknown', 'Undefined status for tomcat')

def getTomcatStartTime():

    try:
        if 'CREAM_PID_FILE' in os.environ:
            tmpf = os.environ['CREAM_PID_FILE']
        else:
            tmpl = glob.glob('/var/run/tomcat*.pid')
            if len(tmpl) > 0:
                tmpf = tmpl[0]
            
        pidTime = os.stat(tmpf).st_mtime
        tmps = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(pidTime))
        return "%s%03d:00" % (tmps, time.timezone / 3600)
        
    except:
        return 'Unknown'

def getHostDN():

    try:
        cmd = shlex.split('openssl x509 -in /etc/grid-security/hostcert.pem -noout -subject')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdoutdata, stderrdata = process.communicate()
        if process.returncode == 0:        
            return stdoutdata
        
    except:
        pass
        
    return 'Unknown'





