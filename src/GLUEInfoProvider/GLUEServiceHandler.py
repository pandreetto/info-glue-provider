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
import types

from GLUEInfoProvider import ServiceInfoUtils



#
# This module should replace glite-info-provider-service-cream-wrapper
# and the related YAIM function config_info_service_cream_ce
#

def getAllVO(siteDefs):
    result = set()
    for tmpl in siteDefs.acbrTable.values():
        for item in tmpl:
            result.add(item) 
    return result

def process(siteDefs, out=sys.stdout):

    srvType = 'org.glite.ce.CREAM'
    srvID = "%s_%s_%d" % (siteDefs.ceHost, srvType, siteDefs.cePort)
    srvDN = 'dn: GlueServiceUniqueID=%s,mds-vo-name=resource,o=grid' % srvID
    
    out.write('%s\n' % srvDN)
    
    out.write('''objectClass: GlueTop
objectClass: GlueService
objectClass: GlueKey
objectClass: GlueSchemaVersion
''')

    out.write('GlueServiceUniqueID: %s\n' % srvID)
    out.write('GlueServiceName: %s-CREAM\n' % siteDefs.siteName)
    out.write('GlueServiceType: %s\n' % srvType)
    out.write('GlueServiceVersion: %s\n' % ServiceInfoUtils.getCREAMServiceInfo()[0])
    out.write('GlueServiceEndpoint: https://%s:%d/ce-cream/services\n' % (siteDefs.ceHost, siteDefs.cePort))
    
    statusCode, statusInfo = ServiceInfoUtils.getTomcatStatus()
    out.write('GlueServiceStatus: %s\n' % statusCode)
    out.write('GlueServiceStatusInfo: %s\n' % statusInfo)
    
    out.write('GlueServiceWSDL: http://grid.pd.infn.it/cream/wsdl/org.glite.ce-cream_service.wsdl\n')
    out.write('GlueServiceSemantics: https://edms.cern.ch/document/595770\n')
    out.write('GlueServiceStartTime: %s\n' % ServiceInfoUtils.getTomcatStartTime())
    
    voList = getAllVO(siteDefs)
    for voItem in voList:
        out.write('GlueServiceOwner: %s\n' % voItem.getVOName())
    for voItem in voList:
        out.write('GlueServiceAccessControlBaseRule: %s\n' % repr(voItem))
        
    out.write('GlueForeignKey: GlueSiteUniqueID=%s\n' % siteDefs.siteName)
    out.write('GlueSchemaVersionMajor: 1\n')
    out.write('GlueSchemaVersionMinor: 3\n')
    out.write('\n')


    srvDataTable = { 'glite-info-service_version' : '1.7',
                     'glite-info-service_hostname' : siteDefs.ceHost,
                     'DN' : ServiceInfoUtils.getHostCertInfo()[0]}
    

    for srvDataItem in srvDataTable:
        
        out.write("dn: GlueServiceDataKey=%s,%s\n" % (srvDataItem, srvDN))
        out.write('''objectClass: GlueTop
objectClass: GlueServiceData
objectClass: GlueKey
objectClass: GlueSchemaVersion
''')

        out.write("GlueServiceDataKey: %s\n" % srvDataItem)
        if isinstance(srvDataTable[srvDataItem], types.ListType):
            for dataItem in srvDataTable[srvDataItem]:
                out.write("GlueServiceDataValue: %s\n" % dataItem)
        else:
            out.write("GlueServiceDataValue: %s\n" % srvDataTable[srvDataItem])
        out.write("GlueChunkKey: GlueServiceUniqueID=%s\n" % srvID)
        out.write("GlueSchemaVersionMajor: 1\n")
        out.write("GlueSchemaVersionMinor: 3\n")
        out.write("\n")






