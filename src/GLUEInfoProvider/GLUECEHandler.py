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

from GLUEInfoProvider import ServiceInfoUtils

MAX_RESPONSE_TIME = 2146660842
MAX_JOB_NUMBER = 444444
MAX_POLICY_NUMBER = 999999999

def process(siteDefs, out=sys.stdout):

    for queue in siteDefs.ruleTable.getQueueList(siteDefs.ceHost):
    
        if len(siteDefs.seAccess) > 0:
            bestSE = min(siteDefs.seAccess.values())
        else:
            bestSE = None
    
        glueceDN = 'GlueCEUniqueID=%s:%d/cream-%s-%s,mds-vo-name=resource,o=grid' % \
                   (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
        
        glueceID = '%s:%d/cream-%s-%s' % (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
    
        out.write('dn:%s\n' % glueceDN)
        
        out.write('''objectClass: GlueCETop
objectClass: GlueCE
objectClass: GlueCEAccessControlBase
objectClass: GlueCEInfo
objectClass: GlueCEPolicy
objectClass: GlueCEState
objectClass: GlueInformationService
objectClass: GlueKey
objectClass: GlueSchemaVersion
''')

        out.write('GlueCEUniqueID: %s\n' % glueceID)
                  
        out.write('GlueCEHostingCluster: %s\n' % siteDefs.ceHost)
        out.write('GlueCEName: %s\n' % queue)
        out.write('GlueCEImplementationName: CREAM\n')
        out.write('GlueCEImplementationVersion: %s\n' % ServiceInfoUtils.getCREAMServiceInfo()[0])
        for capa in siteDefs.capabilities:
            out.write('GlueCECapability: %s\n' % capa)
            
        for acbr in siteDefs.ruleTable.getVOList(siteDefs.ceHost, queue):
            out.write('GlueCEAccessControlBaseRule: %s\n' % repr(acbr))
        
        out.write('GlueCEInfoGatekeeperPort: %d\n' % siteDefs.cePort)
        out.write('GlueCEInfoHostName: %s\n' % siteDefs.ceHost)
        out.write('GlueCEInfoLRMSType: %s\n' % siteDefs.batchsys)
        #TODO investigate LRMSVersion
        out.write('GlueCEInfoLRMSVersion: not defined\n')
        out.write('GlueCEInfoTotalCPUs: 0\n')
        out.write('GlueCEInfoJobManager: %s\n' % siteDefs.jobmanager)
        out.write('GlueCEInfoContactString: https://%s:%d/ce-cream/services\n' % (siteDefs.ceHost, siteDefs.cePort))
        if siteDefs.softDir and len(siteDefs.softDir) > 0:
            out.write('GlueCEInfoApplicationDir: %s\n' % siteDefs.softDir)
        if siteDefs.ceDataDir and len(siteDefs.ceDataDir) > 0:
            out.write('GlueCEInfoDataDir: %s\n' % siteDefs.ceDataDir)
        if bestSE <> None:
            out.write('GlueCEInfoDefaultSE: %s\n' % bestSE.host)
            
        out.write('GlueCEStateEstimatedResponseTime: %d\n' % MAX_RESPONSE_TIME)
        out.write('GlueCEStateWorstResponseTime: %d\n' % MAX_RESPONSE_TIME)
        out.write('GlueCEStateFreeCPUs: 0\n')
        out.write('GlueCEStateRunningJobs: 0\n')
        out.write('GlueCEStateStatus: Unknown\n')
        out.write('GlueCEStateTotalJobs: 0\n')
        out.write('GlueCEStateWaitingJobs: %d\n' % MAX_JOB_NUMBER)
        out.write('GlueCEStateFreeJobSlots: 0\n')
        
        out.write('GlueCEPolicyMaxRunningJobs: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxTotalJobs: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxCPUTime: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxWallClockTime: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxObtainableCPUTime: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxObtainableWallClockTime: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxWaitingJobs: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyMaxSlotsPerJob: %d\n' % MAX_POLICY_NUMBER)
        out.write('GlueCEPolicyPreemption: 0\n')
        out.write('GlueCEPolicyPriority: 1\n')
        out.write('GlueCEPolicyAssignedJobSlots: 0\n')
        
        out.write('GlueForeignKey: GlueClusterUniqueID=%s\n' % siteDefs.ceHost)
        out.write('GlueInformationServiceURL: ldap://%s:2170/mds-vo-name=resource,o=grid\n' % siteDefs.ceHost)
        out.write('GlueSchemaVersionMajor: 1\n')
        out.write('GlueSchemaVersionMinor: 3\n')
        out.write('\n')

    
        for vogrp in siteDefs.ruleTable.getVOList(siteDefs.ceHost, queue):
            
            voviewID = vogrp.getNormName()
            voNameLC = vogrp.getVOName().lower()
            
            out.write("dn:GlueVOViewLocalID=%s,%s\n" % (voviewID, glueceDN))
            
            out.write('''objectClass: GlueCETop
objectClass: GlueVOView
objectClass: GlueCEInfo
objectClass: GlueCEState
objectClass: GlueCEAccessControlBase
objectClass: GlueCEPolicy
objectClass: GlueKey
objectClass: GlueSchemaVersion
''')
            out.write('GlueVOViewLocalID: %s\n' % voviewID)
            out.write('GlueCEStateRunningJobs: 0\n')
            out.write('GlueCEStateWaitingJobs: %d\n' % MAX_JOB_NUMBER)
            out.write('GlueCEStateTotalJobs: 0\n')
            out.write('GlueCEStateFreeJobSlots: 0\n')
            out.write('GlueCEStateEstimatedResponseTime: %d\n' % MAX_RESPONSE_TIME)
            out.write('GlueCEStateWorstResponseTime: %d\n' % MAX_RESPONSE_TIME)
            
            tmpSE = None
            tmpSDir = None
            
            if voNameLC in siteDefs.voParams:
                tmpSE = siteDefs.voParams[voNameLC].defaultSE
                tmpSDir = siteDefs.voParams[voNameLC].softDir
                
            if not tmpSE and bestSE <> None:
                tmpSE = bestSE.host
            
            if not tmpSDir:
                tmpSDir = siteDefs.softDir
                
            if tmpSE:
                out.write('GlueCEInfoDefaultSE: %s\n' % tmpSE)
            if tmpSDir:
                out.write('GlueCEInfoApplicationDir: %s\n' % tmpSDir)

            if siteDefs.ceDataDir and len(siteDefs.ceDataDir) > 0:
                out.write('GlueCEInfoDataDir: %s\n' % siteDefs.ceDataDir)
                
            out.write('GlueChunkKey: GlueCEUniqueID=%s\n' % glueceID)
            out.write('GlueCEAccessControlBaseRule: %s\n' % repr(vogrp))
            out.write('GlueSchemaVersionMajor: 1\n')
            out.write('GlueSchemaVersionMinor: 3\n')
            out.write('\n')

    #end for queue
    
