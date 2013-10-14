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

from GLUEInfoProvider import CommonUtils

#
# This module should replace glite-ce-glue2-executionenvironment-static
# glite-ce-glue2-applicationenvironment-dynamic
# glite-ce-glue2-benchmark-static
# and the related YAIM function config_cream_gip_glue2
#


def parseProcDescr(procDescr):

    cores = '0.0'
    benchName = None
    benchValue = '0.0'
    
    for token in procDescr.strip('\'"').split(','):
        parsed = CommonUtils.pRegex.match(token)
        if not parsed:
            continue
        
        key = parsed.group(1).lower()
        if key == 'cores':
            cores = parsed.group(2).strip()
        elif key == 'benchmark':
            tmps = parsed.group(2).strip()
            idx = tmps.find('-')
            if idx > 0:
                benchName = tmps[idx+1:].lower()
                benchValue = tmps[0:idx]

    return cores, benchName, benchValue


def process(siteDefs, out=sys.stdout):

    if siteDefs.creamStandAloneMode(siteDefs.ceHost):
        return

    now = CommonUtils.getNow()
    
    osType = 'linux'
    # Hardwire the data validity period to 1 hour for now
    validity = 3600
    
    for resItem in siteDefs.resourceTable.values():
    
        #
        # TODO verify following values
        #

        cores, benchName, benchValue = parseProcDescr(resItem.procDescr)
        
        if resItem.smpSize > 0:
            totalInstances = resItem.logCPU/resItem.smpSize
        else:
            totalInstances = resItem.logCPU
        
        if resItem.logCPU == resItem.phyCPU:
            cpuType = 'single'
        else:
            cpuType = 'multi'
            
        if resItem.phyCPU <> 0  and resItem.smpSize == (resItem.logCPU/resItem.phyCPU):
            coreType = 'single'
        else:
            coreType = 'multi'
        
        resDN = 'GLUE2ResourceID=%s,GLUE2ServiceID=%s,GLUE2GroupID=resource,o=glue' \
                % (resItem.id, siteDefs.compServiceID)
        
        out.write("dn: %s\n" % resDN)
        out.write("objectClass: GLUE2Entity\n")
        out.write("objectClass: GLUE2Resource\n")
        out.write("objectClass: GLUE2ExecutionEnvironment\n")
        
        out.write("GLUE2EntityCreationTime: %s\n" % now)
        out.write("GLUE2EntityName: %s\n" % resItem.id)
        out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
        out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
        out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
        out.write("GLUE2EntityOtherInfo: SmpSize=%d\n" % resItem.smpSize)
        out.write("GLUE2EntityOtherInfo: Cores=%s\n" % cores)

        out.write("GLUE2ResourceID: %s\n" % resItem.id)
        out.write("GLUE2ResourceManagerForeignKey: %s_Manager\n" % siteDefs.compServiceID)

        out.write("GLUE2ExecutionEnvironmentPlatform: %s\n" % resItem.osArch)
        out.write("GLUE2ExecutionEnvironmentTotalInstances: %d\n" % totalInstances)
        out.write("GLUE2ExecutionEnvironmentPhysicalCPUs: %d\n" % resItem.phyCPU)
        out.write("GLUE2ExecutionEnvironmentLogicalCPUs: %d\n" % resItem.logCPU)
        out.write("GLUE2ExecutionEnvironmentCPUMultiplicity: %scpu-%score\n" 
                      % (cpuType, coreType))
        out.write("GLUE2ExecutionEnvironmentCPUVendor: %s\n" % resItem.procVendor)
        out.write("GLUE2ExecutionEnvironmentCPUModel: %s\n" % resItem.procModel)
        out.write("GLUE2ExecutionEnvironmentCPUClockSpeed: %s\n" % resItem.procSpeed)
        out.write("GLUE2ExecutionEnvironmentMainMemorySize: %d\n" % resItem.mainMemSize)
        out.write("GLUE2ExecutionEnvironmentVirtualMemorySize: %d\n" % resItem.mainVirtSize)
        out.write("GLUE2ExecutionEnvironmentOSFamily: %s\n" % osType)
        out.write("GLUE2ExecutionEnvironmentOSName: %s\n" % resItem.osName)
        out.write("GLUE2ExecutionEnvironmentOSVersion: %s\n" % resItem.osRelease)
        out.write("GLUE2ExecutionEnvironmentConnectivityIn: %s\n" % repr(resItem.inBound).upper())
        out.write("GLUE2ExecutionEnvironmentConnectivityOut: %s\n" % repr(resItem.outBound).upper())
        out.write("GLUE2ExecutionEnvironmentComputingManagerForeignKey: %s_Manager\n" % siteDefs.compServiceID)
        out.write("GLUE2ExecutionEnvironmentCPUTimeScalingFactor: 1\n")
        out.write("\n")    


        benchList = list()
        benchList.append(('specfp2000', resItem.benchSF00))
        benchList.append(('specint2000', resItem.benchSI00))
        if benchName:
            benchList.append((benchName, benchValue))
        
        for benchName, benchValue in benchList:
            out.write("dn: GLUE2BenchmarkID=%s_%s,%s\n" % (resItem.id, benchName, resDN))
            out.write("objectClass: GLUE2Entity\n")
            out.write("objectClass: GLUE2Benchmark\n")
            out.write("GLUE2EntityCreationTime: %s\n" % now)
            out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
            out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
            out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
            out.write("Glue2EntityName: Benchmark %s\n" % benchName)
            out.write("GLUE2BenchmarkID: %s_%s\n" % (resItem.id, benchName))
            out.write("GLUE2BenchmarkType: %s\n" % benchName)
            out.write("GLUE2BenchmarkValue: %s\n" % benchValue)
            out.write("GLUE2BenchmarkExecutionEnvironmentForeignKey: %s\n" %resItem.id)
            out.write("GLUE2BenchmarkComputingManagerForeignKey: %s_Manager\n" % siteDefs.compServiceID)
            out.write("\n")
        
        for appItem in resItem.runtimeEnv:
            out.write("dn: GLUE2ApplicationEnvironmentId=%s_%s,%s\n" % (appItem, resItem.id, resDN))
            out.write("objectClass: GLUE2Entity\n")
            out.write("objectClass: GLUE2ApplicationEnvironment\n")
            out.write("GLUE2EntityCreationTime: %s\n" % now)
            out.write("GLUE2EntityValidity: %d\n" % validity)
            out.write("GLUE2ApplicationEnvironmentID: %s_%s\n" % (appItem, resItem.id))
            out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
            out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
            out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
            out.write("GLUE2ApplicationEnvironmentAppName: %s\n" % appItem)
            out.write("GLUE2ApplicationEnvironmentComputingManagerForeignKey: %s_Manager\n" % siteDefs.compServiceID)
            out.write("\n")


