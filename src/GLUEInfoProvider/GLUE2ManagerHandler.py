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
# This module should replace glite-ce-glue2-manager-static
# and the related YAIM function config_cream_gip_glue2
#

def process(siteDefs, out=sys.stdout):

    if siteDefs.creamStandAloneMode(siteDefs.ceHost):
        return

    now = CommonUtils.getNow()
    
    out.write("dn: GLUE2ManagerId=%s_Manager,GLUE2ServiceID=%s,GLUE2GroupID=resource,o=glue\n"
                    % (siteDefs.compServiceID, siteDefs.compServiceID))
    out.write("objectClass: GLUE2Entity\n")
    out.write("objectClass: GLUE2Manager\n")
    out.write("objectClass: GLUE2ComputingManager\n")

    out.write("GLUE2EntityCreationTime: %s\n" % now)
    out.write("GLUE2EntityName: Computing Manager on %s\n" % siteDefs.ceHost)
    out.write("GLUE2EntityOtherInfo: InfoProviderName=%s\n" % CommonUtils.providerName)
    out.write("GLUE2EntityOtherInfo: InfoProviderVersion=%s\n" % CommonUtils.providerVersion)
    out.write("GLUE2EntityOtherInfo: InfoProviderHost=%s\n" % siteDefs.ceHost)
    for capaItem in siteDefs.capabilities:
        out.write("GLUE2EntityOtherInfo: %s\n" % capaItem)
        
    out.write("GLUE2ManagerID: %s_Manager\n" % siteDefs.compServiceID)
    out.write("GLUE2ManagerProductName: %s\n" % siteDefs.batchsys)
    out.write("GLUE2ManagerProductVersion: %s\n" % siteDefs.batchsysVer)
    out.write("GLUE2ManagerServiceForeignKey: %s\n" % siteDefs.compServiceID)

    if siteDefs.wAreaShared <> None:
        out.write("GLUE2ComputingManagerWorkingAreaShared: %s\n" % repr(siteDefs.wAreaShared).upper())
    if siteDefs.wAreaGuaranteed <> None:
        out.write("GLUE2ComputingManagerWorkingAreaGuaranteed: %s\n" % repr(siteDefs.wAreaGuaranteed).upper())
    if siteDefs.wAreaTotal <> -1:
        out.write("GLUE2ComputingManagerWorkingAreaTotal: %d\n" % siteDefs.wAreaTotal)
    if siteDefs.wAreaFree <> -1:
        out.write("GLUE2ComputingManagerWorkingAreaFree: %d\n" % siteDefs.wAreaFree)
    if siteDefs.wAreaLifeTime <> -1:
        out.write("GLUE2ComputingManagerWorkingAreaLifeTime: %d\n" % siteDefs.wAreaLifeTime)
    if siteDefs.wAreaMultiSlotTotal <> -1:
        out.write("GLUE2ComputingManagerWorkingAreaMultiSlotTotal: %d\n" % siteDefs.wAreaMultiSlotTotal)
    if siteDefs.wAreaMultiSlotFree <> -1:
        out.write("GLUE2ComputingManagerWorkingAreaMultiSlotFree: %d\n" % siteDefs.wAreaMultiSlotFree)
    if siteDefs.wAreaMultiSlotLifeTime <> -1:
        out.write("GLUE2ComputingManagerWorkingAreaMultiSlotLifeTime: %d\n" % siteDefs.wAreaMultiSlotLifeTime)
    
    out.write("GLUE2ComputingManagerComputingServiceForeignKey: %s\n" % siteDefs.compServiceID)
    out.write("\n")

