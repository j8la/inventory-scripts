#!/usr/bin/env python

# Copyright (C) 2016 - Julien Blanc

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import argparse
import requests
import json
import warnings


#--------------------------------------------------- IGNORE WARNINGS TO CLEAN OUTPUT
warnings.filterwarnings("ignore")


#--------------------------------------------------- INVENTORY MODEL
hosts = { 
    'Hypervisors': {}, 
    'VirtualMachines': {} 
}

hosts['Hypervisors']['hosts'] = []
hosts['VirtualMachines']['hosts'] = []

hosts['_meta'] = { 
    'hostvars': {}
}


#--------------------------------------------------- VARS 
error_count = 0


#--------------------------------------------------- GET CONNEXION PARAMETERS
with open('/etc/ansible/manageiq-inventory.json') as opts_file:    
    opts = json.load(opts_file)

server      = opts["server"]
user        = opts["user"]
password    = opts["password"]
ssl_verify  = opts["ssl_verify"]


#--------------------------------------------------- API REQUEST FUNCTION
def req(server,url,user,password,ssl_verify) :
    try:
        r = requests.get("https://" + server + url, auth=(user,password), verify=ssl_verify)

        if r.status_code == 200 :
            hList = json.loads(r.text)
            return hList
        else:
            print(">>> (status_code:" + str(r.status_code) + ") Can't get " + url)
            return -1

    except :
        print(">>> Can't connect to " + server)
        return -1


#--------------------------------------------------- CHECK MANAGEIQ CONNECTION
try:
    requests.get("https://" + server + "/api", auth=(user,password), verify=ssl_verify)
except :
    print(">>> Can't connect to " + server)
    error_count += 1


#--------------------------------------------------- GET HOSTS
if error_count == 0 :

    hList = req(server,"/api/hosts?expand=resources&attributes=id,hostname,ipaddress,vmm_vendor,vmm_version,vmm_product,vmm_buildnumber",user,password,ssl_verify)

    if hList != -1 :
        for h in hList["resources"] :
            hosts['Hypervisors']['hosts'].append(h["hostname"])

            hosts['_meta']['hostvars'][h["hostname"]] = {
                'id': h["id"],
                'ansible_host': h["ipaddress"],
                'vendor':       h["vmm_vendor"],
                'version':      h["vmm_version"],
                'product':      h["vmm_product"],
                'buildnumber':  h["vmm_buildnumber"]
            }

    else :
        error_count += 1


#--------------------------------------------------- GET VMs
if error_count == 0 :

    hList = req(server,"/api/vms?expand=resources&attributes=name,id,ipaddresses,vendor,cloud,host_id,created_on,updated_on,boot_time,connection_state,power_state",user,password,ssl_verify)

    if hList != -1 :
        for h in hList["resources"] :
            hosts['VirtualMachines']['hosts'].append(h["name"])

            hosts['_meta']['hostvars'][h["name"]] = {
                'id':               h["id"],
                'ansible_host':     h["ipaddresses"][0],
                'vendor':           h["vendor"],
                'cloud':            h["cloud"],
                'host_id':          h["host_id"],
                'created_on':       h["created_on"],
                'updated_on':       h["updated_on"],
                'boot_time':        h["boot_time"],
                'connection_state': h["connection_state"],
                'power_state':      h["power_state"]
            }

    else :
        error_count += 1


#--------------------------------------------------- PRINTS INVENTORY
if error_count != 0 :
    print(">>> Inventory failed!")
else :
    print(json.dumps(hosts, sort_keys=True, indent=2))
