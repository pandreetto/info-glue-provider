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
from GLUEInfoProvider import ServiceInfoUtils

#
# This module should replace glite-ce-glue2-endpoint-static
# glite-ce-glue2-endpoint-dynamic
# and the related YAIM function config_cream_gip_glue2
#

def getAllVO(siteDefs):
    result = set()
    for tmpl in siteDefs.acbrTable.values():
        for item in tmpl:
            result.add(item) 
    return result

def process(siteDefs, out=sys.stdout):

    now = CommonUtils.getNow()

    endPointID = siteDefs.ceHost + '_org.glite.ce.CREAM'
    endPointDN = 'GLUE2EndpointID=%s,GLUE2ServiceID=%s,GLUE2GroupID=resource,o=glue' \
                  % (endPointID, siteDefs.compServiceID)
    implVer, ifaceVer = ServiceInfoUtils.getCREAMServiceInfo()
    hostDN, hostIssuer = ServiceInfoUtils.getHostCertInfo()
    #
    # TODO Validity is hard-coded for now (1hour in seconds)
    #
    validity = 3600
    statusCode, statusInfo = ServiceInfoUtils.getTomcatStatus()
    srvState, srvStarttime = ServiceInfoUtils.getCREAMServingState()
    
    out.write("dn: %s\n" % endPointDN)
    
    out.write("objectClass: GLUE2Entity\n")
    out.write("objectClass: GLUE2Endpoint\n")
    out.write("objectClass: GLUE2ComputingEndpoint\n")
    
    out.write("GLUE2EntityName: %s\n" % endPointID)
    out.write("GLUE2EntityCreationTime: %s\n" % now)
    out.write("GLUE2EntityValidity: %d\n" % validity)
    out.write("GLUE2EntityOtherInfo: HostDN=%s\n" % hostDN)
    out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
    out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
    out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
    out.write("GLUE2EntityOtherInfo: ArgusEnabled=%s\n" % repr(siteDefs.argusEnabled).upper())
    
    out.write("Glue2EndpointStartTime: %s\n" % now)
    out.write("GLUE2EndpointID: %s\n" % endPointID)
    out.write("GLUE2EndpointURL: https://%s:%d/ce-cream/services\n" % (siteDefs.ceHost, siteDefs.cePort))
    out.write("GLUE2EndpointCapability: executionmanagement.jobexecution\n")
    out.write("GLUE2EndpointTechnology: webservice\n")
    out.write("GLUE2EndpointInterfaceName: org.glite.ce.CREAM\n")
    out.write("GLUE2EndpointInterfaceVersion: %s\n" % ifaceVer)
    out.write("GLUE2EndpointWSDL: https://%s:%d/ce-cream/services/CREAM2?wsdl\n" % (siteDefs.ceHost, siteDefs.cePort))
    out.write("GLUE2EndpointSupportedProfile: http://www.ws-i.org/Profiles/BasicProfile-1.0.html\n")
    out.write("GLUE2EndpointSemantics:http://wiki.italiangrid.org/twiki/bin/view/CREAM/UserGuide\n")
    out.write("GLUE2EndpointImplementor: gLite\n")
    out.write("GLUE2EndpointImplementationName: CREAM\n")
    out.write("GLUE2EndpointImplementationVersion: %s\n" % implVer)
    out.write("GLUE2EndpointQualityLevel: production\n")
    
    out.write("GLUE2EndpointHealthState: %s\n" % statusCode)
    out.write("GLUE2EndpointHealthStateInfo: %s\n" % statusInfo)
    out.write("GLUE2EndpointServingState: %s\n" % srvState)
    out.write("GLUE2EndpointStartTime: %s\n" % srvStarttime)
    out.write("GLUE2EndpointIssuerCA: %s\n" % hostIssuer)
    for tCA in ServiceInfoUtils.getTrustAnchors():
        out.write("GLUE2EndpointTrustedCA: %s\n" % tCA)
    
    out.write("GLUE2EndpointDownTimeInfo: See the GOC DB for downtimes: https://goc.egi.eu/\n")
    out.write("GLUE2EndpointServiceForeignKey: %s\n" % siteDefs.compServiceID)
    
    out.write("GLUE2ComputingEndpointStaging: staginginout\n")
    out.write("GLUE2ComputingEndpointJobDescription: glite:jdl\n")
    out.write("GLUE2ComputingEndpointComputingServiceForeignKey: %s\n" % siteDefs.compServiceID)
    out.write("\n")
    
    
    out.write("dn: GLUE2PolicyID=%s_Policy,%s\n" % (endPointID, endPointDN))

    out.write("objectClass: GLUE2Entity\n")
    out.write("objectClass: GLUE2Policy\n")
    out.write("objectClass: GLUE2AccessPolicy\n")
    
    out.write("GLUE2EntityCreationTime: %s\n" % now)
    out.write("GLUE2EntityName: Access control rules for Endpoint %s\n" % endPointID)
    out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
    out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
    out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)

    out.write("GLUE2PolicyID: %s_Policy\n" % endPointID)
    # The policy scheme needs a name: arbitrarily define this as org.glite.standard
    out.write("GLUE2PolicyScheme: org.glite.standard\n")
    
    voList = getAllVO(siteDefs)
    for voItem in voList:
        out.write('GLUE2PolicyUserDomainForeignKey: %s\n' % voItem.getVOName())
    for voItem in voList:
        out.write('GLUE2PolicyRule: %s\n' % repr(voItem))
        
    out.write("GLUE2AccessPolicyEndpointForeignKey: %s\n" % endPointID)
    out.write("\n")

