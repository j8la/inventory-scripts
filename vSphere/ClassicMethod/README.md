# vSphere Inventory (Classic method)

This dynamic inventory script for Ansible Tower uses pyVmomi to get the hypervisors and the virtual machines. It has been tested with vSphere 5.5 to 6.5, Ansible Tower 3.1.3 to 3.2.2, Python 2.7.6/2.7.9/3.x.

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

You can change the path and the name of the credential file at the line #35 :
```
configFile = '/etc/ansible/vsphere-inventory.json'
```

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
        "bootTime": "2017-12-22 10:13:04.796560+00:00",
        "cpu": {
          "numCpu": 2,
          "totalMhz": 5198,
          "usedMhz": 25,
          "usedPer": 0.48
        },
        "folder": "Infrastructure",
        "hostname": "vm1.mydomain.lan",
        "memory": {
          "guest": 983,
          "size": 8192,
          "usedPer": 12.0
        },
        "numNics": 1,
        "status": "poweredOn",
        "storage": [
          {
            "free": 179.54,
            "path": "/",
            "size": 181.98,
            "used": 2.44,
            "usedPer": 1.35
          },
          {
            "free": 0.81,
            "path": "/boot",
            "size": 1.0,
            "used": 0.19,
            "usedPer": 19.0
          },
          {
            "free": 19.96,
            "path": "/home",
            "size": 20.0,
            "used": 0.04,
            "usedPer": 0.2
          },
          {
            "free": 179.54,
            "path": "/tmp",
            "size": 181.98,
            "used": 2.44,
            "usedPer": 1.35
          },
          {
            "free": 179.54,
            "path": "/var/tmp",
            "size": 181.98,
            "used": 2.44,
            "usedPer": 1.35
          }
        ],
        "system": "CentOS 7 (64-bit)",
        "vmTools": "toolsOk"
      },
      "vmhost1.mydomain.lan": {
        "ansible_host": "192.168.0.11",
        "bootTime": "2017-12-04 11:09:50.512999+00:00",
        "cpu": {
          "cores": 32,
          "model": "Intel(R) Xeon(R) CPU E5-2697A v4 @ 2.60GHz",
          "sockets": 2,
          "threads": 64,
          "totalMhz": 83168,
          "usedMhz": 6013,
          "usedPer": 7.23
        },
        "memory": {
          "size": 262033,
          "used": 40740,
          "usedPer": 15.55
        },
        "model": "SSG-6028R-E1CR12T",
        "numNics": 4,
        "status": "poweredOn",
        "system": "VMware ESXi 6.5.0 build-6765664",
        "vendor": "Supermicro"
      },
      "vmhost2.mydomain.lan": {
        "ansible_host": "192.168.0.12",
        "bootTime": "2017-12-04 11:33:26.111000+00:00",
        "cpu": {
          "cores": 32,
          "model": "Intel(R) Xeon(R) CPU E5-2697A v4 @ 2.60GHz",
          "sockets": 2,
          "threads": 64,
          "totalMhz": 83168,
          "usedMhz": 6026,
          "usedPer": 7.25
        },
        "memory": {
          "size": 262033,
          "used": 53212,
          "usedPer": 20.31
        },
        "model": "SSG-6028R-E1CR12T",
        "numNics": 4,
        "status": "poweredOn",
        "system": "VMware ESXi 6.5.0 build-6765664",
        "vendor": "Supermicro"
      },
      "VM2": {
        "ansible_host": "192.168.0.2",
        "bootTime": "2017-12-04 12:54:51.627908+00:00",
        "cpu": {
          "numCpu": 2,
          "totalMhz": 5198,
          "usedMhz": 0,
          "usedPer": 0.0
        },
        "folder": "Infrastructure",
        "hostname": "vm2.mydomain.lan",
        "memory": {
          "guest": 983,
          "size": 8192,
          "usedPer": 12.0
        },
        "numNics": 1,
        "status": "poweredOn",
        "storage": [
          {
            "free": 72.55,
            "path": "C:\\",
            "size": 109.51,
            "used": 36.96,
            "usedPer": 33.76
          }
        ],
        "system": "Microsoft Windows Server 2016 (64-bit)",
        "vmTools": "toolsOk"
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