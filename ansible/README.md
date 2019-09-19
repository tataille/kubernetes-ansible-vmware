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

The host.ini file is generated automatically. It contains the following:

```
[all:vars]
ansible_connection = ssh
ansible_user = genesys
ansible_ssh_private_key_file = ~/.ssh/id_ansible_rsa
ansible_become_pass = # see SSH_PASSWORD env variable
ansible_ssh_user = # see SSH_USERNAME env variable
```

T

```
$ ansible-playbook -i hosts.ini site.yaml 
ansible-playbook -i host.ini site.yaml 
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
 sudo systemctl status firewalld
```
kubectl delete service kubernetes-dashboard --namespace=kubernetes-dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.10.1/src/deploy/recommended/kubernetes-dashboard.yaml
kubectl patch service kubernetes-dashboard --namespace=kube-system  -p '{"spec": {"type": "NodePort"}}'
kubectl get service --all-namespaces -o wide


kubectl expose service kubernetes-dashboard --namespace=kube-system --type NodePort
kubectl proxy
```
see https://stackoverflow.com/questions/53957413/how-to-access-kubernetes-dashboard-from-outside-network to create a user for dashboard.