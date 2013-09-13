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

    for queue in siteDefs.queues[siteDefs.ceHost]:

        glueceID = '%s:%d/cream-%s-%s' % (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
        glueceseGrpDN = 'GlueCESEBindGroupCEUniqueID=%s,mds-vo-name=resource,o=grid' % glueceID

        out.write("dn:%s\n" % glueceseGrpDN)
        
        out.write('''objectClass: GlueGeneralTop
objectClass: GlueCESEBindGroup
objectClass: GlueSchemaVersion
''')

        out.write("GlueCESEBindGroupCEUniqueID: %s\n" % glueceID)
        
        for seItem in siteDefs.seList:
            out.write("GlueCESEBindGroupSEUniqueID: %s\n" % seItem)
        out.write("GlueSchemaVersionMajor: 1\n")
        out.write("GlueSchemaVersionMinor: 3\n")
        out.write("\n")


    for seItem in siteDefs.seList:
        
        if seItem in siteDefs.seAccess:
            accessPoint = siteDefs.seAccess[seItem]
        else:
            accessPoint = 'n.a.'
            
        for queue in siteDefs.queues[siteDefs.ceHost]:
        
            glueceID = '%s:%d/cream-%s-%s' % (siteDefs.ceHost, siteDefs.cePort, siteDefs.jobmanager, queue)
            out.write('dn: GlueCESEBindSEUniqueID=%s,GlueCESEBindGroupCEUniqueID=%s,mds-vo-name=resource,o=grid\n' 
                    % (seItem, glueceID))
        
            out.write('''objectClass: GlueGeneralTop
objectClass: GlueCESEBind
objectClass: GlueSchemaVersion
''')

            out.write('GlueCESEBindSEUniqueID: %s\n' % seItem)
            out.write('GlueCESEBindCEAccesspoint: %s\n' % accessPoint)
            out.write('GlueCESEBindCEUniqueID: %s\n' % glueceID)
            out.write('GlueCESEBindMountInfo: %s\n' % accessPoint)
            out.write('GlueCESEBindWeight: 0\n')
            out.write('GlueSchemaVersionMajor: 1\n')
            out.write('GlueSchemaVersionMinor: 3\n')
            out.write('\n')


