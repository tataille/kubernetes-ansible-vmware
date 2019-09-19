# Kubernetes Installation using Ansible

```
$  pip install requests
$ ansible-playbook zwindler_vmware_add_vm_normal.yml --extra-vars "vsphere_host=$VCLOUD_HOST vsphere_user=$VCLOUD_USERNAME vsphere_password=$VCLOUD_PASSWORD vsphere_datastore="
````

## Kubenetes installation

Inspired by https://github.com/kairen/kubeadm-ansible

System requirements:

* Deployment environment must have Ansible 2.4.0+

### Security

The host.ini file is generated automatically before deploying Kubernetes. It contains the following:

```
[all:vars]
ansible_connection = ssh
ansible_user = # see SSH_USERNAME env variable
ansible_ssh_private_key_file = ~/.ssh/id_ansible_rsa
ansible_become_pass = # see SSH_PASSWORD env variable
ansible_ssh_user = # see SSH_USERNAME env variable
```

### Kubernetes nodes list

```
$ kubectl get nodes -o wide
NAME                            STATUS   ROLES    AGE   VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE                KERNEL-VERSION               CONTAINER-RUNTIME
bs<VCLOUD_USERNAME>masterhost   Ready    master   69s   v1.14.0   135.39.47.179   <none>        CentOS Linux 7 (Core)   3.10.0-957.27.2.el7.x86_64   docker://19.3.2
bs<VCLOUD_USERNAME>slavehost    Ready    <none>   46s   v1.14.0   135.39.47.178   <none>        CentOS Linux 7 (Core)   3.10.0-957.27.2.el7.x86_64   docker://19.3.1
bs<VCLOUD_USERNAME>slavehost2   Ready    <none>   46s   v1.14.0   135.39.47.177   <none>        CentOS Linux 7 (Core)   3.10.0-957.27.2.el7.x86_64   docker://19.3.1
```

### Kubernetes Dashboard


![Kubernetes Dashboard ](img/kubernetes_dashboard.png)

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

The token is stored in file `ansible/dashboard_token` and must be used to login in Admin page.
