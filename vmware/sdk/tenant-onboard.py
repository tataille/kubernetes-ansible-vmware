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

def deploy_local_key(vms, source_vapp_resource, vm_cfg, master_name):
    try:
        vm = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm)
        ip = vm_obj.list_nics()[0]['ip_address'].ljust(20)
        push_local_key(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)
    except EntityNotFoundException:
        print("    Cannot deploy certificate on VM '{0}'".format(vm_cfg['name']))          

def gen_key(master_name,user,password, host):
    print("Generate a remote SSH Key...")
    """Generate a SSH Key."""
    # Genarate private key on remote env, for ease of remote hosts use
    command = "sshpass -p {1} ssh -t {1}@{2} \"yes y | ssh-keygen -t rsa -b 4096 -f /home/{1}/.ssh/id_rsa -C {1} -P ''\"".format(master_name,user,host)
    subprocess.call(command, shell=True)
    # Genarate private key on local env, for ansible
    print("Generate Ansible SSH Key...")
    command = "yes y | ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_ansible_rsa -C {1} -P ''".format(master_name,user,host)
    subprocess.call(command, shell=True)

def open_secure_port( master_name):
    global lastMasterIp
    print("Opening secured port 6443... to  host {0} ".format( lastMasterIp))
    user =os.environ['SSH_USERNAME']
    password = os.environ['SSH_PASSWORD']
    # Installing shpass tool to allow to send command with password without prompt
    command = "sshpass -p {0} ssh -t {1}@{2} ' sudo -S <<< \"{0}\" firewall-cmd --zone=public --add-port=6443/tcp --permanent'".format(password, user,lastMasterIp)
    subprocess.call(command, shell=True)
    command = "sshpass -p {0} ssh -t {1}@{2} ' sudo -S <<< \"{0}\" firewall-cmd --reload'".format(password, user,lastMasterIp)
    subprocess.call(command, shell=True)
    

def deploy_tool(vms, source_vapp_resource, vm_cfg, master_name):
    try:
        vm = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm)
        ip = vm_obj.list_nics()[0]['ip_address'].ljust(20)
        upgrade_os(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)
        install_sshpass(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)
        install_git(os.environ['SSH_USERNAME'], os.environ['SSH_PASSWORD'], ip, master_name)
    except EntityNotFoundException:
        print("    Cannot deploy tool on VM '{0}'".format(vm_cfg['name']))               

def upgrade_os(user, password, host, master_name):
    global lastMasterIp
    print("Upgrading OS... to {0} from host {1} ".format(host, lastMasterIp))
    # Installing shpass tool to allow to send command with password without prompt
    command = "sshpass -p {0} ssh -t {2}@{4} ' sudo -S <<< \"{0}\" yum -y upgrade'".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

def install_sshpass(user, password, host, master_name):
    global lastMasterIp
    print("Installing sshpass... to {0} from host {1} ".format(host, lastMasterIp))
    # Installing shpass tool to allow to send command with password without prompt
    command = "sshpass -p {0} ssh -t {2}@{4} ' sudo -S <<< \"{0}\" yum --enablerepo=epel -y install sshpass'".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

def install_git(user, password, host, master_name):
    global lastMasterIp
    print("Installing git... to {0} from host {1} ".format(host, lastMasterIp))
    # Installing shpass tool to allow to send command with password without prompt
    command = "sshpass -p {0} ssh -t {2}@{4} ' sudo -S <<< \"{0}\" yum -y install git'".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

def push_key(user, password, host, master_name):
    global lastMasterIp
    command = "sshpass -p {0} ssh -t {2}@{4} 'yes y | sshpass -p {0}  ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa.pub {2}@{3}'".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

def push_local_key(user, password, host, master_name):
    global lastMasterIp
    command = "sshpass -p {0}  ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/id_ansible_rsa.pub {2}@{3}".format(password, master_name, user, host,lastMasterIp)
    subprocess.call(command, shell=True)

# Helper functions for creating VDCs.
def _fill_in_pvdc_default(client, vdc_kwargs):
    """Convert '*' value to a default pvcd name"""
    pvdc_name = vdc_kwargs['provider_vdc_name']
    if pvdc_name == '*':
        system = System(client, admin_resource=client.get_admin())
        pvdc_refs = system.list_provider_vdcs()
        for pvdc_ref in pvdc_refs:
            pvdc_name = pvdc_ref.get('name')
            print("Defaulting to first pvdc: {0}".format(pvdc_name))
            vdc_kwargs['provider_vdc_name'] = pvdc_name
            break

        if vdc_kwargs['provider_vdc_name'] == '*':
            raise Exception("Unable to find default provider VDC")

def _fill_in_netpool_default(client, vdc_kwargs):
    """Convert '*' value to a default netpool name"""
    netpool_name = vdc_kwargs['network_pool_name']
    if netpool_name == '*':
        system = System(client, admin_resource=client.get_admin())
        netpools = system.list_network_pools()
        for netpool in netpools:
            netpool_name = netpool.get('name')
            print("Defaulting to first netpool: {0}".format(netpool_name))
            vdc_kwargs['network_pool_name'] = netpool_name
            break

        if vdc_kwargs['network_pool_name'] == '*':
            raise Exception("Unable to find default netpool")

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

# Disable warnings from self-signed certificates.
requests.packages.urllib3.disable_warnings()

