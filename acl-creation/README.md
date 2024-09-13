# ACL RULE ADDITION AND DELETION

This Playbook allows to interaction with AWX and Ansible Automation controller API for create the 
bulk host and Group creation in the inventory

## REQUIREMENTS

The AWX.AWX OR ANSIBLE.CONTROLLER collections MUST be installed in order for this collection to work. It is recommended they be invoked in the playbook in the following way.

```yaml
---

```
## Installing this collection

You can install the awx.awx collection with the Ansible Galaxy CLI:

```console
ansible-galaxy collection install awx.awx
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---

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

```

## Example

``` yaml
---

```
``` yaml
---


``` yaml
---

```                


### Below is the Extra variable input for Delete-host-group-AAP playbook

```yaml

```

## Example:

```yaml


```