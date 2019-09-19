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

from collections import namedtuple
import os
import requests
import sys
import time
import yaml
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
client.set_credentials(BasicLoginCredentials(os.environ['VCLOUD_USERNAME'],
                       os.environ['VCLOUD_ORG'], os.environ['VCLOUD_PASSWORD']))

# Ensure the org exists.
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

vdc.reload()

vapp_resource = vdc.get_vapp(cfg.vapp['name'])
vapp = VApp(client, resource=vapp_resource)


print("Prepare Host.ini file ...")     
hostconfig = configparser.ConfigParser(allow_no_value=True)
hostconfig['all:vars'] = {'ansible_connection': 'ssh',
'ansible_user': os.environ['SSH_USERNAME'],
'ansible_ssh_private_key_file':'~/.ssh/id_ansible_rsa',
'ansible_become_pass': os.environ['SSH_PASSWORD']}
  
for vm_cfg in cfg.vapp['vms']:
    try:
        vm_resource = vapp.get_vm(vm_cfg['name'])
        vm_obj = VM(client, resource=vm_resource)
        print("Adding Master {0} -> {1}".format(vm_resource.get('name'),vm_obj.list_nics()[0]['ip_address'].ljust(20)))
        if not hostconfig.has_section('master'):
            hostconfig.add_section('master')
        hostconfig.set("master",vm_obj.list_nics()[0]['ip_address'].ljust(20))
        for vm_slave_cfg in vm_cfg['slaves']:
            try:
                vm_resource = vapp.get_vm(vm_slave_cfg['name'])
                vm_slave_obj = VM(client, resource=vm_resource)
                if not hostconfig.has_section('node'):
                    hostconfig.add_section('node')
                print("Adding Node {0} -> {1}".format(vm_resource.get('name'),vm_slave_obj.list_nics()[0]['ip_address'].ljust(20)))
                hostconfig.set("node",vm_slave_obj.list_nics()[0]['ip_address'].ljust(20))
            except Exception:
                print("error") 
    except Exception:
        print(" Error writing VM '{0}' ...".format(vm_cfg['name']))
        exit(0)
    hostconfig.add_section('kube-cluster:children')
    hostconfig.set("kube-cluster:children","master")
    hostconfig.set("kube-cluster:children","node")
    hostconfig.set("all:vars",'ansible_ssh_user',os.environ['SSH_USERNAME'])

with open('ansible/host.ini', 'w') as configfile:
    hostconfig.write(configfile)
# Log out.
print("All done!")
client.logout()