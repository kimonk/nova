__author__ = 'akis'
from keystoneclient.v2_0 import client

username='admin'
password='akis100'
tenant_name='demo'
auth_url='http://192.168.1.7:5000/v2.0'
keystone=client.Client(username=username, password=password, tenant_name=tenant_name, auth_url=auth_url)

print(keystone.services.list())