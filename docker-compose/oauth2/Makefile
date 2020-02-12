.PHONY: build push clean

build:
	docker build . -f Dockerfile -t azureusage/oauth2:latest

push:
	docker push azureusage/oauth2:latest

clean:
	docker image rm azureusage/oauth2:latest
