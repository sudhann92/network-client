# ACL RULE ADDITION AND DELETION

This Playbook allows to interaction with Cisco and Hauwei switches to add the new rule to the ACL

## REQUIREMENTS

The cisco.ios required for this playbook to connect with switches and push the ACL rule configuration
The  community.general is used to send the mail to the consumer after the configuration pushed

```yaml
---
- name: Check and Apply ACL Rules on Multiple Switches
  hosts: "{{dynamic_group}}"
  gather_facts: false
  collections:
       - cisco.ios
       - community.general

```
## Installing this collection

You can install the cisco.ios collection with the Ansible Galaxy CLI:

```console
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install community.general
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---

    # If you need a specific version of the collection, you can specify like this:
    # version: ...
collections:
     - cisco.ios
     - community.general
```

## Using this collection

The cisco.ios collection must be invoked in the playbook in order for ansible to pick up the correct modules to use.
This modulde used to pushed the configuration to the cisco switches

The following command will invoke the playbook with the awx collection

```console
ansible-playbook  playbook/Acl_creation.yml --extra-vars "@variable.yaml"
```

## ROLES
created roles for this playbook
1) acl_rule_configuration

### Below is the  Extra variable input for ACL_creation playbook

```yaml
---
acl_name: 'xyz'
new_acl_rule: |
        "permit new rule 1
         permit new rule 2
         permit new rule 3"
dynamic_host: |
         "switch_1
          switch_2
          switch_3"
dynamic_group: "cisco_switch"
config_type: "acl_additon"
change_number: 'CHG000123'
```