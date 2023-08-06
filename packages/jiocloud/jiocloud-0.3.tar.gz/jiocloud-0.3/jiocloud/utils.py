#!/usr/bin/env python
import argparse
import IPy
import os
from novaclient import client as novaclient

"""
Various utils
"""

def get_nova_creds_from_env():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    d['region_name'] = os.environ.get('OS_REGION_NAME')
    return d

def get_nova_client():
    return novaclient.Client("1.1", **get_nova_creds_from_env())

def is_rfc1918(ip_string):
    ip = IPy.IP(ip_string)
    if ip in IPy.IP('10.0.0.0/8'):
        return True
    if ip in IPy.IP('192.168.0.0/16'):
        return True
    if ip in IPy.IP('172.16.0.0/12'):
        return True
    return False

def get_ip_of_node(nova_client, name):
    ip = None
    for server in nova_client.servers.list():
        if server.name.split('_')[-1] == name:
            for network in server.networks.values():
                for ip in network:
                    if not is_rfc1918(ip):
                        return ip
            # Fallthrough... If none are non-rfc1918 just return whatever
            return ip
        raise Exception('Server not found')

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(dest='action', help='Action to perform')

    get_ip_of_node_parser = subparsers.add_parser('get_ip_of_node', help='Get IP for node')
    get_ip_of_node_parser.add_argument('node_name', help='Node name')

    args = argparser.parse_args()
    nova_client = get_nova_client()

    if args.action == 'get_ip_of_node':
        print get_ip_of_node(nova_client, args.node_name)
