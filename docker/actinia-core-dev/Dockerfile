FROM mundialis/actinia-core:g79-latest-alpine

COPY actinia.cfg /etc/default/actinia

RUN pip3 uninstall actinia-core -y

# for actinia plugin development
# RUN pip3 uninstall actinia-metadata-plugin.wsgi -y
# RUN pip3 uninstall actinia-module-plugin.wsgi -y
# WORKDIR /src/actinia-module-plugin
