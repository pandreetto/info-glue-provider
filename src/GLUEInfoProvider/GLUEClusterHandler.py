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


def process(siteDefs, out=sys.stdout):

    if siteDefs.clusterHost and siteDefs.clusterHost <> siteDefs.ceHost:
        #The current node is not the cluster node
        #Cannot process cluster and subclusters
        return

    clusterDN = 'GlueClusterUniqueID=%s,mds-vo-name=resource,o=grid' % siteDefs.clusterId
    
    out.write('dn:%s\n' % clusterDN)
    
    out.write('''objectClass: GlueClusterTop
objectClass: GlueCluster
objectClass: GlueInformationService
objectClass: GlueKey
objectClass: GlueSchemaVersion
''')

    out.write('GlueClusterUniqueID: %s\n' % siteDefs.clusterId)
    out.write('GlueClusterName: %s\n' % siteDefs.clusterName)
    out.write('GlueForeignKey: GlueSiteUniqueID=%s\n' % siteDefs.clusterSite)
    
    for queue in siteDefs.queues[siteDefs.ceHost]:
        glueceID = '%s:%d/cream-%s-%s' % (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
        out.write('GlueForeignKey: GlueCEUniqueID=%s\n' % glueceID)
    for queue in siteDefs.queues[siteDefs.ceHost]:
        glueceID = '%s:%d/cream-%s-%s' % (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
        out.write('GlueClusterService: %s\n' % glueceID)
    
    out.write('GlueInformationServiceURL: ldap://%s:2170/mds-vo-name=resource,o=grid\n' % siteDefs.clusterHost)
    out.write('GlueSchemaVersionMajor: 1\n')
    out.write('GlueSchemaVersionMinor: 3\n')
    out.write('\n')
    
    
    
    for resData in siteDefs.resourceTable.values():
        
        out.write('dn: GlueSubClusterUniqueID=%s,%s\n' % (resData.id, clusterDN))
        
        out.write('''objectClass: GlueClusterTop
objectClass: GlueSubCluster
objectClass: GlueHostApplicationSoftware
objectClass: GlueHostArchitecture
objectClass: GlueHostBenchmark
objectClass: GlueHostMainMemory
objectClass: GlueHostNetworkAdapter
objectClass: GlueHostOperatingSystem
objectClass: GlueHostProcessor
objectClass: GlueInformationService
objectClass: GlueKey
objectClass: GlueSchemaVersion
''')

        out.write('GlueSubClusterUniqueID: %s\n' % resData.id)
        out.write('GlueChunkKey: GlueClusterUniqueID=%s\n' % siteDefs.clusterId)
        out.write('GlueHostArchitecturePlatformType: %s\n' % resData.osArch)
        out.write('GlueHostArchitectureSMPSize: %d\n' % resData.smpSize)
        out.write('GlueHostBenchmarkSF00: %f\n' % resData.benchSF00)
        out.write('GlueHostBenchmarkSI00: %f\n' % resData.benchSI00)
        out.write('GlueHostMainMemoryRAMSize: %d\n' % resData.mainMemSize)
        out.write('GlueHostMainMemoryVirtualSize: %d\n' % resData.mainVirtSize)
        out.write('GlueHostNetworkAdapterInboundIP: %s\n' % str(resData.inBound).upper())
        out.write('GlueHostNetworkAdapterOutboundIP: %s\n' % str(resData.outBound).upper())
        out.write('GlueHostOperatingSystemName: %s\n' % resData.osName)
        out.write('GlueHostOperatingSystemRelease: %s\n' % resData.osRelease)
        out.write('GlueHostOperatingSystemVersion: %s\n' % resData.osVersion)
        out.write('GlueHostProcessorClockSpeed: %d\n' % resData.procSpeed)
        out.write('GlueHostProcessorModel: %s\n' % resData.procModel)
        out.write('GlueHostProcessorVendor: %s\n' % resData.procVendor)
        out.write('GlueHostProcessorOtherDescription: %s\n' % resData.procDescr)
        
        for appItem in resData.runtimeEnv:
            out.write("GlueHostApplicationSoftwareRunTimeEnvironment: %s\n" % appItem)
        
        out.write('GlueSubClusterName: %s\n' % resData.name)
        out.write('GlueSubClusterPhysicalCPUs: %d\n' % resData.phyCPU)
        out.write('GlueSubClusterLogicalCPUs: %d\n' % resData.logCPU)
        out.write('GlueSubClusterTmpDir: %s\n' % resData.tmpDir)
        out.write('GlueSubClusterWNTmpDir: %s\n' % resData.WNDir)
        out.write('GlueInformationServiceURL: ldap://%s:2170/mds-vo-name=resource,o=grid\n' % siteDefs.clusterHost)
        out.write('GlueSchemaVersionMajor: 1\n')
        out.write('GlueSchemaVersionMinor: 3\n')
        out.write('\n')
        
        
    #end of resources












