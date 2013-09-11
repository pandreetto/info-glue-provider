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

MAX_RESPONSE_TIME = 2146660842
MAX_JOB_NUMBER = 444444
MAX_POLICY_NUMBER = 999999999

def process(siteDefs, out=sys.stdout):
    
    for queue in siteDefs.queues:
    
        out.write('dn: GlueCEUniqueID=%s:%d/cream-%s-%s,mds-vo-name=resource,o=grid\n' %
                  (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue))
        
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

        out.write('GlueCEUniqueID: %s:%d/cream-%s-%s\n' %
                  (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue))
        out.write('GlueCEHostingCluster: %s\n' % siteDefs.ceHost)
        out.write('GlueCEName: %s\n' % queue)
        out.write('GlueCEImplementationName: CREAM\n')
        out.write('GlueCEImplementationVersion: %s\n' % CommonUtils.getCREAMServiceInfo()[0])
        for capa in siteDefs.capabilities:
            out.write('GlueCECapability: %s\n' % capa)
        
        out.write('GlueCEInfoGatekeeperPort: %d\n' % siteDefs.cePort)
        out.write('GlueCEInfoHostName: %s\n' % siteDefs.ceHost)
        out.write('GlueCEInfoLRMSType: %s\n' % siteDefs.batchsys)
        #TODO investigate LRMSVersion
        out.write('GlueCEInfoLRMSVersion: not defined\n')
        out.write('GlueCEInfoTotalCPUs: 0\n')
        out.write('GlueCEInfoJobManager: %s\n' % siteDefs.jobmanager)
        out.write('GlueCEInfoContactString: https://%s:%d/ce-cream/services\n' % (siteDefs.ceHost, siteDefs.cePort))
        out.write('GlueCEInfoApplicationDir: %s\n' % siteDefs.softDir)
        out.write('GlueCEInfoDataDir: %s\n' % siteDefs.ceDataDir)
        if len(siteDefs.seList) > 0:
            out.write('GlueCEInfoDefaultSE: %s\n' % siteDefs.seList[0])
            
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

    
    #end for queue
    
