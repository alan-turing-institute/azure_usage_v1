.PHONY: build push run clean dbuild drun dpush dclean

build:
	docker build . -f Dockerfile -t azureusage/azure_usage:latest

run:
	docker run -p 5006:5006 azureusage/azure_usage:latest

push:
	docker push azureusage/azure_usage:latest

clean:
	docker image rm azureusage/azure_usage:latest

dbuild:
	docker build . -f Dockerfile -t azureusage/azure_usage:dev

drun:
	docker run -p 5006:5006 azureusage/azure_usage:dev

dpush:
	docker push azureusage/azure_usage:dev

dclean:
	docker image rm azureusage/azure_usage:dev
