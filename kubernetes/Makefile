PYVCLOUD_IMAGE := pyvcloud:latest


.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

deploy-ansible: ## Deploy Ansible
	ansible-playbook -i host_gen.ini --ask-vault-pass --extra-vars '@passwd.yml' site.yaml 
