# Overview

Allow to deploy Kubernetes cluster in a VM Ware environment.

# Prerequisites

A computer running Docker environment.

# Help

Makefile targets:

```
$ make help
build-env                      Build the docker image with PYVCLOUD. Used to interact with VMWARE
create-vcloud-env              Create a full VMWare environment
deploy-kubernetes              Deploy Kubernetes
destroy-vcloud-env             Destroy VMWare environment
ls-vcloud-env                  List a full VMWare environment
reset-kubernetes               Reset Kubernetes
```



# VM environment setup

```
export VCLOUD_USERNAME=xxxx
export VCLOUD_PASSWORD=xxxx
export VCLOUD_HOST=xxxx
export VCLOUD_ORG=xxxx
```

* VCLOUD_USERNAME: Your username used to login to VCloud server
* VCLOUD_PASSWORD: Your password used to login to VCloud server
* VCLOUD_HOST: Host of the VCLOUD server
* VCLOUD_ORG: Name of the Organization that contains your user
* SSH_USERNAME: SSH Username used to execute shell commands on the newly created VMs 
* SSH_PASSWORD: SSH Password used to execute shell commands on the newly created VMs

## Docker images setup

```
$ make build-env
```


## VM Operations
### Create VMs
```
make create-vcloud-env 
```
### List VMs
```
make ls-vcloud-env 
```
### Delete VMS
```
make destroy-vcloud-env 
```

## Kubernetes Installation
