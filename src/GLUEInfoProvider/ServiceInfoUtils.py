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

from GLUEInfoProvider import CommonUtils

def init(cfg):
    global config
    config = cfg

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
            parsed = CommonUtils.pRegex.match(line)
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
    
def getCREAMServingState():

    try:
    
        sqlTpl = 'mysql -B --skip-column-names -h %s -u %s --password="%s" -e "use %s; %s;"' \
                 % (config['DBHost'], config['MinPrivDBUser'], 
                    config['MinPrivDBPassword'], config['CreamDBName'], '%s')
                    
        
        query1 = 'select submissionEnabled from db_info;'
        
        cmdargs = shlex.split(sqlTpl % query1)
        process = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pOut, pErr = process.communicate()
        if process.returncode > 0:
            raise Exception("Error detecting serving status: " + pErr)
        servingCode = int(pOut.strip())
        
        query2 = 'select SUBTIME((select startUpTime from db_info),TIMEDIFF(CURRENT_TIME(),UTC_TIME())) from db_info;'
        
        cmdargs = shlex.split(sqlTpl % query2)
        process = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pOut, pErr = process.communicate()
        if process.returncode > 0:
            raise Exception("Error detecting start time: " + pErr)
        starttime = pOut.strip().replace(' ', 'T') + 'Z'
        
        if code == 0:
            return ('production', starttime)
        elif code == 1 or code == 2:
            return ('draining', starttime)
        return ('closed', starttime)

    except:
        pass
        
    return ('Unknown', 'Unknown')

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

def getHostCertInfo():

    try:
        cmd = shlex.split('openssl x509 -in /etc/grid-security/hostcert.pem -noout -nameopt RFC2253 -subject -issuer')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdoutdata, stderrdata = process.communicate()
        if process.returncode == 0:
            result = list()
            for line in stdoutdata.split('\n'):
                parsed = CommonUtils.pRegex.match(line)
                if parsed:
                    result.append(parsed.group(2).strip(' \n\t"'))
            return tuple(result)
        
    except:
        pass
        
    return ('Unknown', 'Unknown')
    
def getTrustAnchors():
    
    #
    # TODO cache list
    #
    result = list()
    
    try:
        for CAFile in glob.glob('/etc/grid-security/certificates/*.pem'):
            cmdargs = shlex.split('openssl x509 -in %s -noout -subject -nameopt RFC2253' % CAFile)
            process = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pOut, pErr = process.communicate()
            if process.returncode > 0:
                raise Exception("Error parsing host certificate: " + pErr)

            parsed = CommonUtils.pRegex.match(pOut)
            if parsed:
                trustedCAs.append(parsed.group(2).strip(' \n\t"'))
    except:
        pass
    
    return result





