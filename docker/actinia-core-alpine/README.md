# actinia alpine docker image

A related docker image created and available for download from here:

https://hub.docker.com/r/mundialis/actinia-core

First it creates a build image and a runtime image with packages and dependencies, from them the final image is created:

__Build with__:

```bash
$ docker build \
        --pull \
        --no-cache \
        --file docker/actinia-core-alpine/Dockerfile_build_pkgs \
        --tag actinia-core:alpine-build-pkgs .
$ docker tag actinia-core:alpine-build-pkgs mundialis/actinia-core:alpine-build-pkgs_v5
$ docker push mundialis/actinia-core:alpine-build-pkgs_v4

$ docker build \
        --pull \
        --no-cache \
        --file docker/actinia-core-alpine/Dockerfile_runtime_pkgs \
        --tag actinia-core:alpine-runtime-pkgs .
$ docker tag actinia-core:alpine-runtime-pkgs mundialis/actinia-core:alpine-runtime-pkgs_v5
$ docker push mundialis/actinia-core:alpine-runtime-pkgs_v4

$ docker build \
        --pull \
        --no-cache \
        --file docker/actinia-core-alpine/Dockerfile \
        --tag actinia-core:g78-stable-alpine .

```
