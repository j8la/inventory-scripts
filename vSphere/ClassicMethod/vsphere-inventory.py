#!/usr/bin/env python
# pylint: disable=I0011,C0103,W0703,E0611,W0702

"""
Copyright (C) 2018 - Julien Blanc

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
- pip install dnspython
"""

import json
import warnings
import atexit
import platform
import ssl
from timeit import default_timer as timer
from threading import Thread
from decimal import Decimal, ROUND_UP
import dns.resolver

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


############################################################# BEGIN SCRIPT CONFIG
configFile = '/etc/ansible/vsphere-inventory.json'
dnsServers = []
benchmarkMode = False
############################################################# END SCRIPT CONFIG


#------------- PARAMS
# BENCHMARK
if benchmarkMode is True:
    start = timer()

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

# DNS RESOLVER
dnsResolver = dns.resolver.Resolver()
if len(dnsServers) > 0:
    dnsResolver.nameservers = dnsServers


#------------- MULTITHREAD
class getInfo(Thread):
    """
    GET INFO
    """
    def __init__(self, infoType, item):
        Thread.__init__(self)
        self.infoType = infoType
        self.item = item

    def run(self):
        if self.infoType == "vm":
            get_vm(self.item)
        if self.infoType == "host":
            get_host(self.item)


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


#------------- Get IP with a configured domain name at first
def getVmIpWithDomainName(netcfg):
    """
    GET IP WITH A CONFIGURED DOMAIN NAME AT FIRST
    """

    ipaddr = None

    for nic in netcfg:

        for item in nic.ipConfig.ipAddress:
            req = '.'.join(reversed(item.ipAddress.split("."))) + ".in-addr.arpa"

            try:
                dnsResolver.query(req, "PTR")[0].to_text()
                ipaddr = item.ipAddress
            except:
                pass

    if ipaddr is None:
        ipaddr = netcfg[0].ipAddress[0]

    return ipaddr


#------------- Get IP from host and vmk0
def getHostIpVMK0(netcfg):
    """
    GET IP FROM HOST AND VMK0
    """

    ipaddr = None

    for vnic in netcfg:
        if vnic.device == 'vmk0':
            ipaddr = vnic.spec.ip.ipAddress

    return ipaddr


#------------- Get VM Storage
def getVMStorage(vm):
    """
    GET VM STORAGE
    """

    storage = []

    for disk in vm:
        size = Decimal(
            str(float(disk.capacity)/1024/1024/1024)
            ).quantize(Decimal('.01'), rounding=ROUND_UP)
        free = Decimal(
            str(float(disk.freeSpace)/1024/1024/1024)
            ).quantize(Decimal('.01'), rounding=ROUND_UP)
        used = size - free
        usedPer = Decimal(
            str((float(used)/float(size))*100)
            ).quantize(Decimal('.01'), rounding=ROUND_UP)

        storage.append({
            'path': disk.diskPath,
            'size': float(size),
            'free': float(free),
            'used': float(used),
            'usedPer': float(usedPer)
        })

    return storage


#------------- Get VM Memory
def getVMMemory(vm):
    """
    GET VM MEMORY
    """

    size = vm.config.memorySizeMB
    guest = vm.quickStats.guestMemoryUsage
    usedPer = Decimal(
        str((float(guest)/float(size))*100)
        ).quantize(Decimal('.01'), rounding=ROUND_UP)

    memory = {
        'size': size,
        'guest': guest,
        'usedPer': float(usedPer)
    }

    return memory


#------------- Get Host Memory
def getHostMemory(host):
    """
    GET HOST MEMORY
    """

    size = int(round(host.hardware.memorySize/1024/1024))
    used = host.quickStats.overallMemoryUsage
    usedPer = Decimal(
        str((float(used)/float(size))*100)
        ).quantize(Decimal('.01'), rounding=ROUND_UP)

    memory = {
        'size': size,
        'used': used,
        'usedPer': float(usedPer)
    }

    return memory


