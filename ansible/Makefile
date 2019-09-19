PYVCLOUD_IMAGE := pyvcloud:latest


.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

deploy-kubernetes: ## Deploy Kubernetes
		docker run --rm -it -v $(CURDIR):/ansible/playbooks\
		ansible:latest  site.yaml  -i host.ini --ask-vault-pass --extra-vars '@passwd.yml'
	#ansible-playbook -i host.ini --ask-vault-pass --extra-vars '@passwd.yml' site.yaml 

reset-kubernetes: ## Reset Kubernetes
	ansible-playbook -i host.ini --ask-vault-pass --extra-vars '@passwd.yml' reset-site.yaml
