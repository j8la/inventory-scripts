#!/usr/bin/env python
# pylint: disable=I0011,C0103

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

import atexit
import argparse
import re

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


#------------- System Lists
vm_tmp = []
vm_win = []
vm_lin = []
vm_oth = []
esxi = []


#------------- Regex compile
hypervisor = re.compile(r'^(.*?)(?=[ ])')


#------------- Get Host infos
def get_host(host):
    """
    GET HOST INFORMATION
    """
    extvars = ''

    if host.summary.managementServerIp is not None:
        extvars += ' ansible_host=' + str(host.summary.managementServerIp)

    if host.summary.config.product.name is not None:
        extvars += " os='" + host.summary.config.product.name + "'"

    if host.summary.config.product.version is not None:
        extvars += " version='" + host.summary.config.product.version + "'"

    if host.summary.host is not None:
        extvars += " host=" + str(host.summary.host)

    esxi.append(host.summary.config.name + extvars)


#------------- Get VM infos
def get_vm(virtual_machine):
    """
    GET VM INFORMATION
    """
    summary = virtual_machine.summary

    extvars = ''

    if summary.guest is not None:
        if summary.guest.ipAddress is not None:
            extvars += ' ansible_host=' + str(summary.guest.ipAddress)

    for host in esxi:
        if str(summary.runtime.host) in host:
            extvars += ' hypervisor=' + hypervisor.search(host).group(1)

    extvars += " folder='" + virtual_machine.parent.name + "'"

    if summary.config.template != True:

        if "Linux" in summary.config.guestFullName:
            vm_lin.append(summary.config.name + extvars)

        if "Windows" in summary.config.guestFullName:
            vm_win.append(summary.config.name + extvars)

        if "Linux" not in summary.config.guestFullName and \
           "Windows" not in summary.config.guestFullName:
            vm_oth.append(summary.config.name + extvars)

    else:
        vm_tmp.append(summary.config.name)


def createVIew(instance, obj):
    """
    CREATE VIEW FROM VCENTER
    """
    content = instance.RetrieveContent()
    container = content.rootFolder      # Starting point to look into
    viewtype = obj                      # Object types to look for
    recursive = True                    # Whether we should look into it recursively
    containerview = content.viewManager.CreateContainerView(container, viewtype, recursive)

    return containerview.view


def section(group, members):
    """
    CREATE INI GROUP WITH MEMBERS
    """
    export = '[' + group + ']\n'

    for item in members:
        export += item + '\n'

    export += '\n'

    return export


def main():
    """
    MAIN
    """
    try:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE

        service_instance = connect.SmartConnect(host=server_fqdn,
                                                user=server_username,
                                                pwd=server_password,
                                                port=int(443),
                                                sslContext=context)

        atexit.register(connect.Disconnect, service_instance)

        # HOSTS
        children = createVIew(service_instance, [vim.HostSystem])

        for child in children:
            get_host(child)

        # VMs
        children = createVIew(service_instance, [vim.VirtualMachine])

        for child in children:
            get_vm(child)

        # Create Inventory File
        f = open(inventory_file, 'w')

        f.write(section('Linux', vm_lin))
        f.write(section('Windows', vm_win))
        f.write(section('Other', vm_oth))
        f.write(section('Hypervisors', esxi))

        f.write("[VirtualMachines:children]\n"
                "Windows\n"
                "Linux\n"
                "Other\n"
                "Templates\n\n"
                "[vSphere:children]\n"
                "VirtualMachines\n"
                "Hypervisors\n")

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0


#------------- Start program
if __name__ == "__main__":

    folder = 'root'

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server', help='FQDN of vSphere server', \
                                          action='store', \
                                          required='True')

    parser.add_argument('-u', '--username', help='vSphere username', \
                                            action='store', \
                                            required='True')

    parser.add_argument('-p', '--password', help='vSphere password', \
                                            action='store', \
                                            required='True')

    parser.add_argument('-i', '--inventoryFile', help='Inventory file', \
                                                 action='store', \
                                                 required='True')

    args = parser.parse_args()

    if args.server:
        server_fqdn = args.server

    if args.username:
        server_username = args.username

    if args.password:
        server_password = args.password

    if args.inventoryFile:
        inventory_file = args.inventoryFile

    if (server_fqdn, server_username, server_password, inventory_file) is not None:
        main()

    else:
        parser.print_help()
