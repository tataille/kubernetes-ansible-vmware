PYVCLOUD_IMAGE := pyvcloud:latest


.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

deploy-K8s2: ## Deploy Kubernetes
		docker run --rm -it -v $(HOME)/.ssh:/root/.ssh -v $(CURDIR):/ansible/playbooks\
		ansible:latest  site.yaml  -i host.ini 

reset-K8s2: ## Reset Kubernetes
	docker run --rm -it -v $(HOME)/.ssh:/root/.ssh -v $(CURDIR):/ansible/playbooks\
		ansible:latest  reset-site.yaml  -i host.ini
