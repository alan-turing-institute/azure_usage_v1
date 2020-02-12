.PHONY: build push clean dbuild dpush dclean

build:
	docker build . -f Dockerfile -t azureusage/nginx:latest

push:
	docker push azureusage/nginx:latest

clean:
	docker image rm azureusage/nginx:latest

dbuild:
	docker build . -f Dockerfile -t azureusage/nginx:dev

dpush:
	docker push azureusage/nginx:dev

dclean:
	docker image rm azureusage/nginx:dev