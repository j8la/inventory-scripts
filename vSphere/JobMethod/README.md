# vSphere Inventory (Job method)

This script is designed to work with jobs template instead the classic dynamic inventory scripts which reside in Tower database. It works with "tower-manage" to import a classical inventory file (see playbook).

Why ? Because i want to use GitHub repositories to manage the versioning of my inventory scripts (you can however update inventory scripts in Tower with the Tower Rest API) and doesn't want to depend of database if i must abandon Tower in the future (but not Ansible, of course). 

The method is to configure the GitHub connection at first in a project to keep the scripts up to date, configure the credentials with the necessary sudo command and then configure a job template using the playbook. Personaly i prefer this way instead the classical way. Maybe i'm wrong but this works well for me :)

The type of connection has changed in playbook with last update (09/06/2017) for working with Tower 3.1.3. Well, the problems with local playbooks execution has been finally resolved!

### How to use (standalone)
usage: vsphere-inventory.py [-h] -s SERVER -u USERNAME -p PASSWORD -i INVENTORYFILE 

Arguments:  
  + -h, --help  
  _show this help message and exit_

  + -s SERVER, --server SERVER  
  _FQDN of vSphere server_  

  + -u USERNAME, --username USERNAME  
  _vSphere username_

  + -p PASSWORD, --password PASSWORD  
  _vSphere password_  

  + -i INVENTORYFILE, --inventoryFile INVENTORYFILE  
  _Inventory file_  
 

### Ouput example

_[Linux]_  
_VM-REDHAT ansible_host=192.168.0.1 hypervisor=esx-001.my.lan folder='Developpement'_  
_VM-DEBIAN ansible_host=192.168.0.2 hypervisor=esx-002.my.lan folder='Infrastructure'_  

_[Windows]_  
_VM-W2008 ansible_host=192.168.0.3 hypervisor=esx-001.my.lan folder='Infrastructure'_  
_VM-W2012 ansible_host=192.168.0.4 hypervisor=esx-002.my.lan folder='Active Directory'_  

_[Other]_  
_NETAPP-SIM ansible_host=192.168.0.5_  

_[Hypervisors]_  
_esx-001.my.lan ansible_host=192.168.0.20 os='VMware ESXi' version='5.5.0' host='vim.HostSystem:host-10'_  
_esx-002.my.lan ansible_host=192.168.0.21 os='VMware ESXi' version='5.5.0' host='vim.HostSystem:host-11'_  

_[VirtualMachines:children]_  
_Windows_  
_Linux_  
_Other_    

_[vSphere:children]_  
_VirtualMachines_  
_Hypervisors_  


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