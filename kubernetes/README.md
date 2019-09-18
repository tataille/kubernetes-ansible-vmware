# Kubernetes Installation using Ansible

```
$  pip install requests
$ ansible-playbook zwindler_vmware_add_vm_normal.yml --extra-vars "vsphere_host=$VCLOUD_HOST vsphere_user=$VCLOUD_USERNAME vsphere_password=$VCLOUD_PASSWORD vsphere_datastore="
````

## Kubenetes installation

Inspired by https://github.com/kairen/kubeadm-ansible

System requirements:

* Deployment environment must have Ansible 2.4.0+
* Master and nodes must have passwordless SSH access

### configure passwordless on master/slave nodes

```
$ ls -al ~/.ssh/id_*.pub
$ ssh-keygen -t rsa -b 4096 -C "your_email@domain.com"
$ ssh-copy-id remote_username@server_ip_address
```

### Security

To store sudo password (used on master and slave), we use sudo passwed in a vault. Inventory file must be updated as follow

```
[all:vars]
ansible_connection=ssh
ansible_user=genesys
ansible_become=yes  # use sudo 
ansible_become_method=sudo 
ansible_become_pass='{{ my_cluser_sudo_pass }}'
```
Then we need to create a password file `passwd.yml`using

```
$ ansible-vault create passwd.yml
```

Then start the cookbook

```
$ ansible-playbook -i hosts.ini --ask-vault-pass --extra-vars '@passwd.yml' site.yaml 
ansible-playbook -i ../host_gen.ini --ask-vault-pass --extra-vars '@passwd.yml' site.yaml 
```

### Kubernetes nodes list

```
$ kubectl get nodes -o wide
NAME           STATUS   ROLES    AGE    VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE                KERNEL-VERSION              CONTAINER-RUNTIME
bstaillantm    Ready    master   128m   v1.14.0   135.39.46.103   <none>        CentOS Linux 7 (Core)   3.10.0-693.5.2.el7.x86_64   docker://17.3.1
bstaillants    Ready    <none>   127m   v1.14.0   135.39.46.134   <none>        CentOS Linux 7 (Core)   3.10.0-693.5.2.el7.x86_64   docker://17.3.1
bstaillants2   Ready    <none>   127m   v1.14.0   135.39.46.137   <none>        CentOS Linux 7 (Core)   3.10.0-693.5.2.el7.x86_64   docker://17.3.1
```

### Expose a dashboard

maybe disabling firewall
```
kubectl expose deployment kubernetes-dashboard --namespace=kube-system --type NodePort
kubectl proxy
```
see https://stackoverflow.com/questions/53957413/how-to-access-kubernetes-dashboard-from-outside-network to create a user for dashboard.