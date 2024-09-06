# Controller Configuration Bulk Host and Group Addition

This Playbook allows to interaction with AWX and Ansible Automation controller API for create the 
bulk host and Group creation in the inventory

## REQUIREMENTS

The AWX.AWX OR ANSIBLE.CONTROLLER collections MUST be installed in order for this collection to work. It is recommended they be invoked in the playbook in the following way.

```yaml
---
- name: Playbook to configure ansible controller post installation
  hosts: localhost
  connection: local
  vars:
    controller_validate_certs: false
  collections:
    - awx.awx
```
## Installing this collection

You can install the awx.awx collection with the Ansible Galaxy CLI:

```console
ansible-galaxy collection install awx.awx
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: awx.awx
    # If you need a specific version of the collection, you can specify like this:
    # version: ...
```


## Using this collection

The awx.awx collection must be invoked in the playbook in order for ansible to pick up the correct modules to use.

The following command will invoke the playbook with the awx collection

```console
ansible-playbook  Bulk-host-group/playbook/create-host-group-AAP.yml --extra-vars "@variable.yaml"
```

Otherwise it will look for the modules only in your base installation. If there are errors complaining about "couldn't resolve module/action" this is the most likely cause.

Define following vars inside in the group_vars/all/vars.yml file
```yaml
---
controller_validate_certs: false
controller_username: "<user name to login to the Ansible automation platform>"
#ansible-vault encrypt_string "<password string to encrypt" --name '<string name of the variable>'
controller_password: <Encrypted password>
controller_hostname: "<Ansible automation platform hostname>"
```
You can also specify authentication by a combination of either:

- `controller_hostname`, `controller_username`, `controller_password`
- `controller_hostname`, `controller_oauthtoken`

## ROLES
created four roles for this playbook
1) bulk-host-creation
2) group-creation
3) Host-deletion 
4) Group-deletion

### Below is the  Extra variable input for Create-host-group-AAP playbook 

```yaml
---
controller_inventory_name: "<Name of the inventory>"
controller_host_device_name: "xxxx,yyy,zzzz <name of the devices>"
controller_groups_name:
    - group_name: "<group name>"
      preserve_existing_hosts: "<By default this value is 'false' if you would like to preserve the existing hosts for this group then change as "True" >
      hosts: "aaaa,bbb,cccc,ddddd,xxxx,yyyy,zzzz <name of the devices>"

```

## Example

``` yaml
---
controller_inventory_name: "Demo_Inventory"
controller_host_device_name: "switch_name_1,switch_name_2,switch_name_3,switch_name_4"
controller_groups_name:
              - group_name: "agv_access"
                hosts: "switch_name_1,switch_name_2"
              - group_name: "refer_av"
                hosts: "switch_name_3,switch_name_4"
```
``` yaml
---
controller_inventory_name: "Demo_Inventory"
controller_host_device_name: "switch_name_1,switch_name_2"
controller_groups_name: []
```

``` yaml
---
controller_inventory_name: "Demo_Inventory"
controller_host_device_name: "switch_name_1,switch_name_2"
controller_groups_name:
              - group_name: "agv_access"
                hosts: "switch_name_1,switch_name_2"
```                


### Below is the Extra variable input for Delete-host-group-AAP playbook

```yaml
controller_inventory_name: "<Name of the inventory>"
controller_host_device_name: "<Name of the device>"
controller_groups_name: "<Name of the group>"
```

## Example:

```yaml

controller_inventory_name: "Tuas inventory"
controller_host_device_name: "switch_name_1,switch_name_2,switch_name_3"
controller_groups_name: "group_name_1,group_name_2"
controller_state: "absent"

```