#!/usr/bin/env python 

import os
import requests
import json
import netifaces as ni
from argparse import ArgumentParser
from subprocess import Popen, PIPE

OPERATION='iput'
DEFAULT_IFACE = 'eth1'
DEFAULT_LOCAL_PORT_START = 60000
CONTROLLER_URL = 'http://129.7.98.39:8080'
LOCK_FILE = '/tmp/iput.lock'

def create_args():
    parser = ArgumentParser(
            description='SDN-enabled iRODS iput Utility')
    
    parser.add_argument('-f', '--force',
            dest='force', action='store_true',
            help='whether force overriding existing file')
    parser.add_argument('-v', '--verbose',
            dest='verbose', action='store_true',
            help='verbose')
    parser.add_argument('-V', '--very-verbose',
            dest='very_verbose', action='store_true',
            help='very_verbose')
    parser.add_argument('-R', '--resource', 
            type=str, dest='resource', 
            help='resource name')
    parser.add_argument('-N', '--num-thread', 
            type=int, dest='num_thread', 
            help='number of parallel threads to use')
    parser.add_argument('--metadata', 
            type=str, dest='metadata', 
            help='metadata tag')
    
    return parser.parse_args()

def get_local_port(num_thread):
    pass

def get_local_ip_addr():
    return ni.ifaddresses(DEFAULT_IFACE)[2][0]['addr']

def send_request(tcp_info, metadata):
    '''
        tcp_info::tuple - (src_ip, src_port_start, src_port_end)
        metadata::str - metadata tag
    '''
    data = json.dumps({
        'tcp_info': tcp_info,
        'operation': OPERATION,
        'metadata': metadata
    })
    res = requests.put(CONTROLLER_URL, data=data)
    

def create_command(args):
    pass

if '__main__' == __name__:
    print get_local_port()
    print get_local_ip_addr()
