#!/usr/bin/env python3
# Copyright (c) 2018 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the
# Apache License, Version 2.0 (the "License").
# You may not use this product except in compliance with the License.
#
# This product may include a number of subcomponents with
# separate copyright notices and license terms. Your use of the source
# code for the these subcomponents is subject to the terms and
# conditions of the subcomponent's license, as noted in the LICENSE file.

# Example procedure to onboard a tenant. This file reads the desired org,
# user, catalog contents, network, and vapp(s) from a configuration file.
# It adds anything that is missing.  If everything already exists, the
# sample procedure does nothing.
#
# https://github.com/vmware/pyvcloud/blob/master/examples/tenant-onboard.py
# Usage: python3 tenant-onboard.py tenant.yaml

import os
from collections import namedtuple
import requests
import sys
import time
import yaml
import sys
import subprocess
import argparse
import configparser

# Private utility functions.
from tenantlib import handle_task

from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import FenceMode
from pyvcloud.vcd.client import QueryResultFormat
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.system import System
from pyvcloud.vcd.utils import to_dict
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.exceptions import EntityNotFoundException

lastMasterIp = ''

def create_vm(vms, source_vapp_resource, vm_cfg, master_name, master=False):
    try:
        global lastMasterIp
        vm = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm)
        ip = vm_obj.list_nics()[0]['ip_address'].ljust(20)
        if master:
            #gen_key(vm_cfg['name'],os.environ['SSH_USERNAME'],os.environ['SSH_PASSWORD'], ip)
            lastMasterIp = ip
        if vm_obj.is_powered_on() == True:
            print("    VM '{0}' ... OK".format(vm_cfg['name']))
        else:
            print("    VM '{0}' ... DOWN -> starting ...\r".format(vm_cfg['name']), end='')
            result = vm_obj.power_on()
            handle_task(client, result)
            print("    VM '{0}' ... UP {1}".format(vm_cfg['name'], "".ljust(20)))
        #if not master:
        #    push_key(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)

    except EntityNotFoundException:
        print("    VM '{0}' ... NONE -> marked for creation ...".format(vm_cfg['name']))               
        spec = {'source_vm_name': vm_cfg['source_vm_name'], 'vapp': source_vapp_resource}
        spec['target_vm_name'] = vm_cfg['name']
        spec['hostname'] = vm_cfg['hostname']
        vms.append(spec)

def create_master_vm(vms, source_vapp_resource, vm_cfg):
    # Generating ssh keys
    create_vm(vms, source_vapp_resource, vm_cfg, master_name=vm_cfg['name'], master=True)

def create_slave_vm(vms, master_name, source_vapp_resource, vm_cfg):
    create_vm(vms, source_vapp_resource, vm_cfg, master_name=master_name, master=False)

def generate_key(vms, source_vapp_resource, vm_cfg):
    try:
        global lastMasterIp
        vm = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm)
        ip = vm_obj.list_nics()[0]['ip_address'].ljust(20)
        lastMasterIp = ip
        gen_key(vm_cfg['name'],os.environ['SSH_USERNAME'],os.environ['SSH_PASSWORD'], ip)
    except EntityNotFoundException:
        print("    Cannot generate certificate on VM '{0}'".format(vm_cfg['name']))               

def deploy_key(vms, source_vapp_resource, vm_cfg, master_name):
    try:
        vm = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm)
        ip = vm_obj.list_nics()[0]['ip_address'].ljust(20)
        push_key(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)
    except EntityNotFoundException:
        print("    Cannot deploy certificate on VM '{0}'".format(vm_cfg['name']))               

def gen_key(master_name,user,password, host):
    print("Generate a SSH Key...")
    """Generate a SSH Key."""
    # Genarate private key on local env
    command = "sshpass -p {1} ssh -t {1}@{2} \"yes y | ssh-keygen -t rsa -b 4096 -f /home/{1}/.ssh/id_rsa -C {1} -P ''\"".format(master_name,user,host)
    subprocess.call(command, shell=True)

