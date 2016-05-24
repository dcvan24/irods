#!/usr/bin/env python

import os
import sys
import uuid
import json
import atexit
import socket
import requests
import netifaces as ni

from argparse import ArgumentParser
from subprocess import Popen, PIPE

OPERATION = 'iput'
ICAT_HOST = 'icat'
LOCAL_HOSTNAME = socket.gethostname()
LOCAL_IP_ADDR = ni.ifaddresses('eth1')[2][0]['addr'] 
DEFAULT_IFACE = 'eth1'
TMP_PORT_ENTRY = '/tmp/irods/irods_local_port'
MAX_PORT_VALUE = 65565
LOCAL_PORT_START = 60000
DEFAULT_BANDWIDTH = '10M'
CONTROLLER_WSGI_URL = 'http://165.124.159.6:8080'
HTTP_HEADERS = {
    'content-type': 'application/json' 
}

def create_args():
   parser = ArgumentParser(
           description='SDN-enabled iRODS iput Utility')
   parser.add_argument('-N', '--num-thread',
           type=int, dest='num_thread',
           help='use specific number of TCP streams to transfer data')
   parser.add_argument('-R', '--resource',
           type=str, dest='resource', 
           default='%sResource'%socket.gethostname(),
           help='resource name')
   parser.add_argument('-b', '--bandwidth',
           type=int, dest='bandwidth', default=DEFAULT_BANDWIDTH,
           help='bandwidth demand in (K/M/G)')
   parser.add_argument('--metadata',
           type=str, dest='metadata',
           help='metadata tag')
   parser.add_argument('-f', '--force',
           dest='is_force', action='store_true',
           help='whether force overriding existing file')
   parser.add_argument('-v', '--verbose',
           dest='is_verbose', action='store_true',
           help='verbose')
   parser.add_argument('-V', '--very-verbose',
           dest='is_very_verbose', action='store_true',
           help='very verbose')
   parser.add_argument('path', action='store')

   return parser.parse_args()

def init_args(args):
    args.transfer_id = '%s-%s'%(LOCAL_HOSTNAME, str(uuid.uuid4()))
    args.path = os.path.abspath(args.path)
    # set number of threads if not set
    if not args.num_thread:
        file_size = os.stat(args.path).st_size
        args.num_thread = get_num_thread(file_size)
    args.local_port = get_port(args.num_thread)
    args.has_requested_controller = False

def request_management_flows(args):
    print 'Request management flow'
    res = http_put('/client/%s'%LOCAL_HOSTNAME, {
        'client_ip': LOCAL_IP_ADDR,
        'icat_ip': socket.gethostbyname(ICAT_HOST)
    })

def request_data_transfer_flows(args):
    print "Request data transfer flows"
    dst_ip = get_resource_ip_addr(args.resource)
    if not dst_ip:
        return {}
    data = {
        'src_ip': LOCAL_IP_ADDR,
        'dst_ip': dst_ip,
        'num_thread': args.num_thread,
        'src_port': args.local_port,
        'bandwidth': args.bandwidth,
    }
    if args.metadata:
        data['metadata'] = args.metadata
    has_requested_controller = True
    r = http_put('/transfer/%s'%args.transfer_id, data)
    if not r.ok:
        raise Exception(r.text)
    args.has_requested_controller = True
    return r.json()

def create_command(args):
    cmd = ['iput']
    cmd.extend(['-R', args.resource])
    cmd.extend(['-N', str(args.num_thread)])
    cmd.extend(['-L', str(args.local_port)])
    if args.metadata:
        cmd.append('--metadata=meta;%s'%args.metadata)
    if args.is_force:
        cmd.append('-f')
    if args.is_very_verbose:
        cmd.append('-V')
    elif args.is_verbose:
        cmd.append('-v')
    cmd.append(args.path)
    return cmd

def execute_command(cmd):
    print 'Start transfer'
    out, err = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
    if err:
        raise Exception(err)
    if len(out) > 0:
        print out,
    print 'Transfer done'

def clean_up(args):
    print 'Clean up'
    if args.has_requested_controller:
        r = http_delete('/transfer/%s'%args.transfer_id)
        if not r.ok:
            sys.stderr.write(r.text)

def get_num_thread(file_size):
    file_size /= 1024 ** 2
    file_size = 32 if file_size > 32 else file_size
    return file_size * 2 if file_size else 1

def get_port(num_thread):
    port = None
    if os.path.exists(TMP_PORT_ENTRY):
        with open(TMP_PORT_ENTRY, 'r+b') as f:
            port = int(f.readline(5))
            if MAX_PORT_VALUE - port < num_thread:
                port = LOCAL_PORT_START
            f.seek(0)
            f.write('%d'%(port + num_thread))
            f.truncate()
    else:
        port = LOCAL_PORT_START
        with open(TMP_PORT_ENTRY, 'w') as f:
            f.write('%d'%(LOCAL_PORT_START + num_thread))
    return port

def get_resource_ip_addr(resource):
    hostname = resource[:resource.index('R')]
    localhost = socket.gethostname() 
    if localhost == hostname:
        return None
    ip = socket.gethostbyname(hostname)
    return ip

def http_put(path, data):
    r = requests.put(
        '%s%s'%(CONTROLLER_WSGI_URL, path),
        data=json.dumps(data), headers=HTTP_HEADERS)
    try:
        return r
    except Exception, e:
        return {}

def http_delete(path):
    r = requests.delete(
        '%s%s'%(CONTROLLER_WSGI_URL, path))
    return r

if '__main__' == __name__:
    args = create_args()
    atexit.register(clean_up, args)
    try:
        init_args(args)
        request_management_flows(args)
        alloc = request_data_transfer_flows(args)
        print json.dumps(alloc, sort_keys=True, indent=4)
        cmd = create_command(args)
        print cmd
        execute_command(cmd)
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print e
        sys.exit(str(e))
