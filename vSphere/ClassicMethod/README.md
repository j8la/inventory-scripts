# vSphere Inventory (Classic method)

This dynamic inventory script for Ansible Tower uses pyVmomi to get the hypervisors and the virtual machines. It has been tested with vSphere 5.5, Ansible Tower 3.1.3, Python 2.7.6/2.7.9/3.x.

### Prerequisites
You have to install the following with pip on the Ansible Tower host :
```
pip install pyvmomi
```

### How to
At first, copy the *vsphere-inventory.json* file in */etc/ansible* on the Ansible Tower host. Then edit it :
```json
{
    "vcenter":"vcenter.my.domain",       
    "user":"myaccount",
    "password":"mypassword",
    "ssl_verify":false
}
```
- vcenter : The vCenter server
- user : vCenter user
- password : vCenter password
- ssl_verify : If you don't use a self-signed certificate, change it to true

Secondly, copy the *vsphere-inventory.py* file contents, add a new custom inventory in Tower (SETTINGS / INVENTORY SCRIPTS) and paste them.

Lastly, in INVENTORIES, add a new inventory, add a group and select de custom inventory script.

### Ouput example
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
      "VM2"
    ]
  },
  "_meta": {
    "hostvars": {
      "VM1": {
        "ansible_host": "192.168.0.1",
        "bootTime": "2017-05-31 15:52:42.850803+00:00",
        "folder": "Infrastructure",
        "memory": 3072,
        "numCpu": 2,
        "numNics": 1,
        "status": "poweredOn",
        "storage": 128.11,
        "system": "SUSE Linux Enterprise 11 (64-bit)"
      },
      "vmhost1.mydomain.lan": {
        "ansible_host": "192.168.0.11",
        "bootTime": "2017-05-31 15:48:16.240673+00:00",
        "memory": 16268,
        "numCores": 4,
        "numCpu": 1,
        "numNics": 4,
        "numThreads": 4,
        "status": "poweredOn",
        "system": "VMware ESXi 5.5.0 build-1623387"
      },
      "vmhost2.mydomain.lan": {
        "ansible_host": "None",
        "bootTime": "2016-10-03 14:00:20.323000+00:00",
        "memory": 8091,
        "numCores": 2,
        "numCpu": 1,
        "numNics": 1,
        "numThreads": 2,
        "status": "unknown",
        "system": "VMware ESXi 5.1.0 build-799733"
      },
      "VM2": {
        "ansible_host": "192.168.0.2",
        "bootTime": "2016-10-03 14:02:01.131000+00:00",
        "folder": "Infrastructure",
        "memory": 256,
        "numCpu": 1,
        "numNics": 1,
        "status": "poweredOn",
        "storage": 783.09,
        "system": "Microsoft Windows Server 2003 Standard (32-bit)"
      }
    }
  }
}
```

### License
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