# Login. SSL certificate verification is turned off to allow self-signed
# certificates.  You should only do this in trusted environments.
print("Logging in...")
client = Client(os.environ['VCLOUD_HOST'], verify_ssl_certs=False,
                api_version='27.0',
                log_file='pyvcloud.log',
                log_requests=True,
                log_headers=True,
                log_bodies=True)
               

print("  Username '{0}'".format(os.environ['VCLOUD_USERNAME']))

client.set_credentials(BasicLoginCredentials(os.environ['VCLOUD_USERNAME'],
                       os.environ['VCLOUD_ORG'], os.environ['VCLOUD_PASSWORD']))

# Ensure the org exists.
print("Fetching org...")
try:
    # This call gets a record that we can turn into an Org class.
    org_record = client.get_org_by_name(os.environ['VCLOUD_ORG'])
    org = Org(client, href=org_record.get('href'))
    print("Org already exists: {0}".format(org.get_name()))
except Exception:
    print("Org does not exist, creating: {0}".format(os.environ['VCLOUD_ORG']))
    sys_admin_resource = client.get_admin()
    system = System(client, admin_resource=sys_admin_resource)
    admin_org_resource = system.create_org(os.environ['VCLOUD_ORG'], "Test Org", True)
    org_record = client.get_org_by_name(os.environ['VCLOUD_ORG'])
    org = Org(client, href=org_record.get('href'))
    print("Org now exists: {0}".format(org.get_name()))

# Ensure VDC exists.
try:
    vdc_resource = org.get_vdc(os.environ['VCLOUD_VDC_NAME'])
    vdc = VDC(client, resource=vdc_resource)
    print("  VDC '{0}' ... OK".format(os.environ['VCLOUD_VDC_NAME']))
except Exception:

    print("  VDC '{0}' ... KO. Exiting.".format(os.environ['VCLOUD_VDC_NAME']))
    exit(0)

# # Fetching catalogs
#try:
#    catalogs_resource = org.list_catalogs()
#    print("Catalogs: {0}".format(catalogs_resource))
#except Exception:
#     print("Catalogs fetch error")

# List catalog items (Templates).
#try:
#    catalog_items = org.list_catalog_items(cfg.catalog['name'])
#    print("Catalog items: {0}".format(catalog_items))
#except Exception:
#    print("Catalog items fetch error")
#    exit(0)

# Ensure the catalog (vApp template) and catalog item (VM template) exists

for vm_cfg in cfg.vapp['vms']:
    try:
        catalog = org.get_catalog(vm_cfg['catalog'])
        print("  Catalog '{0}' ... OK".format(vm_cfg['catalog']))
    except Exception:
        print("  Catalog '{0}' ... KO. Exiting.".format(vm_cfg['catalog']))
        exit(0)

    try:
        catalog_item = org.get_catalog_item(vm_cfg['catalog'],vm_cfg['catalog_item'])
        print("  Catalog item '{0} / {1}' ... OK".format(vm_cfg['catalog'],vm_cfg['catalog_item']))
    except Exception:
        print("  Catalog item '{0} / {1}' ... KO. Exiting.".format(vm_cfg['catalog'],vm_cfg['catalog_item']))
        exit(0)

# Check for vApps and create them if they don't exist.  We have to
# reload the VDC object so it has all the links to current vApps.
vdc.reload()

try:
    vapp = vdc.get_vapp(cfg.vapp['name'])
    print("vApp exists: {0}".format(cfg.vapp['name']))
except Exception:
    print("vApp does not exist: name={0}".format(cfg.vapp['name']))
    vapp = vdc.create_vapp(name=cfg.vapp['name'], description=cfg.vapp['description'], network=cfg.vapp['network'], accept_all_eulas=cfg.vapp['accept_all_eulas'])
    print("  vApp '{0}' ... instanciated ...\r".format(cfg.vapp['name']), end='')
    handle_task(client, vapp.Tasks.Task[0])
    print("  vApp '{0}' ... OK {1}".format(cfg.vapp['name'], "".ljust(20)))
    # We don't track the task as instantiating a vApp takes a while.
    # Uncomment below if you want to ensure the vApps are available.
    # handle_task(client, vapp_resource.Tasks.Task[0])

vdc.reload()

vapp_resource = vdc.get_vapp(cfg.vapp['name'])
vapp = VApp(client, resource=vapp_resource)

vms = []
for vm_cfg in cfg.vapp['vms']:
    print(vm_cfg)
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

vapp.reload()
vm_obj.reload()

# Deploying tool & keys
for vm_cfg in cfg.vapp['vms']:
    print(vm_cfg)
    source_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
    generate_key(vms, source_vapp_resource, vm_cfg)
    deploy_local_key(vms, source_vapp_resource, vm_cfg, vm_cfg['name'])
    # Disabling firewall on port 6443)
    open_secure_port(vm_cfg['name'])
    for vm_slave_cfg in vm_cfg['slaves']:
        try:
            source_slave_vapp_resource = client.get_resource(catalog_item.Entity.get('href'))
            deploy_tool(vms, source_slave_vapp_resource, vm_slave_cfg, vm_cfg['name'])
            deploy_key(vms, source_slave_vapp_resource, vm_slave_cfg, vm_cfg['name'])
            deploy_local_key(vms, source_slave_vapp_resource, vm_slave_cfg, vm_cfg['name'])
        except Exception:
            print("error")

# Log out.
print("All done!")
client.logout()