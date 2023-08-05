"""
Connecting to a set of solr servers.

To get a :class:`~solrcloudpy.SolrCollection` instance from a :class:`SolrConnection` use either dictionary-style or attribute-style access:


    >>> from solrcloudpy.connection import SolrConnection
    >>> conn = SolrConnection()
    >>> conn.list()
    [u'collection1']
    >>> conn['collection1']
    SolrCollection<collection1>


"""
import urllib
import json

import solrcloudpy.collection as collection
from solrcloudpy.utils import _Request

class SolrConnection(object):
    """
    Connection to a solr server or several ones

    :param server: The server. Can be a single one or a list of servers. Example  ``localhost:8983`` or ``[localhost,solr1.domain.com:8983]``.
    :param detect_live_nodes: whether to detect live nodes automativally or not. This assumes that one is able to access the IPs listed by Zookeeper. The default value is ``False``.

    :param user: HTTP basic auth user name
    :param password: HTTP basic auth password
    :param timeout: timeout for HTTP requests
    """
    def __init__(self,server="localhost:8983",
                 detect_live_nodes=False,
                 user=None,
                 password=None,
                 timeout=10):
        self.user = user
        self.password = password
        if type(server) == type(''):
            self.url = "http://%s/solr/" % server
            servers = [self.url,self.url]
            if detect_live_nodes:
                url = servers[0]
                self.servers = self.detect_nodes(url)
            else:
                self.servers = servers
        if type(server) == type([]):
            servers = ["http://%s/solr/" % a for a in server]
            if detect_live_nodes:
                url = servers[0]
                self.servers = self.detect_nodes(url)
            else:
                self.servers = servers

        self.client = _Request(self,timeout)

    def detect_nodes(self,url):
        url = url+'zookeeper?path=/live_nodes'
        live_nodes = urllib.urlopen(url).read()
        data = json.loads(live_nodes)
        children = [d['data']['title'] for d in data['tree'][0]['children']]
        nodes = [c.replace('_solr','') for c in children]
        return ["http://%s/solr/" % a for a in nodes]

    def list(self):
        """
        Lists out the current collections in the cluster
        """
        params = {'detail':'false','path':'/collections'}
        response = self.client.get('/solr/zookeeper',params).result
        data = response['tree'][0]['children']
        colls = [node['data']['title'] for node in data]
        return colls

    def _list_cores(self):
        params = {'wt':'json',}
        response = self.client.get('admin/cores',params).result
        cores = response.get('status',{}).keys()
        return cores

    @property
    def cluster_health(self):
        """
        Determine the state of all nodes and collections in the cluster. Problematic nodes or
        collections are returned, along with their state, otherwise an `OK` message is returned
        """
        params = {'detail':'true','path':'/clusterstate.json'}
        response = self.client.get('/solr/zookeeper',params).result
        data = json.loads(response['znode']['data'])
        res = []
        collections = self.list()
        for coll in collections:
            shards = data[coll]['shards']
            for shard,shard_info in shards.iteritems():
                replicas = shard_info['replicas']
                for replica, info in replicas.iteritems():
                    state = info['state']
                    if state != 'active':
                        item = {"collection":coll,
                                "replica":replica,
                                "shard":shard,
                                "info": info,
                                }
                        res.append(item)

        if not res:
            return {"status": "OK"}

        return {"status": "NOT OK", "details": res}

    @property
    def cluster_leader(self):
        """
        Gets the cluster leader
        """
        params = {'detail':'true','path':'/overseer_elect/leader'}
        response = self.client.get('/solr/zookeeper',params).result
        return json.loads(response['znode']['data'])

    @property
    def live_nodes(self):
        """
        Lists all nodes that are currently online
        """
        params = {'detail':'true','path':'/live_nodes'}
        response = self.client.get('/solr/zookeeper',params).result
        children = [d['data']['title'] for d in response['tree'][0]['children']]
        nodes = [c.replace('_solr','') for c in children]
        return ["http://%s/solr/" % a for a in nodes]

    def create_collection(self,collname, *args, **kwargs):
        r"""
        Create a collection.

        :param collname: The collection name
        :param \*args: additiona arguments
        :param \*\*kwargs: additional named parameters
        """
        coll = collection.SolrCollection(self,collname)
        return coll.create(*args, **kwargs)

    def __getattr__(self, name):
        return collection.SolrCollection(self,name)

    def __getitem__(self, name):
        return collection.SolrCollection(self,name)

    def __dir__(self):
        return self.list()

    def __repr__(self):
        return "SolrConnection %s" % str(self.servers)
