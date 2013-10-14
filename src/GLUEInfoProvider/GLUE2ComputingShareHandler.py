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
# This module should replace glite-ce-glue2-share-static
# and the related YAIM function config_cream_gip_glue2
#
MAX_RESPONSE_TIME = 2146660842
MAX_JOB_NUMBER = 444444
MAX_POLICY_NUMBER = 999999999

def process(siteDefs, out=sys.stdout):

    if siteDefs.creamStandAloneMode(siteDefs.ceHost):
        return

    now = CommonUtils.getNow()
    
    for queue in siteDefs.ruleTable.getQueueList():
    
        ceList, voList = siteDefs.ruleTable.getHostAndVOList(queue)
        
        #
        # For the moment we consider just one host per share
        #
        ceId = '%s:%d/cream-%s-%s' % (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
    
        for voItem in voList:
            
            shareId = "%s_%s_%s" % (queue, voItem.getNormName(), siteDefs.compServiceID)
            shareDN = 'GLUE2ShareID=%s,GLUE2ServiceID=%s,GLUE2GroupID=resource,o=glue' \
                      % (shareId, siteDefs.compServiceID)
            
            out.write("dn: %s\n" % shareDN)
            
            out.write("objectClass: GLUE2Entity\n")
            out.write("objectClass: GLUE2Share\n")
            out.write("objectClass: GLUE2ComputingShare\n")
            
            out.write("GLUE2EntityCreationTime: %s\n" % now)
            out.write("GLUE2EntityOtherInfo: CREAMCEId=%s\n" % ceId)
            out.write("GLUE2EntityOtherInfo: ServiceType=org.glite.ce.CREAM\n")
            out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
            out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
            out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
            
            out.write("GLUE2ShareID: %s\n" % shareId)
            out.write("GLUE2ShareDescription: Share of %s for %s\n" % (queue, voItem.getVOName()))

            out.write("GLUE2ComputingShareMappingQueue: %s\n" % queue)
            # Default value for Serving state is production
            # Real value supposed to be provided by the dynamic plugin
            out.write("GLUE2ComputingShareServingState: unknown\n")
            out.write("GLUE2ComputingShareDefaultCPUTime: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareMaxCPUTime: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareDefaultWallTime: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareMaxWallTime: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareMaxRunningJobs: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareMaxTotalJobs: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareMaxWaitingJobs: %d\n" % MAX_POLICY_NUMBER)
            out.write("GLUE2ComputingShareMaxSlotsPerJob: %d\n" % MAX_JOB_NUMBER)
            out.write("GLUE2ComputingShareRunningJobs: 0\n")
            out.write("GLUE2ComputingShareTotalJobs: 0\n")
            out.write("GLUE2ComputingShareFreeSlots: 0\n")
            out.write("GLUE2ComputingShareUsedSlots: 0\n")
            out.write("GLUE2ComputingShareWaitingJobs: %d\n"  % MAX_JOB_NUMBER)
            out.write("GLUE2ComputingShareEstimatedAverageWaitingTime: %d\n" % MAX_RESPONSE_TIME)
            out.write("GLUE2ComputingShareEstimatedWorstWaitingTime: %d\n" % MAX_RESPONSE_TIME)
            out.write("GLUE2ComputingShareMaxMainMemory: %d\n"  % MAX_JOB_NUMBER)
            out.write("GLUE2ComputingShareMaxVirtualMemory: %d\n"  % MAX_JOB_NUMBER)
            out.write("GLUE2ComputingShareGuaranteedMainMemory: 0\n")
            out.write("GLUE2ComputingShareGuaranteedVirtualMemory: 0\n")

            for resItem in siteDefs.resourceTable.values():
                out.write("GLUE2ShareResourceForeignKey: %s\n" % resItem.id)
                out.write("GLUE2ComputingShareExecutionEnvironmentForeignKey: %s\n" % resItem.id)
            
            for ceHostItem in ceList:
                out.write("GLUE2ShareEndpointForeignKey: %s_org.glite.ce.CREAM\n" % ceHostItem)
                out.write("GLUE2ComputingShareComputingEndpointForeignKey: %s_org.glite.ce.CREAM\n" % ceHostItem)
            
            out.write("GLUE2ShareServiceForeignKey: %s\n" % siteDefs.compServiceID)
            out.write("GLUE2ComputingShareComputingServiceForeignKey: %s\n" % siteDefs.compServiceID)
            out.write("\n")
            
            out.write("dn: GLUE2PolicyID=%s_policy,%s\n" % (shareId, shareDN))
            out.write("objectClass: GLUE2Entity\n")
            out.write("objectClass: GLUE2Policy\n")
            out.write("objectClass: GLUE2MappingPolicy\n")
            out.write("GLUE2EntityCreationTime: %s\n" % now)
            out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
            out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
            out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)

            out.write("GLUE2PolicyID: %s_policy\n" % shareId)
            out.write("GLUE2PolicyScheme: org.glite.standard\n")
            out.write("GLUE2PolicyRule: %s\n" % repr(voItem))
            out.write("GLUE2PolicyUserDomainForeignKey: %s\n" % voItem.getVOName())

            out.write("GLUE2MappingPolicyShareForeignKey: %s\n" % shareId)
            out.write("\n")


    
