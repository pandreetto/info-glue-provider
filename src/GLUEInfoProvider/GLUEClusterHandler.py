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
    
    out.write('GlueInformationServiceURL: ldap://%s:2170/mds-vo-name=resource,o=grid\n' % siteDefs.ceHost)
    out.write('GlueSchemaVersionMajor: 1\n')
    out.write('GlueSchemaVersionMinor: 3\n')
    out.write('\n')




