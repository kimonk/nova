__author__ = 'akis'

from novaclient import client

nova = client.Client('2.19', 'admin', 'akis100', 'demo', 'http://192.168.1.7:5000/v2.0')



#print(nova.hosts.get('akis-petaTest'))

#print(nova.hypervisors.list(True))

#print(nova.hypervisors.get(1).NAME_ATTR)


print(nova.bitstreams.list())
print(nova.images.list())