PYVCLOUD_IMAGE := pyvcloud:latest
KUBERNETES_DIR=ansible


.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build-env: ## Build the docker image with PYVCLOUD. Used to interact with VMWARE
	docker build -t $(PYVCLOUD_IMAGE) . -f Dockerfile

create-vcloud-env: ## Create a full VMWare environment
	docker run --rm -it -v $(CURDIR)/vmware/sdk:/src -v $(HOME)/.ssh:/root/.ssh -w /src  -e SSH_USERNAME=${SSH_USERNAME} -e SSH_PASSWORD=${SSH_PASSWORD} -e VCLOUD_USERNAME=${VCLOUD_USERNAME} -e VCLOUD_PASSWORD="${VCLOUD_PASSWORD}" -e VCLOUD_HOST=${VCLOUD_HOST} -e VCLOUD_ORG=${VCLOUD_ORG} -e VCLOUD_VDC_NAME="${VCLOUD_VDC_NAME}" $(PYVCLOUD_IMAGE)	 python tenant-onboard.py  tenant.yaml

destroy-vcloud-env: ## Destroy VMWare environment
	docker run --rm -it -v $(CURDIR)/vmware/sdk:/src -w /src -e VCLOUD_USERNAME=${VCLOUD_USERNAME} -e VCLOUD_PASSWORD=${VCLOUD_PASSWORD} -e VCLOUD_HOST=${VCLOUD_HOST} -e VCLOUD_ORG=${VCLOUD_ORG} -e VCLOUD_VDC_NAME="${VCLOUD_VDC_NAME}" $(PYVCLOUD_IMAGE) python tenant-destroy.py  tenant.yaml

ls-vcloud-env: ## List a full VMWare environment
	docker run --rm -it -v $(CURDIR)/vmware/sdk:/src -w /src -e VCLOUD_USERNAME=${VCLOUD_USERNAME} -e VCLOUD_PASSWORD=${VCLOUD_PASSWORD} -e VCLOUD_HOST=${VCLOUD_HOST} -e VCLOUD_ORG=${VCLOUD_ORG} -e VCLOUD_VDC_NAME="${VCLOUD_VDC_NAME}" $(PYVCLOUD_IMAGE) python tenant-ls.py  tenant.yaml

deploy-kubernetes: ## Deploy Kubernetes
	docker run --rm -it -v $(CURDIR):/src:rw -w /src -e VCLOUD_USERNAME=${VCLOUD_USERNAME} -e SSH_USERNAME=${SSH_USERNAME} -e VCLOUD_PASSWORD=${VCLOUD_PASSWORD} -e VCLOUD_HOST=${VCLOUD_HOST} -e VCLOUD_ORG=${VCLOUD_ORG} -e VCLOUD_VDC_NAME="${VCLOUD_VDC_NAME}" $(PYVCLOUD_IMAGE) python ansible/deploy-ansible.py  vmware/sdk/tenant.yaml
	@(cd $(KUBERNETES_DIR) && $(MAKE) $@)

reset-kubernetes: ## Reset Kubernetes
	@(cd $(KUBERNETES_DIR) && $(MAKE) $@)

