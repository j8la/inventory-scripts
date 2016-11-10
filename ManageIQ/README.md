# ManageIQ Inventory

This dynamic inventory script for Ansible Tower uses ManageIQ API to get the hypervisors and the virtual machines. It has been tested with the ManageIQ 4.1 appliance and Ansible Tower 3.0.3 on CentOS 7.  

### Prerequisites
You have to install the following with pip on the Ansible Tower host if you don't use Python 3.x :
```
pip install requests
```

### How to
At first, copy the *manageiq-inventory.json* file in */etc/ansible* on the Ansible Tower host. Then edit it :
```json
{
    "server":"",       
    "user":"admin",
    "password":"",
    "ssl_verify":false,
    "vm_filter":[]
}
```
- server : The ManageIQ server
- user : ManageIQ user
- password : ManageIQ password
- ssl_verify : If you don't use a self-signed certificate, change it to true
- vm_filter : If you want to exclude specific virtual machines from inventory (for an example, ManageIQ, vCenter, Tower...), insert them in this array

Secondly, copy the *manageiq-inventory.py* file contents, add a new custom inventory in Tower (SETTINGS / INVENTORY SCRIPTS) and paste them.

Lastly, in INVENTORIES, add a new inventory, add a group and select de custom inventory script.  

### Output

The output of the script is :
```json
{
  "Hypervisors": {
    "hosts": [
      "vmhost1.mydomain.lan",
      "vmhost2.mydomain.lan"
    ]
  },
  "VirtualMachines": {
    "hosts": [
      "VM1",
      "VM2",
      "VM3",
      "VM4"
    ]
  },
  "_meta": {
    "hostvars": {
      "VM1": {
        "ansible_host": "192.168.0.1",
        "boot_time": "2016-11-03T13:59:34Z",
        "cloud": false,
        "connection_state": "connected",
        "created_on": "2016-11-03T13:59:52Z",
        "host_id": 2,
        "id": 11,
        "power_state": "on",
        "updated_on": "2016-11-03T17:27:18Z",
        "vendor": "vmware"
      },
      "VM2": {
        "ansible_host": "192.168.0.2",
        "boot_time": "2016-11-03T17:25:55Z",
        "cloud": false,
        "connection_state": "connected",
        "created_on": "2016-10-29T00:19:56Z",
        "host_id": 2,
        "id": 6,
        "power_state": "on",
        "updated_on": "2016-11-03T17:27:18Z",
        "vendor": "vmware"
      },
      "VM3": {
        "ansible_host": "192.168.0.3",
        "boot_time": "2016-09-01T20:30:57Z",
        "cloud": false,
        "connection_state": "connected",
        "created_on": "2016-10-29T00:19:56Z",
        "host_id": 2,
        "id": 8,
        "power_state": "on",
        "updated_on": "2016-10-29T00:19:56Z",
        "vendor": "vmware"
      },
      "VM4": {
        "ansible_host": "192.168.0.4",
        "boot_time": "2016-10-03T14:01:37Z",
        "cloud": false,
        "connection_state": "connected",
        "created_on": "2016-10-29T00:19:56Z",
        "host_id": 1,
        "id": 7,
        "power_state": "on",
        "updated_on": "2016-11-04T17:28:19Z",
        "vendor": "vmware"
      },
      "vmhost1.mydomain.lan": {
        "buildnumber": "1623387",
        "id": 2,
        "ansible_host": "192.168.0.11",
        "product": "ESXi",
        "vendor": "vmware",
        "version": "5.5.0"
      },
      "vmhost2.mydomain.lan": {
        "buildnumber": "1623387",
        "id": 1,
        "ansible_host": "192.168.0.12",
        "product": "ESXi",
        "vendor": "vmware",
        "version": "5.5.0"
      }
    }
  }
}
```

=====

Ansible, Ansible Tower & RedHat are trademarks of Red Hat, Inc.

Copyright (C) 2016 - Julien Blanc

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


