TAG ?= cert-exporter

build:
	docker build -t $(TAG) .

push:
	docker push $(TAG)
