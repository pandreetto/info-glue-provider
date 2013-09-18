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
# This module should replace glite-ce-glue2-tostorageservice-static
# and the related YAIM function config_cream_gip_glue2
#


def process(siteDefs, out=sys.stdout):

    now = CommonUtils.getNow()
    
    for seData in siteDefs.seAccess.values():
    
        # In GLUE2 access points are mandatory
        if seData.mount == None or seData.export == None:
            continue
    
        out.write("dn: GLUE2ToStorageServiceID=%s_%s,GLUE2ServiceID=%s,GLUE2GroupID=resource,o=glue\n"
                    % (siteDefs.compServiceID, seData.host, siteDefs.compServiceID))
        out.write("objectClass: GLUE2Entity\n")
        out.write("objectClass: GLUE2ToStorageService\n")
        out.write("GLUE2ToStorageServiceID: %s_%s\n" % (siteDefs.compServiceID, seData.host))
        out.write("GLUE2EntityCreationTime: %s\n" % now)
        out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
        out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
        out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
        out.write("Glue2EntityName: %s_%s\n" % (siteDefs.compServiceID, seData.host))
        out.write("GLUE2ToStorageServiceLocalPath: %s\n" % seData.mount)
        out.write("GLUE2ToStorageServiceRemotePath: %s\n" % seData.export)
        out.write("GLUE2ToStorageServiceComputingServiceForeignKey: %s\n" % siteDefs.compServiceID)
        out.write("GLUE2ToStorageServiceStorageServiceForeignKey: %s\n" % seData.host)
        out.write("\n")