def deploy_tool(vms, source_vapp_resource, vm_cfg, master_name):
    try:
        vm = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm)
        ip = vm_obj.list_nics()[0]['ip_address'].ljust(20)
        install_sshpass(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)
    except EntityNotFoundException:
        print("    Cannot deploy tool on VM '{0}'".format(vm_cfg['name']))               

def install_sshpass(user, password, host, master_name):
    global lastMasterIp
    print("Installing sshpass... to {0} from host {1} ".format(host, lastMasterIp))
    # Installing shpass tool to allow to send command with password without prompt
    command = "sshpass -p {0} ssh -t {2}@{4} ' sudo -S <<< \"{0}\" yum --enablerepo=epel -y install sshpass'".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

def push_key(user, password, host, master_name):
    global lastMasterIp
    command = "sshpass -p {0} ssh -t {2}@{4} 'yes y | sshpass -p {0}  ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa.pub {2}@{3}'".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

# Collect arguments.
if len(sys.argv) != 2:
    print("Usage: python3 {0} config_file".format(sys.argv[0]))
    sys.exit(1)
config_yaml = sys.argv[1]

# Load the YAML configuration and convert to an object with properties for
# top-level entries.  Values are either scalar variables, dictionaries,
# or lists depending on the structure of the YAML.
with open(config_yaml, "r") as config_file:
    config_dict = yaml.safe_load(config_file)
    cfg = namedtuple('ConfigObject', config_dict.keys())(**config_dict)

#Build host.ini file
host = configparser.ConfigParser()
for vm_cfg in cfg.vapp['vms']:
    print(vm_cfg)
    host["master"]
    source_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
    create_master_vm(vms, source_vapp_resource, vm_cfg)
    for vm_slave_cfg in vm_cfg['slaves']:
        source_slave_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
        create_slave_vm(vms,vm_cfg['name'], source_slave_vapp_resource, vm_slave_cfg)
        
print("Creating (if needed) ...") 
result = vapp.add_vms(vms)
handle_task(client, result)

print("Statuses ...")     
while (vapp.get_all_vms() is None or len(vapp.get_all_vms()) < len(cfg.vapp['vms'])):
    print("  VMs ... {0}\r".format("waiting full start ...".ljust(20)), end='')
    vapp.reload()

for vm in vapp.get_all_vms():
    vm_obj = VM(client, resource=vm)
    while(vm_obj.is_powered_on() == False):
        print("  VM '{0}' ... {1}\r".format(vm.get('name'), "DOWN (waiting)".ljust(20)), end='')
        vm_obj.reload()
        time.sleep(5)
    print("  VM '{0}' ... {1}\r".format(vm.get('name'), "UP").ljust(20), end='')
    while(vm_obj.list_nics() is None or (len(vm_obj.list_nics()) == 0) or ('ip_address' not in vm_obj.list_nics()[0].keys())) :
        print("  VM '{0}' ... {1}  -  IP = {2}\r".format(vm.get('name'), "UP", "... (waiting)".ljust(20)), end='')
        vm_obj.reload()
        time.sleep(5)
    print("  VM '{0}' ... {1}  -  IP = {2}".format(vm.get('name'), "UP", vm_obj.list_nics()[0]['ip_address'].ljust(20)))

# Deploying tool
for vm_cfg in cfg.vapp['vms']:
    print(vm_cfg)
    source_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
    generate_key(vms, source_vapp_resource, vm_cfg)
    for vm_slave_cfg in vm_cfg['slaves']:
        try:
            source_slave_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
            deploy_tool(vms, source_slave_vapp_resource, vm_slave_cfg, vm_cfg['name'])
        except Exception:
            print("error")

# Deploying keys
for vm_cfg in cfg.vapp['vms']:
    print(vm_cfg)
    for vm_slave_cfg in vm_cfg['slaves']:
        try:
            time.sleep(5.0)
            source_slave_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
            deploy_key(vms, source_slave_vapp_resource, vm_slave_cfg, vm_cfg['name'])
        except Exception:
            print("error")
        

# Log out.
print("All done!")
client.logout()