#------------- Get VM CPU Usage
def getVMCPU(vm):
    """
    GET VM CPU USAGE
    """

    numCpu = vm.config.numCpu
    totalMhz = vm.runtime.maxCpuUsage
    usedMhz = vm.quickStats.overallCpuUsage
    usedPer = Decimal(
        str((float(usedMhz)/float(totalMhz))*100)
        ).quantize(Decimal('.01'), rounding=ROUND_UP)

    cpu = {
        'numCpu': numCpu,
        'totalMhz': totalMhz,
        'usedMhz': usedMhz,
        'usedPer': float(usedPer)
    }

    return cpu

#------------- Get Host CPU informations and Usage
def getHostCPU(host):
    """
    GET HOST CPU
    """

    model = host.hardware.cpuModel
    numCpu = host.hardware.numCpuPkgs
    numCores = host.hardware.numCpuCores
    numThreads = host.hardware.numCpuThreads
    totalMhz = host.hardware.cpuMhz * numCores
    usedMhz = host.quickStats.overallCpuUsage
    usedPer = Decimal(
        str((float(usedMhz)/float(totalMhz))*100)
        ).quantize(Decimal('.01'), rounding=ROUND_UP)

    cpu = {
        'model': model,
        'sockets': numCpu,
        'cores': numCores,
        'threads': numThreads,
        'totalMhz': totalMhz,
        'usedMhz': usedMhz,
        'usedPer': float(usedPer)
    }

    return cpu


#------------- Get VMS
def get_vm(vm):
    """
    GET VM INFORMATION
    """
    summary = vm.summary

    if summary.config.template != True:

        ip = getVmIpWithDomainName(vm.guest.net)
        req = '.'.join(reversed(ip.split("."))) + ".in-addr.arpa"
        host = dnsResolver.query(req, "PTR")[0].to_text()

        hosts['VirtualMachines']['hosts'].append(summary.config.name)

        hosts['_meta']['hostvars'][summary.config.name] = {
            'ansible_host':     ip,
            'hostname':         host,
            'folder':           vm.parent.name,
            'system':           summary.config.guestFullName,
            'cpu':              getVMCPU(summary),
            'memory':           getVMMemory(summary),
            'numNics':          summary.config.numEthernetCards,
            'storage':          getVMStorage(vm.guest.disk),
            'status':           summary.runtime.powerState,
            'bootTime':         str(summary.runtime.bootTime),
            'vmTools':          summary.guest.toolsStatus
        }


#------------- Get hypervisors
def get_host(host):
    """
    GET HOST INFORMATION
    """
    summary = host.summary

    hosts['Hypervisors']['hosts'].append(summary.config.name)

    hosts['_meta']['hostvars'][summary.config.name] = {
        'ansible_host':     getHostIpVMK0(host.config.network.vnic),
        'system':           summary.config.product.fullName,
        'memory':           getHostMemory(summary),
        'cpu':              getHostCPU(summary),
        'numNics':          summary.hardware.numNics,
        'status':           summary.runtime.powerState,
        'bootTime':         str(summary.runtime.bootTime),
        'vendor':           summary.hardware.vendor,
        'model':            summary.hardware.model
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
    with open(configFile) as opts_file:
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
        host_children = createVIew(service_instance, [vim.HostSystem])

        # Prepare threads
        host_thread = [None] * len(host_children)
        host_index = 0

        for child in host_children:
            host_thread[host_index] = getInfo("host", child)
            host_thread[host_index].start()
            host_index += 1

        # GET VMs
        vm_children = createVIew(service_instance, [vim.VirtualMachine])

        # Prepare threads
        vm_thread = [None] * len(vm_children)
        vm_index = 0

        for child in vm_children:
            vm_thread[vm_index] = getInfo("vm", child)
            vm_thread[vm_index].start()
            vm_index += 1

        # Wait for all threads to finish
        for t in host_thread:
            t.join()

        for v in vm_thread:
            v.join()

        # EXPORT JSON TO STANDARD OUTPUT
        print(json.dumps(hosts, sort_keys=True, indent=2))

        if benchmarkMode is True:
            print("Execution time: " + str(round(timer() - start, 3)) + "s")


# START PROGRAM
if __name__ == "__main__":
    main()
