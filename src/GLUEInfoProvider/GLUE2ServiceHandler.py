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
# This module should replace glite-ce-glue2-computingservice-static
# and the related YAIM function config_cream_gip_glue2
#

def process(siteDefs, out=sys.stdout):

    now = CommonUtils.getNow()
    srvType = 'org.glite.ce.CREAM'
    
    endpointCount = 2  # CREAM + RTEPublisher (CEMon ?)
    shareCount = 0
    for tmpl in siteDefs.acbrTable.values():
        shareCount += len(tmpl)
    resourceCount = len(siteDefs.resourceTable)
    
    out.write("dn: GLUE2ServiceID=%s,GLUE2GroupID=resource,o=glue\n" % siteDefs.compServiceID)
    out.write("objectClass: GLUE2Entity\n")
    out.write("objectClass: GLUE2Service\n")
    out.write("objectClass: GLUE2ComputingService\n")
        
    out.write("GLUE2EntityCreationTime: %s\n" % now)
    out.write("GLUE2EntityName: Computing Service %s\n" % siteDefs.compServiceID)
    out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
    out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
    out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
        
    out.write("GLUE2ServiceID: %s\n" % siteDefs.compServiceID)
    out.write("GLUE2ServiceType: %s\n" % srvType)
    out.write("GLUE2ServiceCapability: executionmanagement.jobexecution\n")
    out.write("GLUE2ServiceQualityLevel: production\n")
    out.write("GLUE2ServiceComplexity: endpointType=%d, share=%d, resource=%d\n"
                   % (endpointCount, shareCount, resourceCount))
    out.write("GLUE2ServiceAdminDomainForeignKey: %s\n" % siteDefs.siteName)
    out.write("\n")




