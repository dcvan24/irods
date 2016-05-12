#!/usr/bin/env python

import os
import sys
import uuid
import json
import socket
import requests
import logging
import netifaces as ni

from argparse import ArgumentParser
from subprocess import Popen, PIPE

TMP_PORT_ENTRY = '/tmp/irods/irods_local_port'
TMP_ICAT_ENTRY = '/tmp/irods/icat_connected'
MAX_PORT_VALUE = 65565
LOCAL_PORT_START = 60000
DEFAULT_BANDWIDTH = '10M'
CONTROLLER_WSGI_URL = 'http://129.7.98.12:8080'
HTTP_HEADERS = {
    'content-type': 'application/json' 
}

has_requested_controller = False

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
           type=str, dest='bandwidth', default=DEFAULT_BANDWIDTH,
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
    args.transfer_id = '%s-%s'%(socket.gethostname(), str(uuid.uuid4()))
    args.path = os.path.abspath(args.path)
    # set number of threads if not set
    if not args.num_thread:
        file_size = os.stat(args.path).st_size
        args.num_thread = get_num_thread(file_size)
    args.local_port = get_port(args.num_thread)
    args.bandwidth = parse_bandwidth(args.bandwidth)

def request_icat_path(args):
    res = http_put('/icat/%s'%args.transfer_id, {
        'src_ip': ni.ifaddresses('eth1')[2][0]['addr'],
        'dst_ip': socket.gethostbyname('icat')
    })


def request_bandwidth(args):
    dst_ip = get_resource_ip_addr(args.resource)
    if not dst_ip:
        return {}

    with open(TMP_ICAT_ENTRY, 'w') as f:
        f.write('')

    data = {
        'src_ip': ni.ifaddresses('eth1')[2][0]['addr'],
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
    return r.json()

def limit_rate(alloc):
    pass

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
    out, err = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
    if err:
        raise Exception(err)
    print out

def clean_up(args):
    return http_delete('/transfer/%s'%args.transfer_id)

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
            f.write('%d'%(port + num_thread))
    else:
        port = LOCAL_PORT_START
        with open(TMP_PORT_ENTRY, 'w') as f:
            f.write('%d'%(LOCAL_PORT_START + num_thread))
    return port

def parse_bandwidth(bandwidth):
    unit = bandwidth[-1]
    val = int(bandwidth[:-1])
    if unit not in ('M', 'G'):
        raise ValueError('Invalid bandwidth value')
    elif 'G' == unit:
        val *= 1000 
    return val

def get_resource_ip_addr(resource):
    hostname = resource[:resource.index('R')]
    localhost = socket.gethostname() 
    if localhost == hostname:
        return None
    if resource == 'demoResc':
        return socket.gethostbyname('icat')
    ip = socket.gethostbyname(hostname)
    return ip

def http_put(path, data):
    r = requests.put(
        '%s%s'%(CONTROLLER_WSGI_URL, path),
        data=json.dumps(data), headers=HTTP_HEADERS)
    try:
        return r
    except Exception, e:
        logging.exception(str(e))
        return {}

def http_delete(path):
    r = request.delete(
        '%s%s'%(CONTROLLER_WSGI_URL, path))
    return r

if '__main__' == __name__:
    args = create_args()
    try:
        init_args(args)
        request_icat_path(args)
        alloc = request_bandwidth(args)
        #if alloc:
        #    limit_rate(alloc)
        cmd = create_command(args)
        print cmd
        execute_command(cmd)
    #except KeyboardInterrupt:
    #    pass
    #except Exception, e:
    #    sys.exit(str(e))
    finally:
        if has_requested_controller:
            r = clean_up(args)
            if not r.ok:
                logging.error(r.text)
