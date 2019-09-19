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
deploy-K8s2                    Deploy Kubernetes
destroy-vcloud-env             Destroy VMWare environment
ls-vcloud-env                  List a full VMWare environment
reset-K8s2                     Reset Kubernetes
```



# VM environment setup

```
export VCLOUD_USERNAME=xxxx
export VCLOUD_PASSWORD=xxxx
export VCLOUD_HOST=xxxx
export VCLOUD_ORG=xxxx
export SSH_USERNAME=xxx
export SSH_PASSWORD=xxx
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
VMs list is defined in file [vmware/sdk/tenant.yaml](vmware/sdk/tenant.yaml)
```
$ make create-vcloud-env 
```
### List VMs
This command displays details about created VMs 
```
$ make ls-vcloud-env 
```
### Delete VMS
This command delete created VMs 
```
$ make destroy-vcloud-env 
```

## Kubernetes Installation

This commands use Ansible to deploy Kubernetes cluster on the created VMs

```
$ make deploy-K8s2 
```

This commands use Ansible to reset Kubernetes cluster on the created VMs
```
$ make reset-K8s2
```

### Kubernetes Dashboard

### Kubernetes Dashboard


![Kubernetes Dashboard ](ansible/img/kubernetes_dashboard.png)


Kubernetes Dashboard details can be retrieved from Ansible logs:

```
TASK [kubernetes/master : show dashboard instructions] *************************************************************************************************************************************************************************************************************
ok: [135.39.47.179] => {
    "msg": "Dashboard is available at https://135.39.47.179:32497"
}

TASK [kubernetes/master : show dashboard token] ********************************************************************************************************************************************************************************************************************
ok: [135.39.47.179] => {
    "msg": "The dashboard login token is: eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImdlbmVzeXNhZG1pbi10b2tlbi02dGM3cCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJnZW5lc3lzYWRtaW4iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI4NGM4NDRhMS1kYWQxLTExZTktYjE4OS0wMDUwNTYwMTBmMDYiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpnZW5lc3lzYWRtaW4ifQ.29zMMmVnt-XPEkjxO-yFZbELUkvJzqWimWeOlH2DY_v0Sz2H1CkMniyeNyLmcCbJghn36opuyhXae1FWnP0SmUXXxxAL68nSfOJMA2tcj3x4R3ffkQ_Jhm3usim-ldPQTJZhFisutEuZzh2KOQlVwzG38mfiu5Uns_eZTnD50Q9acJmflBOGg2KihYt9ZOVrfzbU27jy1tCW_h-v9F8ZEszxIdONy3fgCdH1aAATaCFdh52K1bRVilbBV6RPPlSQnM-2DrcXiExIYzHZiSRByusMMJ-DQQzD9Z6ce3Z0AFkhB3CMLYWgdkDDetXh7BtUH6-b7PXLD7QW-mxVl9yiBw"
}
```