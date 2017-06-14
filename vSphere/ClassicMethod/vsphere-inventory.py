#!/usr/bin/env python
# pylint: disable=I0011,C0103,W0703

"""
Copyright (C) 2017 - Julien Blanc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Requirements :
- pip install pyVmomi
"""

import json
import warnings
import atexit
import platform
import ssl

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


# INVENTORY MODEL
hosts = {
    'Hypervisors': {},
    'VirtualMachines': {}
}

hosts['Hypervisors']['hosts'] = []
hosts['VirtualMachines']['hosts'] = []

hosts['_meta'] = {
    'hostvars': {}
}


#------------- Create view from vCenter
def createVIew(instance, obj):
    """
    CREATE VIEW
    """
    content = instance.RetrieveContent()
    container = content.rootFolder      # Starting point to look into
    viewType = obj                      # Object types to look for
    recursive = True                    # Whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    return containerView.view


#------------- Get VMS
def get_vm(vm):
    """
    GET VM INFORMATION
    """
    summary = vm.summary

    if summary.config.template != True:
        hosts['VirtualMachines']['hosts'].append(summary.config.name)

        hosts['_meta']['hostvars'][summary.config.name] = {
            'ansible_host':     str(summary.guest.ipAddress),
            'folder':           vm.parent.name,
            'system':           summary.config.guestFullName,
            'memory':           summary.config.memorySizeMB,
            'numCpu':           summary.config.numCpu,
            'numNics':          summary.config.numEthernetCards,
            'storage':          round((summary.storage.committed+
                                       summary.storage.uncommitted)/1024/1024/1024, 2),
            'status':           summary.runtime.powerState,
            'bootTime':         str(summary.runtime.bootTime)
        }


#------------- Get hypervisors
def get_host(host):
    """
    GET HOST INFORMATION
    """
    summary = host.summary

    hosts['Hypervisors']['hosts'].append(summary.config.name)

    hosts['_meta']['hostvars'][summary.config.name] = {
        'ansible_host':     str(summary.managementServerIp),
        'system':           summary.config.product.fullName,
        'memory':           int(round(summary.hardware.memorySize/1024/1024)),
        'numCpu':           summary.hardware.numCpuPkgs,
        'numCores':         summary.hardware.numCpuCores,
        'numThreads':       summary.hardware.numCpuThreads,
        'numNics':          summary.hardware.numNics,
        'status':           summary.runtime.powerState,
        'bootTime':         str(summary.runtime.bootTime)
    }


def main():
    """
    MAIN
    """
    # IGNORE WARNINGS TO CLEAN OUTPUT
    warnings.filterwarnings("ignore")

    # ERRORS
    error = False

    # GET CONNEXION PARAMETERS
    with open('/etc/ansible/vsphere-inventory.json') as opts_file:
        opts = json.load(opts_file)

    vcenter = opts["vcenter"]
    user = opts["user"]
    password = opts["password"]
    ssl_verify = opts["ssl_verify"]

    # SSL CONTEXT
    context = None

    # DISABLE SSL VERIFICATION FOR SELF-SIGNED CERTIFICATES
    if ssl_verify is not True:
        if platform.python_version() != "2.7.6":
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_NONE

    try:
        # VCENTER CONNECTION
        service_instance = SmartConnect(host=vcenter,
                                        user=user,
                                        pwd=password,
                                        port=int(443),
                                        sslContext=context)

        atexit.register(Disconnect, service_instance)

    except Exception:
        print(">>> Can't connect to " + vcenter)
        error = True

    if error is not True:

        # GET HOSTS
        children = createVIew(service_instance, [vim.HostSystem])

        for child in children:
            get_host(child)

        # GET VMs
        children = createVIew(service_instance, [vim.VirtualMachine])

        for child in children:
            get_vm(child)

        # EXPORT JSON TO STANDARD OUTPUT
        print(json.dumps(hosts, sort_keys=True, indent=2))


# START PROGRAM
if __name__ == "__main__":
    main()
